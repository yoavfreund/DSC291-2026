# S3 Setup Guide for Class

This guide explains how to set up and use Amazon S3 buckets for the class. The setup uses IAM roles, which is the recommended and most secure approach.

## Overview

- **TAs**: Create S3 buckets and configure IAM roles
- **Students/Teams**: Use EC2 instances with attached IAM roles to access S3 buckets
- **Access Method**: IAM roles (no credentials needed on EC2 instances)
- **Bucket Structure**:
  - **One bucket per team**: Each team has their own bucket with full read/write access
  - **One shared bucket**: Read-only access for all teams, read-write for TAs (for shared datasets, reference materials, etc.)

## For Teaching Assistants (TAs)

### Prerequisites

- AWS CLI installed and configured with admin credentials
- Access to create IAM roles and S3 buckets
- List of team names (e.g., team01, team02, etc.)

### Step 1: Create S3 Buckets

#### Step 1a: Create Team Buckets

Create a separate bucket for each team:

```bash
# Navigate to the S3 scripts directory
cd Documentation/S3

# Make scripts executable
chmod +x *.sh

# Create bucket for team 1
./setup-s3-bucket.sh cse255-team01 us-east-1 EC2-S3-Role

# Create bucket for team 2
./setup-s3-bucket.sh cse255-team02 us-east-1 EC2-S3-Role

# Create bucket for team 3
./setup-s3-bucket.sh cse255-team03 us-east-1 EC2-S3-Role

# ... repeat for all teams
```

Each team will have:
- Their own bucket: `cse255-team01`, `cse255-team02`, etc.
- Full read/write access to their bucket
- No access to other teams' buckets

#### Step 1b: Create Shared Read-Only Bucket

Create a shared bucket that teams can read from (for shared datasets, reference materials, etc.):

```bash
# Create shared bucket (read-only for teams, read-write for TAs)
./setup-shared-readonly-bucket.sh cse255-shared us-east-1 EC2-S3-Role

# Optional: If you have a separate TA role, specify it for read-write access
# ./setup-shared-readonly-bucket.sh cse255-shared us-east-1 EC2-S3-Role arn:aws:iam::ACCOUNT_ID:role/TA-Role
```

The shared bucket:
- All teams have read-only access
- TAs have read-write access (if TA role ARN is provided)
- Use this for datasets, reference materials, or other shared resources

### Step 2: Create IAM Role for EC2 Instances

Create the IAM role that will be attached to all EC2 instances. This role allows access to all team buckets (read-write) and the shared bucket (read-only).

```bash
# Create IAM role with access to all buckets
# List all team buckets and the shared bucket
./setup-ec2-s3-access-multi-bucket.sh cse255-shared cse255-team01 cse255-team02 cse255-team03 cse255-team04

# Or if you have many teams, you can list them all:
./setup-ec2-s3-access-multi-bucket.sh cse255-shared \
    cse255-team01 cse255-team02 cse255-team03 cse255-team04 \
    cse255-team05 cse255-team06 cse255-team07 cse255-team08
```

This script:
- Creates IAM policy: `EC2-S3-Access-Policy`
- Creates IAM role: `EC2-S3-Role`
- Creates instance profile: `EC2-S3-InstanceProfile`
- Grants read-only access to shared bucket
- Grants read-write access to all team buckets

**Note**: You only need to run this once for the entire class. The same role can be used for all EC2 instances. If you add more teams later, you can re-run this script with the updated bucket list.

### Step 3: Attach IAM Role to EC2 Instances

For each EC2 instance that students will use:

```bash
# Attach role to instance
./attach-role-to-instance.sh i-1234567890abcdef0
```

**For new EC2 instances**, you can specify the IAM role during creation:

```bash
aws ec2 run-instances \
    --image-id ami-0c55b159cbfafe1f0 \
    --instance-type t2.micro \
    --iam-instance-profile Name=EC2-S3-InstanceProfile \
    --key-name your-key-pair \
    --security-group-ids sg-xxxxxxxxx \
    --subnet-id subnet-xxxxxxxxx
```

### Step 4: Verify Setup

Test that everything works:

```bash
# From an EC2 instance with the role attached
./verify-s3-access.sh cse255-data
```

## For Students/Teams

### Prerequisites

