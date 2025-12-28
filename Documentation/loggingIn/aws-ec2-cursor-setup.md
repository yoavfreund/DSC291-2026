# AWS EC2 Setup and Cursor Connection Guide

This guide explains how to log into AWS, start an EC2 instance, and connect to it using Cursor IDE.

## Prerequisites

- AWS account access (personal or institutional)
- SSH client installed (pre-installed on macOS/Linux)
- Cursor IDE installed
- Key pair (.pem file) for SSH access

## Logging into AWS Console

1. Go to [https://aws.amazon.com/console/](https://ets-apps.ucsd.edu/individual/DSC291_WI26_A00)
2. enter your active directory credentials.
3. You will see the costs accrued by your AWS account.
4. Click on "Click here to access AWS" at the bottom of the page.
5. Click on the 3xx3 grid at the top left of the page and select ec2

## Starting an EC2 Instance

### If You Have an Existing Instance

1. Navigate to **EC2** → **Instances** in the AWS Console
2. Select your instance from the list
3. Click **Instance state** → **Start instance**
4. Wait for the instance status to show "Running" (green checkmark)
5. Note the **Public IPv4 address** (you'll need this for SSH)

### If You Need to Create a New Instance

1. Navigate to **EC2** → **Instances** → **Launch instance**
2. **Name**: Enter a name (e.g., "cse255-student-instance")
3. **AMI**: Select **Amazon Linux 2023** (recommended)
4. **Instance type**: Select **t3.medium**
5. **Key pair**: 
   - Select an existing key pair, or
   - Click "Create new key pair" → Name it → Download the .pem file
6. **Network settings**:
   - Allow SSH traffic from **My IP** (recommended) or **Anywhere (0.0.0.0/0)** (less secure)
7. **Advanced details** (if needed):
   - IAM instance profile: Select **EC2-S3-InstanceProfile** (for S3 access)
8. Click **Launch instance**

## Setting Up SSH Access

### Step 1: Save and Secure Your Key File

```bash
# Move key to ~/.ssh directory
mv ~/Downloads/your-key.pem ~/.ssh/

# Set proper permissions (required for SSH)
chmod 400 ~/.ssh/your-key.pem
```

### Step 2: Get Connection Details

From the AWS Console:
- **Public IP**: EC2 → Instances → Select instance → See "Public IPv4 address"
- **Username**: `ec2-user` (for Amazon Linux)

### Step 3: Test SSH Connection

```bash
ssh -i ~/.ssh/your-key.pem ec2-user@<PUBLIC_IP>
```

Replace `<PUBLIC_IP>` with your instance's public IP address.

## Connecting to EC2 from Cursor

### Step 1: Install Remote SSH Extension

1. Open Cursor
2. Press `Cmd+Shift+X` (Mac) or `Ctrl+Shift+X` (Windows/Linux)
3. Search for "Remote - SSH"
4. Install the extension by Microsoft

### Step 2: Configure SSH

Create or edit `~/.ssh/config`:

```bash
nano ~/.ssh/config
```

Add this configuration:

```
Host ec2-instance
    HostName <PUBLIC_IP_ADDRESS>
    User ec2-user
    IdentityFile ~/.ssh/your-key.pem
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
```

Replace:
- `<PUBLIC_IP_ADDRESS>` with your instance's public IP
- `your-key.pem` with your actual key file name

### Step 3: Connect in Cursor

1. Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
2. Type "Remote-SSH: Connect to Host"
3. Select "ec2-instance"
4. Cursor opens a new window connected to the remote instance
5. Click "Open Folder" → Navigate to `/home/ec2-user` → Click "OK"

## Working in Cursor

Once connected:
- **Terminal**: Press `` Ctrl+` `` to open terminal (runs on EC2)
- **File Explorer**: Browse files on the remote instance
- **Install packages**: `pip install dask pandas boto3 s3fs`

## Troubleshooting

### Connection Refused

- Verify instance is "Running" in AWS Console
- Check security group allows SSH (port 22) from your IP
- Wait 1-2 minutes after starting instance

### Permission Denied

- Verify key permissions: `chmod 400 ~/.ssh/your-key.pem`
- Check username is `ec2-user` (for Amazon Linux)
- Verify key pair matches the instance

### IP Address Changed

If your instance gets a new IP after restart:
1. Get new IP from AWS Console
2. Update `~/.ssh/config` with new IP address
3. Reconnect in Cursor

### Cursor Can't Find SSH

- macOS/Linux: SSH is pre-installed
- Windows: Install OpenSSH or use Git Bash
- Check Cursor settings: `Cmd+,` → Search "remote.SSH.path"

## Security Notes

- Restrict SSH access to "My IP" in security groups
- Never share your .pem file
- Use IAM roles for S3 access (no credentials needed)
