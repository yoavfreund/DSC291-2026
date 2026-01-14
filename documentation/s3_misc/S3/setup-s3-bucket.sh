#!/bin/bash
# setup-s3-bucket.sh
# Creates an S3 bucket with proper permissions for EC2 access
# Usage: ./setup-s3-bucket.sh <bucket-name> <region> [role-name] [enable-public-access]

set -e

# Configuration
BUCKET_NAME="${1:-my-s3-bucket}"
REGION="${2:-us-east-1}"
ROLE_NAME="${3:-EC2-S3-Role}"
ENABLE_PUBLIC_ACCESS="${4:-false}"  # Set to "true" if you need public access

# Get account ID and role ARN
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}"

echo "Setting up S3 bucket: $BUCKET_NAME"
echo "Region: $REGION"
echo "Role ARN: $ROLE_ARN"

# Step 1: Create bucket
echo "Creating bucket..."
if [ "$REGION" = "us-east-1" ]; then
    aws s3 mb s3://$BUCKET_NAME 2>/dev/null || echo "Bucket may already exist"
else
    aws s3 mb s3://$BUCKET_NAME --region $REGION 2>/dev/null || echo "Bucket may already exist"
fi

# Step 2: Configure Block Public Access
echo "Configuring Block Public Access..."
if [ "$ENABLE_PUBLIC_ACCESS" = "true" ]; then
    aws s3api put-public-access-block \
        --bucket $BUCKET_NAME \
        --public-access-block-configuration \
        "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=false,RestrictPublicBuckets=false"
else
    aws s3api put-public-access-block \
        --bucket $BUCKET_NAME \
        --public-access-block-configuration \
        "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
fi

# Step 3: Create and apply bucket policy
echo "Creating bucket policy..."
cat > /tmp/bucket-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowEC2ReadWrite",
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
                "arn:aws:s3:::$BUCKET_NAME/*"
            ]
        }
    ]
}
EOF

aws s3api put-bucket-policy \
    --bucket $BUCKET_NAME \
    --policy file:///tmp/bucket-policy.json

# Step 4: Enable versioning (optional but recommended)
echo "Enabling versioning..."
aws s3api put-bucket-versioning \
    --bucket $BUCKET_NAME \
    --versioning-configuration Status=Enabled

# Step 5: Enable server-side encryption (optional but recommended)
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

echo "Bucket setup complete!"
echo "Bucket: s3://$BUCKET_NAME"
echo "Region: $REGION"

