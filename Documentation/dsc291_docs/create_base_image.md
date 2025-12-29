### Create a base AMI for DSC291

Create a base AMI that already contains all required libraries inside a virtual environment. When launching a new AWS instance, a startup script can automatically:
- **create the venv**
- **Install all necessary packages**
- **Clone the DSC291 repo**
- **Run system updates and any other setup steps**

This makes the environment fully reproducible, so you and students can set it up on any instance with one script. Future updates are simple: just modify the script and rerun it on a fresh instance.

### Concepts

- **What is an AMI?** An Amazon Machine Image is a snapshot of an instance’s root volume and metadata. Launching from an AMI creates new instances with the same baseline state.
- **Why use a virtual environment?** It isolates Python dependencies for the course and is baked into the AMI, so Python tooling is ready immediately on boot.
- **Persistence model.** The AMI stores a snapshot; instances launched from it are independent. Changes made after launch are NOT written back to the AMI—you’d create a new AMI if you want to capture updates.
- **Security note.** Don’t bake secrets/API keys into the image. Prefer attaching an IAM role to your EC2 instance for access to AWS services.

### Steps

Once you have launched a fresh instance from AWS, follow the steps given below.
**Step 1:** Create setup script: `nano setup_dsc291.sh`
**Note:** We are using Amazon Linux, so use dnf. apt is Debian/Ubuntu-specific. Amazon Linux 2023 is based on Fedora/RHEL, so it uses dnf.

**Step 2:** Add the following to the bash script
```bash
#!/bin/bash
# DSC291 Amazon Linux 2023 environment setup

# Install Python 3 and pip (venv is built-in)
sudo dnf install -y python3 python3-pip git

# Create virtual environment
VENV_PATH=/home/ec2-user/dsc291_venv
python3 -m venv $VENV_PATH

# Activate venv and install packages
source $VENV_PATH/bin/activate
pip install --upgrade pip

# Install packages from requirements.txt if it exists
REQ_FILE="requirements.txt"
if [ -f "$REQ_FILE" ]; then
    echo "Installing packages from $REQ_FILE..."
    pip install -r "$REQ_FILE"
else
    echo "$REQ_FILE not found. Skipping package installation."
fi

# Clone and install public GitHub repo
git clone <https://github.com/yoavfreund/dask-CSE255.git> ~/dask-CSE255

echo "DSC291 environment setup complete!"
echo "Activate the venv with: source $VENV_PATH/bin/activate"
```

**Step 3:** Add permissions:
```bash
chmod +x setup_dsc291.sh
```

**Step 4:** Source the sh file:
```bash
./setup_dsc291.sh
```

**Step 5:** (optional, if not activated) Activating the venv:
```bash
source ~/dsc291_venv/bin/activate
```

### Requirements file
We also have a dedicated set of libraries that we want to install (placeholder).
Add the following to nano requirements.txt (this can reference the Dask repo later on).
```text
dask==2024.8.0
numpy==2.0.2
pandas==2.3.3
matplotlib==3.9.4
matplotlib-inline==0.2.1
seaborn==0.13.2
```

### Verify installed libraries
To check all the Python libraries installed: `pip freeze`

### Optional: Terminal colors
To add terminal colors:
Open the file: `nano ~/.bashrc`

Add the following at the bottom of the bashrc file:
```bash
PS1='\\[\\e[1;32m\\]\\u@\\h\\[\\e[m\\]:\\[\\e[1;34m\\]\\w\\[\\e[m\\]\\$ '
```
Apply: `source ~/.bashrc`


### **Create an AMI from Your Running EC2 Instance**

In your instance page in AWS: Actions → Image and templates → Create image.

- **Image name:** `DSC291-BaseImage`
- **Description:** `Amazon Linux 2023 instance with venv, requirements, and dask-CSE255 repo`
- Leave **reboot** as checked.

**Click →** Create image

AWS will now:

- Copy the instance root volume
- Create a snapshot
- Create an AMI descriptor


<p align="center">
  <img src="assets/create_ami.png" alt="Create AMI">
</p>

<span style="color: red;"><strong>This takes a few minutes.</strong></span>

Go to: **EC2 → AMIs**

We should see the image created and available.

<p align="center">
  <img src="assets/ami_image.png" alt="AMI list">
</p>



### **Creating a new instance from the above image**

- **Step1**: Go to AMIs page in AWS.
- **Step2**: Select the desired AMI: **`DSC291-BaseImage`**
- **Step3**: Click **Launch instance** **from AMI** (top menu). This opens the same instance launch wizard. Select your key-pair.
- **Step4**: `Launch Instance`

BOOM! 💥💥💥💥. Our Image creation was a SUCCESS.

<p align="center">
  <img src="assets/instance_from_ami.png" alt="AMI list" width="60%">
</p>

### Optional: Post-launch update

After launching a new instance from the AMI, you can update the repo and re-activate the environment:

```bash
source ~/dsc291_venv/bin/activate
cd ~/dask-CSE255 && git pull --ff-only
```
