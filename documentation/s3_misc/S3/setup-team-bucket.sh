#!/bin/bash
# setup-team-bucket.sh
# Creates an S3 bucket for a specific team with team-specific prefix permissions
# Usage: ./setup-team-bucket.sh <bucket-name> <team-name> <region> [role-name]

set -e

# Configuration
BUCKET_NAME="${1}"
TEAM_NAME="${2}"
REGION="${3:-us-east-1}"
ROLE_NAME="${4:-EC2-S3-Role}"

if [ -z "$BUCKET_NAME" ] || [ -z "$TEAM_NAME" ]; then
    echo "Usage: ./setup-team-bucket.sh <bucket-name> <team-name> <region> [role-name]"
    echo "Example: ./setup-team-bucket.sh cse255-data team01 us-east-1 EC2-S3-Role"
    exit 1
fi

# Get account ID and role ARN
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}"

echo "Setting up S3 bucket for team: $TEAM_NAME"
echo "Bucket: $BUCKET_NAME"
echo "Region: $REGION"
echo "Role ARN: $ROLE_ARN"

# Step 1: Create bucket if it doesn't exist
echo "Checking if bucket exists..."
if ! aws s3 ls "s3://$BUCKET_NAME" &>/dev/null; then
    echo "Creating bucket..."
    if [ "$REGION" = "us-east-1" ]; then
        aws s3 mb s3://$BUCKET_NAME
    else
        aws s3 mb s3://$BUCKET_NAME --region $REGION
    fi
else
    echo "Bucket already exists"
fi

# Step 2: Configure Block Public Access
echo "Configuring Block Public Access..."
aws s3api put-public-access-block \
    --bucket $BUCKET_NAME \
    --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

# Step 3: Get existing bucket policy (if any)
echo "Updating bucket policy..."
EXISTING_POLICY=$(aws s3api get-bucket-policy --bucket $BUCKET_NAME --query Policy --output text 2>/dev/null || echo "{}")

# Create new policy statement for this team
TEAM_POLICY_STATEMENT=$(cat << EOF
        {
            "Sid": "AllowTeam${TEAM_NAME}Access",
            "Effect": "Allow",
            "Principal": {
                "AWS": "$ROLE_ARN"
            },
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::$BUCKET_NAME",
                "arn:aws:s3:::$BUCKET_NAME/${TEAM_NAME}/*"
            ],
            "Condition": {
                "StringLike": {
                    "s3:prefix": "${TEAM_NAME}/*"
                }
            }
        }
EOF
)

# If there's an existing policy, merge it; otherwise create new
if [ "$EXISTING_POLICY" != "{}" ] && [ -n "$EXISTING_POLICY" ]; then
    # Parse existing policy and add new statement
    echo "$EXISTING_POLICY" | python3 -c "
import json
import sys
policy = json.load(sys.stdin)
if 'Statement' not in policy:
    policy['Statement'] = []
# Remove existing statement for this team if it exists
policy['Statement'] = [s for s in policy['Statement'] if s.get('Sid') != 'AllowTeam${TEAM_NAME}Access']
# Add new statement
new_stmt = json.loads('''$TEAM_POLICY_STATEMENT''')
policy['Statement'].append(new_stmt)
print(json.dumps(policy, indent=2))
" > /tmp/bucket-policy.json
else
    # Create new policy
    cat > /tmp/bucket-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
$TEAM_POLICY_STATEMENT
    ]
}
EOF
fi

# Apply the bucket policy
aws s3api put-bucket-policy \
    --bucket $BUCKET_NAME \
    --policy file:///tmp/bucket-policy.json

# Step 4: Enable versioning
echo "Enabling versioning..."
aws s3api put-bucket-versioning \
    --bucket $BUCKET_NAME \
    --versioning-configuration Status=Enabled

# Step 5: Enable server-side encryption
echo "Enabling server-side encryption..."
aws s3api put-bucket-encryption \
    --bucket $BUCKET_NAME \
    --server-side-encryption-configuration '{
        "Rules": [{
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "AES256"
            }
        }]
    }'

# Cleanup
rm -f /tmp/bucket-policy.json

echo ""
echo "Team bucket setup complete!"
echo "Bucket: s3://$BUCKET_NAME"
echo "Team prefix: ${TEAM_NAME}/"
echo "Team can access: s3://$BUCKET_NAME/${TEAM_NAME}/*"