- Access to an EC2 instance with the IAM role attached (TAs will do this)
- AWS CLI installed on the EC2 instance
- Your team name (e.g., team01)

### Step 1: Verify Access

SSH into your EC2 instance and verify you have S3 access:

```bash
# Check your AWS identity (should show the role ARN)
aws sts get-caller-identity

# List available buckets
aws s3 ls

# List your team's bucket (replace team01 with your team number)
aws s3 ls s3://cse255-team01/

# List shared bucket (read-only)
aws s3 ls s3://cse255-shared/
```

### Step 2: Using S3 from Command Line

#### Working with Your Team Bucket (Read-Write)

```bash
# Replace team01 with your team number
TEAM_BUCKET="cse255-team01"

# List objects in your team's bucket
aws s3 ls s3://$TEAM_BUCKET/

# Upload a file
aws s3 cp local-file.txt s3://$TEAM_BUCKET/

# Upload a directory
aws s3 cp ./data/ s3://$TEAM_BUCKET/data/ --recursive

# Download a file
aws s3 cp s3://$TEAM_BUCKET/file.txt ./

# Download a directory
aws s3 cp s3://$TEAM_BUCKET/data/ ./local-data/ --recursive

# Sync directory (only uploads changed files)
aws s3 sync ./data/ s3://$TEAM_BUCKET/data/

# Delete a file
aws s3 rm s3://$TEAM_BUCKET/file.txt

# Delete a directory
aws s3 rm s3://$TEAM_BUCKET/data/ --recursive
```

#### Working with Shared Bucket (Read-Only)

```bash
SHARED_BUCKET="cse255-shared"

# List objects in shared bucket
aws s3 ls s3://$SHARED_BUCKET/

# Download a file (read-only - you cannot upload)
aws s3 cp s3://$SHARED_BUCKET/dataset.csv ./

# Download a directory
aws s3 cp s3://$SHARED_BUCKET/reference-data/ ./reference-data/ --recursive

# Sync shared data to local (read-only)
aws s3 sync s3://$SHARED_BUCKET/ ./shared-data/

# Note: Upload/delete operations will fail with "Access Denied"
# This is expected - teams only have read access to the shared bucket
```

### Step 3: Using S3 from Python (boto3)

#### Installation

```bash
pip install boto3
```

#### Basic Usage

```python
import boto3
from botocore.exceptions import ClientError

# Create S3 client (automatically uses IAM role credentials)
s3_client = boto3.client('s3')

# Replace team01 with your team number
TEAM_BUCKET = 'cse255-team01'
SHARED_BUCKET = 'cse255-shared'

# Working with your team bucket (read-write)
print("=== Team Bucket ===")
response = s3_client.list_objects_v2(Bucket=TEAM_BUCKET)
if 'Contents' in response:
    for obj in response['Contents']:
        print(f"Object: {obj['Key']}, Size: {obj['Size']} bytes")

# Upload a file to your team bucket
try:
    s3_client.upload_file('local-file.txt', TEAM_BUCKET, 'remote-file.txt')
    print("Upload successful")
except ClientError as e:
    print(f"Error uploading file: {e}")

# Download a file from your team bucket
try:
    s3_client.download_file(TEAM_BUCKET, 'remote-file.txt', 'local-file.txt')
    print("Download successful")
except ClientError as e:
    print(f"Error downloading file: {e}")

# Delete a file from your team bucket
s3_client.delete_object(Bucket=TEAM_BUCKET, Key='file.txt')

# Working with shared bucket (read-only)
print("\n=== Shared Bucket (Read-Only) ===")
response = s3_client.list_objects_v2(Bucket=SHARED_BUCKET)
if 'Contents' in response:
    for obj in response['Contents']:
        print(f"Object: {obj['Key']}, Size: {obj['Size']} bytes")

# Download from shared bucket
try:
    s3_client.download_file(SHARED_BUCKET, 'dataset.csv', 'dataset.csv')
    print("Downloaded from shared bucket")
except ClientError as e:
    print(f"Error downloading from shared bucket: {e}")

# Note: Upload to shared bucket will fail with AccessDenied
# This is expected - teams only have read access
```

#### Using S3 Resource (Higher-level API)

