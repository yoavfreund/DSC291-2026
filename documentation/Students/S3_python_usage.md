### Accessing S3 using Python

**boto3** is the AWS SDK for Python. It allows you to interact with S3 programmatically.

### Installation

The library comes pre-installed in your virtual environment: `dsc291_venv`. If not accessible then simply do `pip install boto3`.


### Basic Usage

#### 1. Create an S3 client

```python
import boto3

# Create S3 client
s3 = boto3.client('s3')
```

> **Note:** If you've already configured AWS CLI (`aws configure`), boto3 will automatically use those credentials. Otherwise, you can set credentials programmatically or use environment variables.

#### 2. List all accessible buckets

```python
import boto3
import warnings
warnings.simplefilter('ignore')

s3 = boto3.client('s3')
response = s3.list_buckets()

print("Available buckets:")
for bucket in response['Buckets']:
    print(f"  - {bucket['Name']}")
```

#### 3. List files in a bucket

```python
import boto3
import warnings
warnings.simplefilter('ignore')

s3 = boto3.client('s3')
bucket_name = 'dsc291-ucsd'

# List objects in bucket
response = s3.list_objects_v2(Bucket=bucket_name, MaxKeys=10)

if 'Contents' in response:
    for obj in response['Contents']:
        print(f"{obj['Key']} - {obj['Size']} bytes")
```

#### 4. Download a file from S3

```python
import boto3
import warnings
warnings.simplefilter('ignore')

s3 = boto3.client('s3')
bucket_name = 'dsc291-ucsd'
s3_file_key = 'path/to/file.txt'
local_file_path = 'downloaded_file.txt'

# Download file
s3.download_file(bucket_name, s3_file_key, local_file_path)
print(f"Downloaded {s3_file_key} to {local_file_path}")
```

#### 5. Upload a file to S3

```python
import boto3

s3 = boto3.client('s3')
bucket_name = 'your-bucket-name'
local_file_path = 'myfile.txt'
s3_file_key = 'uploads/myfile.txt'

# Upload file
s3.upload_file(local_file_path, bucket_name, s3_file_key)
print(f"Uploaded {local_file_path} to s3://{bucket_name}/{s3_file_key}")
```

### Troubleshooting

- **NoCredentialsError** → Either configure AWS CLI (`aws configure`) or use `config=Config(signature_version=UNSIGNED)` for public buckets
- **AccessDenied** → Check bucket name and ensure you have proper permissions or use anonymous access for public buckets
- **PythonDeprecationWarning about Python 3.9** → This is just a warning, not an error. boto3 works fine with Python 3.9 until April 2026. You can safely ignore it for this course
