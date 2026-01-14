# Using S3 from an EC2 Instance

This guide explains how to configure and use Amazon S3 from an EC2 instance, including setting up proper read/write permissions.

## Table of Contents

1. [Overview](#overview)
2. [Method 1: IAM Roles (Recommended)](#method-1-iam-roles-recommended)
3. [Method 2: AWS Credentials](#method-2-aws-credentials)
4. [Setting S3 Bucket Permissions](#setting-s3-bucket-permissions)
5. [Using AWS CLI](#using-aws-cli)
6. [Using Python (boto3)](#using-python-boto3)
7. [Troubleshooting](#troubleshooting)

## Overview

There are two main approaches to access S3 from an EC2 instance:

1. **IAM Roles (Recommended)**: Attach an IAM role to your EC2 instance. This is the most secure method as it doesn't require storing credentials.
2. **AWS Credentials**: Store AWS access keys on the EC2 instance (less secure, not recommended for production).

## Method 1: IAM Roles (Recommended)

### Step 1: Create an IAM Role

1. Go to the **IAM Console** → **Roles** → **Create role**
2. Select **AWS service** → **EC2** → **Next**
3. Create a new policy or attach an existing one with S3 permissions:

```json
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
                "arn:aws:s3:::your-bucket-name",
                "arn:aws:s3:::your-bucket-name/*"
            ]
        }
    ]
}
```

4. Name your policy (e.g., `EC2-S3-Access`) and create it
5. Attach the policy to your role
6. Name your role (e.g., `EC2-S3-Role`) and create it

### Step 2: Attach Role to EC2 Instance

**For a new EC2 instance:**
- During instance creation, in the **Configure Instance** step, select your IAM role from the dropdown

**For an existing EC2 instance:**
1. Go to **EC2 Console** → Select your instance
2. **Actions** → **Security** → **Modify IAM role**
3. Select your IAM role and save

### Step 3: Verify Access

SSH into your EC2 instance and verify:

```bash
# Check if credentials are available
aws sts get-caller-identity

# List S3 buckets (if you have permission)
aws s3 ls
```

## Method 2: AWS Credentials

⚠️ **Not recommended for production** - Use IAM roles instead.

### Step 1: Create IAM User with S3 Permissions

1. Go to **IAM Console** → **Users** → **Create user**
2. Attach a policy with S3 permissions (same as above)
3. Go to **Security credentials** tab → **Create access key**
4. Download the access key ID and secret access key

### Step 2: Configure Credentials on EC2

```bash
# Install AWS CLI if not already installed
sudo yum install aws-cli  # Amazon Linux
# or
sudo apt-get install awscli  # Ubuntu

# Configure credentials
aws configure
# Enter your Access Key ID
# Enter your Secret Access Key
# Enter default region (e.g., us-east-1)
# Enter default output format (e.g., json)
```

Or create credentials file manually:

```bash
mkdir -p ~/.aws
cat > ~/.aws/credentials << EOF
[default]
aws_access_key_id = YOUR_ACCESS_KEY_ID
aws_secret_access_key = YOUR_SECRET_ACCESS_KEY
EOF

cat > ~/.aws/config << EOF
[default]
region = us-east-1
output = json
EOF
```

## Setting S3 Bucket Permissions

### Option 1: Bucket Policy (Recommended)

Bucket policies control access at the bucket level. This is useful when using IAM roles.

1. Go to **S3 Console** → Select your bucket → **Permissions** tab
2. Scroll to **Bucket policy** → **Edit**
3. Add a policy like this:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowEC2ReadWrite",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::YOUR_ACCOUNT_ID:role/EC2-S3-Role"
            },
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::your-bucket-name",
                "arn:aws:s3:::your-bucket-name/*"
            ]
        }
    ]
}
```

**For public read access (read-only):**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::your-bucket-name/*"
        }
    ]
}
```

### Option 2: ACL (Access Control List)

1. Go to **S3 Console** → Select your bucket → **Permissions** tab
2. Scroll to **Access Control List (ACL)** → **Edit**
3. Grant permissions to specific AWS accounts or make it public

⚠️ **Note**: ACLs are being phased out. Use bucket policies instead.

### Option 3: Block Public Access Settings

If you need public access, you may need to modify Block Public Access settings:

1. Go to **S3 Console** → Select your bucket → **Permissions** tab
2. **Block Public Access settings** → **Edit**
3. Uncheck the settings you need to allow (be careful with security implications)

## Using AWS CLI

### Basic Commands

```bash
# List all buckets
aws s3 ls

# List objects in a bucket
aws s3 ls s3://your-bucket-name/

# List objects in a prefix
aws s3 ls s3://your-bucket-name/prefix/

# Copy file to S3
aws s3 cp local-file.txt s3://your-bucket-name/path/

# Copy file from S3
aws s3 cp s3://your-bucket-name/path/file.txt ./

# Copy directory recursively
aws s3 cp ./local-directory/ s3://your-bucket-name/path/ --recursive

# Sync directory (only uploads changed files)
aws s3 sync ./local-directory/ s3://your-bucket-name/path/

# Delete a file
aws s3 rm s3://your-bucket-name/path/file.txt

# Delete all files in a prefix
aws s3 rm s3://your-bucket-name/prefix/ --recursive

# Create a bucket
aws s3 mb s3://new-bucket-name

# Delete a bucket (must be empty first)
aws s3 rb s3://bucket-name
```

### Presigned URLs

Generate temporary URLs for sharing:

```bash
# Generate presigned URL (valid for 1 hour by default)
aws s3 presign s3://your-bucket-name/path/file.txt

# Generate presigned URL with custom expiration (e.g., 1 day = 86400 seconds)
aws s3 presign s3://your-bucket-name/path/file.txt --expires-in 86400
```

## Using Python (boto3)

### Installation

```bash
pip install boto3
```

### Basic Usage

```python
import boto3
from botocore.exceptions import ClientError

# Create S3 client (automatically uses IAM role credentials if available)
s3_client = boto3.client('s3')

# List buckets
response = s3_client.list_buckets()
for bucket in response['Buckets']:
    print(f"Bucket: {bucket['Name']}")

# List objects in a bucket
response = s3_client.list_objects_v2(Bucket='your-bucket-name')
if 'Contents' in response:
    for obj in response['Contents']:
        print(f"Object: {obj['Key']}, Size: {obj['Size']}")

# Upload a file
try:
    s3_client.upload_file('local-file.txt', 'your-bucket-name', 'path/remote-file.txt')
    print("Upload successful")
except ClientError as e:
    print(f"Error uploading file: {e}")

# Download a file
try:
    s3_client.download_file('your-bucket-name', 'path/remote-file.txt', 'local-file.txt')
    print("Download successful")
except ClientError as e:
    print(f"Error downloading file: {e}")

# Upload file object (from memory)
with open('local-file.txt', 'rb') as data:
    s3_client.upload_fileobj(data, 'your-bucket-name', 'path/remote-file.txt')

# Get object as bytes
response = s3_client.get_object(Bucket='your-bucket-name', Key='path/file.txt')
content = response['Body'].read()

# Delete an object
s3_client.delete_object(Bucket='your-bucket-name', Key='path/file.txt')

# Generate presigned URL
url = s3_client.generate_presigned_url(
    'get_object',
    Params={'Bucket': 'your-bucket-name', 'Key': 'path/file.txt'},
    ExpiresIn=3600  # 1 hour
)
print(f"Presigned URL: {url}")
```

### Using S3 Resource (Higher-level API)

```python
import boto3

s3 = boto3.resource('s3')
bucket = s3.Bucket('your-bucket-name')

# Upload file
bucket.upload_file('local-file.txt', 'path/remote-file.txt')

# Download file
bucket.download_file('path/remote-file.txt', 'local-file.txt')

# List all objects
for obj in bucket.objects.all():
    print(f"Object: {obj.key}, Size: {obj.size}")

# List objects with prefix
for obj in bucket.objects.filter(Prefix='path/'):
    print(f"Object: {obj.key}")

# Delete object
obj = bucket.Object('path/file.txt')
obj.delete()
```

### Reading Parquet Files with Dask

```python
import dask.dataframe as dd
import s3fs

# Create S3 filesystem
s3 = s3fs.S3FileSystem()

# Read parquet files from S3
df = dd.read_parquet('s3://your-bucket-name/path/to/parquet/*.parquet', 
                     filesystem=s3)

# Or with boto3 credentials
df = dd.read_parquet('s3://your-bucket-name/path/to/parquet/*.parquet')
```

## Troubleshooting

### Permission Denied Errors

**Error**: `AccessDenied` or `403 Forbidden`

**Solutions**:
1. Verify IAM role is attached to EC2 instance
2. Check IAM policy includes necessary S3 permissions
3. Verify bucket policy allows your IAM role/user
4. Check bucket Block Public Access settings
5. Verify resource ARNs in policies are correct

### Credentials Not Found

**Error**: `Unable to locate credentials`

**Solutions**:
1. If using IAM role: Verify role is attached to instance
2. If using credentials: Check `~/.aws/credentials` file exists
3. Verify AWS CLI is configured: `aws configure list`
4. Check environment variables: `echo $AWS_ACCESS_KEY_ID`

### Testing Permissions

```bash
# Test read access
aws s3 ls s3://your-bucket-name/

# Test write access
echo "test" > test.txt
aws s3 cp test.txt s3://your-bucket-name/test.txt
aws s3 rm s3://your-bucket-name/test.txt
rm test.txt

# Check your identity
aws sts get-caller-identity
```

### Common IAM Policy Patterns

**Read-only access:**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::your-bucket-name",
                "arn:aws:s3:::your-bucket-name/*"
            ]
        }
    ]
}
```

**Write-only access (no read):**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject"
            ],
            "Resource": "arn:aws:s3:::your-bucket-name/*"
        }
    ]
}
```

**Full access to specific prefix:**
```json
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
                "arn:aws:s3:::your-bucket-name",
                "arn:aws:s3:::your-bucket-name/prefix/*"
            ]
        }
    ]
}
```

## Security Best Practices

1. **Always use IAM roles** instead of storing credentials on EC2 instances
2. **Follow principle of least privilege** - only grant necessary permissions
3. **Use bucket policies** to restrict access at the bucket level
4. **Enable versioning** for important buckets
5. **Enable logging** to track access: `aws s3api put-bucket-logging`
6. **Use encryption** for sensitive data (SSE-S3, SSE-KMS, or SSE-C)
7. **Regularly audit** IAM policies and bucket policies
8. **Use presigned URLs** for temporary access instead of making buckets public

## Additional Resources

- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [IAM Roles for EC2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/iam-roles-for-amazon-ec2.html)
- [S3 Bucket Policies](https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucket-policies.html)
- [boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)

