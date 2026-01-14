## **Directions to login and launch AWS instance**

This guide explains how to log into AWS and start an EC2 instance.

## Prerequisites

- AWS account access (UCSD institutional account)
- SSH client installed (pre-installed on macOS/Linux)


## Logging into AWS Console

1. Go to your [AWS Portal](https://ets-apps.ucsd.edu/individual/DSC291_WI26_G00/)
2. Enter your UCSD credentials.
3. You will see the costs accrued by your AWS account.
4. Click on "**Click here to access AWS**" at the bottom of the page.


## Starting an EC2 Instance

### If You Need to Create a New Instance

1. Navigate to **EC2** → **Instances** → **Launch instance**
2. **Name**: Enter a name (e.g., "cse255-student-instance")
3. **AMI**: Select **Amazon Linux 2023** (recommended)

   > **✅ PREFERRED METHOD: Launch from DSC291 Base Image**
   > 
   > Navigate to **AMIs** inside **Images** and choose the **`DSC291_BASE_IMAGE`** AMI and launch an instance from that AMI. 

4. **Instance type**: Select **t3.medium**
5. **Key pair**: 
   - Select an existing key pair, or
   - Click "Create new key pair" → Name it → Download the .pem file
6. **Network settings**:
   - Allow SSH traffic from **My IP** (recommended) or **Anywhere (0.0.0.0/0)** (less secure)
7. **Advanced details** (if needed):
   - IAM instance profile: Select **EC2-S3-InstanceProfile** (for S3 access)
8. Click **Launch instance**



### If You Have an Existing Instance

1. Navigate to **EC2** → **Instances** in the AWS Console
2. Select your instance from the list
3. Click **Instance state** → **Start instance**
4. Wait for the instance status to show "Running" (green checkmark)
5. Note the **Public IPv4 address** (you'll need this for SSH)


## Setting Up SSH Access

Once you click Launch an instance, you will see a section on Key pair (login) and you can create a new key pair from here.

### Step 1: Save and Secure Your Key File

```bash
# Move key to ~/.ssh directory
mv ~/Downloads/your-key.pem ~/.ssh/

# Set proper permissions (required for SSH)
chmod 400 ~/.ssh/your-key.pem
```

Make sure you created a key pair from AWS, downloaded and moved it to ~/.ssh/

### Step 2: Get Connection Details

From the AWS Console:
- **Public IP**: EC2 → Instances → Select instance → See "Public IPv4 address"
- **Username**: `ec2-user` (for Amazon Linux)

### Step 3: Test SSH Connection

```bash
ssh -i ~/.ssh/your-key.pem ec2-user@<PUBLIC_IP>
```

Replace `<PUBLIC_IP>` with your instance's public IP address.



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
2. Use the new IP address in your SSH command

## Security Notes

- Restrict SSH access to "My IP" in security groups
- Never share your .pem file
- Use IAM roles for S3 access (no credentials needed)
