#!/bin/bash
# setup-ec2-s3-access-multi-bucket.sh
# Creates IAM role and policy for EC2 instances to access multiple S3 buckets
# Usage: ./setup-ec2-s3-access-multi-bucket.sh <shared-bucket> <team-bucket-1> [team-bucket-2] ... [instance-id]

set -e  # Exit on error

# Configuration
SHARED_BUCKET="${1}"
shift || true
TEAM_BUCKETS=("$@")

# Remove instance ID if it's the last argument
INSTANCE_ID=""
if [ ${#TEAM_BUCKETS[@]} -gt 0 ]; then
    LAST_ARG="${TEAM_BUCKETS[-1]}"
    if [[ "$LAST_ARG" =~ ^i- ]]; then
        INSTANCE_ID="$LAST_ARG"
        unset 'TEAM_BUCKETS[-1]'
    fi
fi

if [ -z "$SHARED_BUCKET" ] || [ ${#TEAM_BUCKETS[@]} -eq 0 ]; then
    echo "Usage: ./setup-ec2-s3-access-multi-bucket.sh <shared-bucket> <team-bucket-1> [team-bucket-2] ... [instance-id]"
    echo "Example: ./setup-ec2-s3-access-multi-bucket.sh cse255-shared cse255-team01 cse255-team02 cse255-team03"
    exit 1
fi

ROLE_NAME="EC2-S3-Role"
POLICY_NAME="EC2-S3-Access-Policy"
INSTANCE_PROFILE_NAME="EC2-S3-InstanceProfile"

# Get account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "Using AWS Account ID: $ACCOUNT_ID"
echo "Shared bucket (read-only): $SHARED_BUCKET"
echo "Team buckets (read-write): ${TEAM_BUCKETS[*]}"

# Step 1: Create policy document
echo "Creating IAM policy..."

# Build resource list
RESOURCES=""
STATEMENTS=""

# Shared bucket - read-only access
SHARED_STATEMENT=$(cat << EOF
        {
            "Sid": "AllowSharedBucketReadOnly",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::$SHARED_BUCKET",
                "arn:aws:s3:::$SHARED_BUCKET/*"
            ]
        }
EOF
)
STATEMENTS="$SHARED_STATEMENT"

# Team buckets - read-write access
for BUCKET in "${TEAM_BUCKETS[@]}"; do
    TEAM_STATEMENT=$(cat << EOF
        {
            "Sid": "AllowTeamBucket${BUCKET}ReadWrite",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::$BUCKET",
                "arn:aws:s3:::$BUCKET/*"
            ]
        }
EOF
)
    if [ -n "$STATEMENTS" ]; then
        STATEMENTS="$STATEMENTS,$TEAM_STATEMENT"
    else
        STATEMENTS="$TEAM_STATEMENT"
    fi
done

# Create policy document
cat > s3-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
$STATEMENTS
    ]
}
EOF

# Create policy (ignore error if it already exists)
aws iam create-policy \
    --policy-name $POLICY_NAME \
    --policy-document file://s3-policy.json \
    --description "Allows EC2 instances to access S3 buckets: shared (read-only) and team buckets (read-write)" \
    2>/dev/null || echo "Policy already exists, updating..."

# If policy exists, update it
POLICY_ARN="arn:aws:iam::${ACCOUNT_ID}:policy/${POLICY_NAME}"
aws iam create-policy-version \
    --policy-arn $POLICY_ARN \
    --policy-document file://s3-policy.json \
    --set-as-default 2>/dev/null || echo "Policy version created or updated"

# Step 2: Create trust policy
echo "Creating IAM role..."
cat > ec2-trust-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "ec2.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

# Create role (ignore error if it already exists)
aws iam create-role \
    --role-name $ROLE_NAME \
    --assume-role-policy-document file://ec2-trust-policy.json \
    --description "IAM role for EC2 instances to access S3" \
    2>/dev/null || echo "Role already exists, skipping creation"

# Attach policy to role
echo "Attaching policy to role..."
aws iam attach-role-policy \
    --role-name $ROLE_NAME \
    --policy-arn $POLICY_ARN

# Step 3: Create instance profile
echo "Creating instance profile..."
aws iam create-instance-profile \
    --instance-profile-name $INSTANCE_PROFILE_NAME \
    2>/dev/null || echo "Instance profile already exists, skipping creation"

# Add role to instance profile (ignore error if already added)
aws iam add-role-to-instance-profile \
    --instance-profile-name $INSTANCE_PROFILE_NAME \
    --role-name $ROLE_NAME \
    2>/dev/null || echo "Role already in instance profile"

# Wait a moment for IAM to propagate
echo "Waiting for IAM changes to propagate..."
sleep 10

# Step 4: Attach to instance if provided
if [ -n "$INSTANCE_ID" ]; then
    echo "Attaching role to instance $INSTANCE_ID..."
    aws ec2 associate-iam-instance-profile \
        --instance-id $INSTANCE_ID \
        --iam-instance-profile Name=$INSTANCE_PROFILE_NAME
    echo "Role attached successfully!"
else
    echo "No instance ID provided. To attach this role to an instance, run:"
    echo "  ./attach-role-to-instance.sh <instance-id>"
fi

# Cleanup temporary files
rm -f s3-policy.json ec2-trust-policy.json

echo ""
echo "Setup complete!"
echo "Role ARN: arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}"
echo "Instance Profile: $INSTANCE_PROFILE_NAME"
echo ""
echo "Access permissions:"
echo "  - Shared bucket ($SHARED_BUCKET): Read-only"
echo "  - Team buckets: Read-write"

