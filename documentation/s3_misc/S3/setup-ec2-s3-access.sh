#!/bin/bash
# setup-ec2-s3-access.sh
# Creates IAM role and policy for EC2 instances to access S3 buckets
# Usage: ./setup-ec2-s3-access.sh <bucket-name> [instance-id]

set -e  # Exit on error

# Configuration
BUCKET_NAME="${1:-my-s3-bucket}"
ROLE_NAME="EC2-S3-Role"
POLICY_NAME="EC2-S3-Access-Policy"
INSTANCE_PROFILE_NAME="EC2-S3-InstanceProfile"
INSTANCE_ID="${2:-}"  # Optional: instance ID to attach role to

# Get account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "Using AWS Account ID: $ACCOUNT_ID"

# Step 1: Create policy document
echo "Creating IAM policy..."
cat > s3-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
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
    ]
}
EOF

# Create policy (ignore error if it already exists)
aws iam create-policy \
    --policy-name $POLICY_NAME \
    --policy-document file://s3-policy.json \
    --description "Allows EC2 instances to read/write to S3 bucket $BUCKET_NAME" \
    2>/dev/null || echo "Policy already exists, skipping creation"

POLICY_ARN="arn:aws:iam::${ACCOUNT_ID}:policy/${POLICY_NAME}"

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

echo "Setup complete!"
echo "Role ARN: arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}"
echo "Instance Profile: $INSTANCE_PROFILE_NAME"

