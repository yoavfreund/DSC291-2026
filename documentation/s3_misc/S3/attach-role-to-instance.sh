#!/bin/bash
# attach-role-to-instance.sh
# Attaches the EC2-S3-Role to an EC2 instance
# Usage: ./attach-role-to-instance.sh <instance-id>

set -e

INSTANCE_ID="${1}"
INSTANCE_PROFILE_NAME="EC2-S3-InstanceProfile"

if [ -z "$INSTANCE_ID" ]; then
    echo "Usage: ./attach-role-to-instance.sh <instance-id>"
    echo "Example: ./attach-role-to-instance.sh i-1234567890abcdef0"
    exit 1
fi

echo "Attaching IAM role to instance: $INSTANCE_ID"

# Check if instance exists
if ! aws ec2 describe-instances --instance-ids $INSTANCE_ID &>/dev/null; then
    echo "Error: Instance $INSTANCE_ID not found"
    exit 1
fi

# Attach the instance profile
aws ec2 associate-iam-instance-profile \
    --instance-id $INSTANCE_ID \
    --iam-instance-profile Name=$INSTANCE_PROFILE_NAME

echo "Role attached successfully!"
echo "Instance: $INSTANCE_ID"
echo "Instance Profile: $INSTANCE_PROFILE_NAME"
echo ""
echo "Note: It may take a few minutes for the role to be available on the instance."
echo "SSH into the instance and run: aws sts get-caller-identity"

