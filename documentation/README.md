# DSC291 - Getting Started

Complete setup guide for AWS EC2, GitHub, and S3 access.

---

## Team Formation

Please fill out the following Google Sheet to form your teams of 5:

👉 https://docs.google.com/spreadsheets/d/1SAUB3VEiCOhB09dcFVERWKl_1qNPkNYIKlFSRel-kvU/edit?usp=sharing

We will use this sheet to map each team to its AWS account, so it is important that the information is accurate and complete.

While filling the sheet, please follow the instructions shared by the professor in class, including assigning the following roles within your team:

**Required Roles (one per team):**

- **Treasurer**: Responsible for starting and stopping EC2 instances and monitoring AWS costs. 

- **Code Manager**: Responsible for code organization and maintaining the GitHub repository.

- **Communicator**: Responsible for compiling and submitting the final report for each project stage.

**Be careful not to run out of budget – no additional funds will be available.**

Please coordinate with your teammates and ensure all required fields are filled in by your team.

---

## Setup Steps

### Step 0: Login to AWS and Launch Instance

Login to AWS portal and launch your EC2 instance.

📖 **[logging_in.md](logging_in.md)**

- Login to UCSD AWS Portal
- Launch instance from DSC291 Base Image
- Set up SSH access
- Get your instance's public IP

### Step 1: Connect to EC2 with Cursor

SSH into your AWS instance and connect via Cursor IDE.

📖 **[ssh_tunneling_and_cursor.md](Students/ssh_tunneling_and_cursor.md)**

- Download and install Cursor
- Launch AWS instance from AMI
- Configure SSH and connect

### Step 2: GitHub Setup

Configure Git and clone your team repository.

📖 **[github_setup.md](Students/github_setup.md)**

- Set Git identity
- Generate Personal Access Token
- Clone repository with PAT

### Step 3: Access S3 Data

Choose how you want to work with S3 datasets (CLI is the preferred route):

**Using AWS CLI** (for file operations)  
📖 **[S3_cli_usage.md](Students/S3_cli_usage.md)**

**Using Python** (for data analysis - recommended)  
📖 **[S3_python_usage.md](Students/S3_python_usage.md)**

---

## Troubleshooting

- Each guide has a dedicated troubleshooting section
- Post questions on Piazza
- Reach out to your TA
