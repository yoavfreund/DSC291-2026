### Git and GitHub setup on EC2

**Step 1: Configure Git identity on the EC2 instance**

```bash
git config --global user.name "Team EC2"
git config --global user.email "team@example.com"
```

To check if they are set properly, do:

```bash
git config --list
```

**Step 2:**

Directions for how to use team GitHub from the EC2 instance without storing credentials.

**Create a GitHub Personal Access Token** (any team member can do this).

On GitHub:

1. Go to **Settings → Developer settings → Personal access tokens → Tokens (classic)**.
2. Click **Generate new token → classic**.
3. Give it a name like `dsc291_ec2_access`.
4. Set an expiration (30 or 90 days is typical).

Once you generate it, **copy the token somewhere safe**—you won’t be able to see it again.

> 🚧 The instance will **use a single PAT** (from one account that has access to the team repo) to interact with GitHub. All Git operations (`git pull`, `git push`) from that instance will appear as **that account**, not the individual students.

**Step 3: cloning the repo**

```bash
git clone https://github.com/github_username/repo.git
```

You can enter a username manually again, but a workaround is to use your PAT in the clone command.

Clone using a PAT:

```bash
git clone https://<github_username>:<PAT>@github.com/<org>/<repo>.git
```
This will clone the repo.

When you are done with your changes/work, you can commit and push your changes back to the repo. If **your repo is cloned using a PAT in HTTPS**, you can push back changes directly.

> 🚧 If you **terminate the EC2 instance**, anything stored on it—including any locally saved PAT—**will be lost**. So, a **shutdown is safe for keeping your PAT**, but termination is not. You can start the instance again and continue where you left off.
