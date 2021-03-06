# Sentiment Analysis using Lexicon with Italian Tweets

This README is also available in [Italian](https://github.com/CarloNuvole/Sentiment-Analysis-Big-Data/blob/main/README.it.md).

### Authors: [Carlo Nuvole](https://github.com/CarloNuvole) & [Luca Sedda](https://github.com/seddaluca)

## Terraform Setup

#### Step 1
> To run this project you need to install [Terraform](https://www.terraform.io/downloads.html) in your computer. Depending on your OS, you might move Terraform binary from download folder to the project folder. In this case, you need to use `./terraform <command>` instead of `terraform <command>`. The following instructions will use the first because the tests were made using Mac OS which works this way.
  
#### Step 2  
> After downloading the project from the repository, you need to move inside `spark-terraform` folder and create `terraform.tfvars` file and paste in it the following lines:
```
  access_key="<AWS ACCESS KEY>"
  secret_key="<AWS SECRET KEY>"
  token="<AWS TOKEN>"
```
> Where `AWS ACCESS KEY`, `AWS SECRET KEY` and `AWS TOKEN` are the AWS keys obtainable in Vocareum Workbench (the page opened immediately after AWS Educate login). Those string are obtainable clicking on "Account Details" button and later "AWS CLI show" button.

#### Step 3
> Create inside `spark-terraform` folder a ssh key using the following command:
```
  ssh-keygen -f localkey
```
#### Step 4
> Once you have created the ssh key, you need to create a `new pair of PEM keys on AWS`. Then, you need move the key inside `spark-terraform` folder changing its permissions using the following commands:
```
  chmod 400 amzkey.pem
```
> Note that the file name for the key must be the one you chose in AWS, otherwise Terraform cannot verify key authenticity. 

#### Step 5
> Before starting Terraform, you need to create a `subnet-id` in EC2 Dashboard. Go to Network Interface under Network & Security tab and create a new interface, choosing as area `us-east-1a`. You need also to set as custom IPv4 IP address `172.31.0.64` and select at least one security group (i.e `default`. If you have already a security group called "Hadoop_cluster_sc" **do not use it**).
<img src="https://github.com/CarloNuvole/Sentiment-Analysis-Big-Data/blob/main/images/photo_2021-05-28%2018.59.22.jpeg">

> Once the subnet has been created, you need to copy the `Subnet ID` value into `main.tf` file at `rows 39 and 106`.

#### Step 6
> Now you can run Terraform using the following commands:
```
  ./terraform init
  ./terraform apply
```
> You can check if all instances were created correctly in AWS EC2 Dashboard.
 
## AWS Setup

#### Step 1
> Connect to the master node `???s01???` through ssh using the following command: 
```
  ssh -i amzkey.pem ubuntu@<PUBLIC_DNS>
```
> Where `<PUBLIC_DNS>` is the master address (s01) that can be found in AWS EC2 Dashboard or in the Terraform output.

#### Step 2
> If ssh connection to the master node (s01) is established, run the following commands:
```
  $HADOOP_HOME/sbin/start-dfs.sh
  $HADOOP_HOME/sbin/start-yarn.sh
  $HADOOP_HOME/sbin/mr-jobhistory-daemon.sh start historyserver
```
#### Step 3  
> Once Hadoop is running, you need to copy the files and datasets to the destribuited file system. To simplify this operation, you can use our script `setup_hadoop.sh` to make it writing only the following command:
``` 
  bash setup_hadoop.sh
```
> If the output shows 6 files, it means that all files were moved correctly.
#### Step 4  
> To start the master and the slaves run the following commands:
```
  $SPARK_HOME/sbin/start-master.sh
  $SPARK_HOME/sbin/start-slaves.sh spark://s01:7077
```
#### Step 5
> To run `sentiment.py script in test mode`, run the following command:
```
  /opt/spark-3.0.1-bin-hadoop2.7/bin/spark-submit --master spark://s01:7077 --executor-cores 2 sentiment.py 5 true tweet_teams.csv tweet_teams_sentiment.csv 
```
> Before lunching `test.py` script you need to move `Comparison_%date%.csv` file to Hadoop (where `%date%` is the date of `sentiment.py` execution) using the following commands: 
```
  hadoop fs -put Comparison_%date%.csv
  /opt/spark-3.0.1-bin-hadoop2.7/bin/spark-submit --master spark://s01:7077 --executor-cores 2 test.py 5 Comparison_%Date%.csv
``` 
> If you chose to run `sentiment.py without test mode`, you can download `Valutation_%date%.csv` in your local machine using the following command (**only on your local machine**):
``` 
  scp -i amzkey.pem ubuntu@<PUBLIC_DNS>:~/Valutation_%date%.csv <PATH_ON_YOUR_MACHINE> 
``` 
> Where `<PATH_ON_YOUR_MACHINE>` is the path on your computer (i.e `~/Documents` to download into your Documents folder) and `%date%` is the date of script execution.
#### Step 6
> You can delete all the instances using the following command:
```
  ./terraform destroy
``` 
## More informations
> As of the week of May 10 2021, there were changes made to the AWS Educate program. Due this, you may encounter some problems with some steps reported above. 

> Twitter API keys are missing in `twitter.py` for security reasons. If you want to use this script, get a `Twitter Developer Account` or check the project report to use ours.
