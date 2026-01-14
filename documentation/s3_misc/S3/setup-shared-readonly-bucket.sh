#!/bin/bash
# setup-shared-readonly-bucket.sh
# Creates a shared S3 bucket with read-only access for teams, read-write for TAs
# Usage: ./setup-shared-readonly-bucket.sh <bucket-name> <region> <role-name> <ta-role-arn>

set -e

# Configuration
BUCKET_NAME="${1}"
REGION="${2:-us-east-1}"
TEAM_ROLE_NAME="${3:-EC2-S3-Role}"
TA_ROLE_ARN="${4:-}"  # Optional: TA's IAM role ARN for read-write access

if [ -z "$BUCKET_NAME" ]; then
    echo "Usage: ./setup-shared-readonly-bucket.sh <bucket-name> <region> [team-role-name] [ta-role-arn]"
    echo "Example: ./setup-shared-readonly-bucket.sh cse255-shared us-east-1 EC2-S3-Role"
    exit 1
fi

# Get account ID and team role ARN
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
TEAM_ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${TEAM_ROLE_NAME}"

echo "Setting up shared read-only bucket: $BUCKET_NAME"
echo "Region: $REGION"
echo "Team Role ARN: $TEAM_ROLE_ARN"
if [ -n "$TA_ROLE_ARN" ]; then
    echo "TA Role ARN: $TA_ROLE_ARN"
fi

# Step 1: Create bucket
echo "Creating bucket..."
if [ "$REGION" = "us-east-1" ]; then
    aws s3 mb s3://$BUCKET_NAME 2>/dev/null || echo "Bucket may already exist"
else
    aws s3 mb s3://$BUCKET_NAME --region $REGION 2>/dev/null || echo "Bucket may already exist"
fi

# Step 2: Configure Block Public Access
echo "Configuring Block Public Access..."
aws s3api put-public-access-block \
    --bucket $BUCKET_NAME \
    --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

# Step 3: Create bucket policy
echo "Creating bucket policy..."

# Build policy statements
STATEMENTS=""

# Team read-only access
TEAM_STATEMENT=$(cat << EOF
        {
            "Sid": "AllowTeamReadOnly",
            "Effect": "Allow",
            "Principal": {
                "AWS": "$TEAM_ROLE_ARN"
            },
            "Action": [
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::$BUCKET_NAME",
                "arn:aws:s3:::$BUCKET_NAME/*"
            ]
        }
EOF
)
STATEMENTS="$TEAM_STATEMENT"

# TA read-write access (if provided)
if [ -n "$TA_ROLE_ARN" ]; then
    TA_STATEMENT=$(cat << EOF
        {
            "Sid": "AllowTAReadWrite",
            "Effect": "Allow",
            "Principal": {
                "AWS": "$TA_ROLE_ARN"
            },
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::$BUCKET_NAME",
                "arn:aws:s3:::$BUCKET_NAME/*"
            ]
        }
EOF
)
    STATEMENTS="$STATEMENTS,$TA_STATEMENT"
fi

# Create policy document
cat > /tmp/bucket-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
$STATEMENTS
    ]
}
EOF

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
echo "Shared bucket setup complete!"
echo "Bucket: s3://$BUCKET_NAME"
echo "Teams have: Read-only access"
if [ -n "$TA_ROLE_ARN" ]; then
    echo "TAs have: Read-write access"
fi

