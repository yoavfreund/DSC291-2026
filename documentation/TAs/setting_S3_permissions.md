### Setting S3 permissions for public read

We want the S3 bucket (`dsc291-ucsd`) which houses the taxi and weather datasets accessible to the students, so they can easily read it in the EC2 instances.

Since the datasets are themselves procured from open sources, we can make the S3 bucket public.

**Step 1: Disable “Block Public Access” for the bucket**

By default, AWS blocks public buckets.

- Go to S3 → Your bucket
- Open Permissions tab
- Click Block public access (bucket settings) → Edit
- Uncheck: Block all public access
- Save changes and confirm

This only allows public access; it does not grant it yet.

**Step 2: Add a bucket policy for public read access**

In the same Permissions tab, open Bucket policy and paste this policy and save:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicListEntireBucket",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::dsc291-ucsd"
    },
    {
      "Sid": "PublicReadAllObjects",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::dsc291-ucsd/*"
    }
  ]
}
```

Note: Public access does not make a bucket visible in personal (or students) AWS console. AWS Console visibility requires explicit IAM permissions, not public access.

### How students should access the files (AWS S3 CLI)

First, verify the public accessibility. Use ```aws s3 ls s3://dsc291-ucsd --no-sign-request```. You should see:

<p align="center">
  <img src="assets/s3_accessibility.png" alt="S3 Accessibility" width="70%">
</p>


```bash
aws s3 sync s3://dsc291-ucsd/taxi ./taxi --no-sign-request
```

```bash
aws s3 sync s3://dsc291-ucsd/weather ./weather --no-sign-request
```

The --no-sign-request flag allows downloading from a public S3 bucket without AWS credentials and supports resuming large downloads (~100GB). If you dont use this flag, you might encounter a <span style="color: red;">fatal error: Unable to locate credentials</span>.