```python
import boto3

s3 = boto3.resource('s3')

# Replace team01 with your team number
TEAM_BUCKET = 'cse255-team01'
SHARED_BUCKET = 'cse255-shared'

# Working with your team bucket
team_bucket = s3.Bucket(TEAM_BUCKET)

# Upload file
team_bucket.upload_file('local-file.txt', 'remote-file.txt')

# Download file
team_bucket.download_file('remote-file.txt', 'local-file.txt')

# List all objects in your team bucket
for obj in team_bucket.objects.all():
    print(f"Object: {obj.key}, Size: {obj.size} bytes")

# Working with shared bucket (read-only)
shared_bucket = s3.Bucket(SHARED_BUCKET)

# List objects in shared bucket
for obj in shared_bucket.objects.all():
    print(f"Shared Object: {obj.key}, Size: {obj.size} bytes")

# Download from shared bucket
shared_bucket.download_file('dataset.csv', 'dataset.csv')
```

#### Reading Parquet Files with Dask

```python
import dask.dataframe as dd

# Replace team01 with your team number
TEAM_BUCKET = 'cse255-team01'
SHARED_BUCKET = 'cse255-shared'

# Read parquet files from your team bucket
df = dd.read_parquet(f's3://{TEAM_BUCKET}/data/*.parquet')

# Or read from shared bucket (read-only)
shared_df = dd.read_parquet(f's3://{SHARED_BUCKET}/datasets/*.parquet')

# Process the data
result = df.groupby('column').sum().compute()

# Write results back to your team bucket
result.to_parquet(f's3://{TEAM_BUCKET}/results/')

# Note: Writing to shared bucket will fail - teams only have read access
```

### Step 4: Verify Your Setup

Use the verification script:

```bash
# Download the script to your EC2 instance
# (or ask your TA to provide it)

# Run verification
./verify-s3-access.sh cse255-data
```

## Troubleshooting

### Permission Denied Errors

**Error**: `AccessDenied` or `403 Forbidden`

**Solutions**:
1. Verify IAM role is attached to your EC2 instance:
   ```bash
   aws sts get-caller-identity
   # Should show a role ARN, not a user ARN
   ```

2. Check that you're using the correct bucket name:
   ```bash
   # List buckets you can access
   aws s3 ls
   
   # List your team's bucket (replace team01 with your team number)
   aws s3 ls s3://cse255-team01/
   
   # List shared bucket
   aws s3 ls s3://cse255-shared/
   ```

3. Contact your TA if the role is not attached or bucket permissions are incorrect

### Credentials Not Found

**Error**: `Unable to locate credentials`

**Solutions**:
1. Verify IAM role is attached to the instance (ask your TA)
2. Wait a few minutes after the role is attached (IAM changes can take time to propagate)
3. Check AWS CLI is installed:
   ```bash
   aws --version
   ```

### Bucket Not Found

**Error**: `NoSuchBucket`

**Solutions**:
1. Verify the bucket name is correct (ask your TA)
2. Check the region:
   ```bash
   aws configure get region
   ```

## Scripts Reference

All scripts are in the `Documentation/S3/` directory:

- `setup-ec2-s3-access-multi-bucket.sh` - Creates IAM role and policy for multiple buckets (TAs only, run once)
- `setup-s3-bucket.sh` - Creates a single team S3 bucket (TAs)
- `setup-shared-readonly-bucket.sh` - Creates shared read-only bucket for teams (TAs)
- `attach-role-to-instance.sh` - Attaches IAM role to an EC2 instance (TAs)
- `verify-s3-access.sh` - Verifies S3 access from an EC2 instance (Everyone)

**Legacy scripts** (not used in current setup):
- `setup-ec2-s3-access.sh` - Single bucket version (use multi-bucket version instead)
- `setup-team-bucket.sh` - For prefix-based access (not used with separate buckets per team)

## Security Notes

- **Never store AWS credentials on EC2 instances** - Use IAM roles instead
- **Teams can only access their own prefix** - When using shared buckets with team prefixes
- **All data is encrypted** - Server-side encryption is enabled by default
- **Versioning is enabled** - Accidental deletions can be recovered

## Additional Resources

- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [IAM Roles for EC2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/iam-roles-for-amazon-ec2.html)
- [boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [Dask S3 Documentation](https://docs.dask.org/en/stable/howto/connect-to-remote-data.html#amazon-s3)

