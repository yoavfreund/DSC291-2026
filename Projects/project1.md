## Project 1: familiarization with AWS and counting

### Goals
1. Forming teams
2. Organizing resources
3. Performing large-scale counting.
   
### Teams
Teams, each consisting of 5 students, with the following roles

1. **Repository Manager** Responsible for maintaining the team's github repository and it's organization. Things to pay attention to:
   a. Directory organization: each directory should contain closely related items. 
   b. Readme file: the root directory should contain a readme.md file which describes the organization of the repository.
   c. Avoid large files: Files larger than 10MB should not be stored in the repository. If there is need to store them long term, they should reside on S3.
2. **Budget manager** Each student will be able to spin a small instance and a 10$ budget to spend on running it. Each student will be responsible for starting, stopping and monitoring their instance. 
                     Each team will be able to spin a large instance with 30 CPUs, with a budget of $200 to spend on it. The buget manager will be in charge of starting and stopping the instance and monitoring the cluster budget.
3. **Reporter** THe main outcome of each project is a  report. The report length would be specified for the project and will typically be 2-4 pages and be a Word document. Translating the figures and tables in the notebooks to the word report is the responsibility of the reporter.
4. **S3 Manager** responsible for storing and retrieving information stored on S3
5. **Configuration manager** responsible for maintaining the virtual environment. If there is a persistant problem, communicating with the TA to fix the AIM Image.

### Resources
1. Cursor
2. AWS instances: how to start/stop and monitor and instance from an image.
3. Connecting to an instance through SSH
4. Starting the virtua environment
5. Connecting Cursor to an instance through ssh
6. Interacting with a github repository from an instance.

## HW
1. Study the structure of the NYC taxicab repository available on s3:....
2. Use dask to load parquet files
3. The question you are to answer is: which are the 20 most popular routes (Pickup zone to Dropoff zone) for each of the taxi services. Use all years available.
4. Use a combination of 5% sampling and the Space-Saving (Metwally, Agrawal, Abbadi, 2005) algorithm to reduce memory and time requirements.
5. Your algorithm should complete, on the team computer, within XX minutes for 80 points, XX minutes for 90 points and XX minutes for 100 times
6. Test your algorithm by feeding it synthetic data.