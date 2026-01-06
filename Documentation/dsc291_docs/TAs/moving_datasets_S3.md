### Moving large datasets to S3

The taxi (~60 GB) and the weather datasets (~20 GB) are both located at ensemble (Prof's local machine) and our goal is to transfer these datasets to an S3 bucket. Now, one approach can be to move data to S3 directly from ensemble; this is slightly difficult, as you need to set public write permissions for the bucket from IT.

Since the datasets are GBs of magnitude, we need a bigger instance to move the dataset to S3 buckets. We use **t3.medium** and **100 GiB** storage.

To check available storage in an EC2 instance (get size of folders in a directory), do:

```bash
du -sh *
```

<p align="center">
  <img src="assets/check_available_storage.png" alt="Check available storage" width="50%">
</p>

### Transfer data to the instance

First, move the PEM file to your local machine/ensemble which houses the datasets.

```bash
rsync -avP ~/.ssh/grader_dsc291_pem.pem cse255_cluster:/home/akash2016/
```

Now use this command to transfer taxi data from ensemble to the instance:

```bash
rsync -avP -e "ssh -i grader_dsc291_pem.pem" /home/yfreund/taxi ec2-user@52.11.244.87:~
```
