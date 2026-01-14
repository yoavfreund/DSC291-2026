#!/bin/bash
# verify-s3-access.sh
# Verifies S3 access setup from an EC2 instance
# Usage: ./verify-s3-access.sh [bucket-name]

set -e

BUCKET_NAME="${1:-}"

echo "=== Verifying S3 Access Setup ==="
echo ""

# Check AWS identity
echo "1. Current AWS Identity:"
IDENTITY=$(aws sts get-caller-identity 2>&1)
if [ $? -eq 0 ]; then
    echo "$IDENTITY" | python3 -m json.tool 2>/dev/null || echo "$IDENTITY"
    ROLE_ARN=$(echo "$IDENTITY" | grep -o 'arn:aws:iam::[^"]*:role/[^"]*' | head -1)
    if [ -n "$ROLE_ARN" ]; then
        echo "   ✓ Using IAM role: $ROLE_ARN"
    else
        echo "   ⚠ Not using an IAM role (may be using access keys)"
    fi
else
    echo "   ✗ Cannot get identity: $IDENTITY"
    exit 1
fi

# Check if bucket name provided
if [ -z "$BUCKET_NAME" ]; then
    echo ""
    echo "2. Available S3 buckets:"
    aws s3 ls 2>&1 || echo "   ✗ Cannot list buckets"
    echo ""
    echo "To test a specific bucket, run: ./verify-s3-access.sh <bucket-name>"
    exit 0
fi

echo ""
echo "2. Testing bucket access: s3://$BUCKET_NAME"

# Test list bucket
echo "   Testing list bucket..."
if aws s3 ls "s3://$BUCKET_NAME/" &>/dev/null; then
    echo "   ✓ Can list bucket contents"
    aws s3 ls "s3://$BUCKET_NAME/" | head -5
else
    echo "   ✗ Cannot list bucket contents"
fi

# Test write access
echo ""
echo "3. Testing write access..."
TEST_FILE="/tmp/s3-test-$$.txt"
echo "test content $(date)" > $TEST_FILE
TEST_KEY="test-verify-$$.txt"

if aws s3 cp "$TEST_FILE" "s3://$BUCKET_NAME/$TEST_KEY" &>/dev/null; then
    echo "   ✓ Can upload files"
    
    # Test read access
    echo ""
    echo "4. Testing read access..."
    if aws s3 cp "s3://$BUCKET_NAME/$TEST_KEY" "/tmp/s3-test-download-$$.txt" &>/dev/null; then
        echo "   ✓ Can download files"
    else
        echo "   ✗ Cannot download files"
    fi
    
    # Test delete access
    echo ""
    echo "5. Testing delete access..."
    if aws s3 rm "s3://$BUCKET_NAME/$TEST_KEY" &>/dev/null; then
        echo "   ✓ Can delete files"
    else
        echo "   ✗ Cannot delete files"
    fi
else
    echo "   ✗ Cannot upload files"
fi

# Cleanup
rm -f $TEST_FILE /tmp/s3-test-download-$$.txt

echo ""
echo "=== Verification Complete ==="

