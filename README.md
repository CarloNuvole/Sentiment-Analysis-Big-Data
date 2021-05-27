# Sentiment Analysis using Lexicon with Italian Tweets

## Terraform Setup

#### Step 1
> Per poter lanciare il progetto è necessario installare [Terraform](https://www.terraform.io/downloads.html) sulla propria macchina. A seconda del sistema operativo, potrebbe essere necessario spostare dalla cartella di download il file eseguibile terraform nella cartella del progetto. In questo caso, bisogna utilizzare il comando ./terraform <comando> invece di terraform <comando>. I comandi riportati di seguito riporteranno la prima forma, in quanto i test sono stati effettuati su Mac OS il quale opera in questo modo. 
  
#### Step 2  
> Dopo aver scaricato il progetto dalla repository, posizionarsi all’interno dalla cartella spark-terraform e creare il file terraform.tfvars e al suo interno incollare le seguenti stringhe:
```
  access_key="<AWS ACCESS KEY>"
  secret_key="<AWS SECRET KEY>”
  token="<AWS TOKEN>"
```
> Dove AWS ACCESS KEY, AWS SECRET KEY e AWS TOKEN sono le chiavi di AWS reperibili nella Workbench di Vocareum (la pagina che viene aperta subito dopo aver fatto il login su AWS Educate). Questi dati sono reperibili cliccando sul bottone "Account Details" e successivamente sul tasto "AWS CLI show".

#### Step 3
> Il passo successivo sarà quello di creare all’interno della cartella spark-terraform una chiave ssh, e sarà possibile farlo attraverso il comando:
```
  ssh-keygen -f localkey
```
#### Step 4
> Una volta creata la chiave ssh, sarà necessario **creare una nuova coppia di chiavi PEM** attraverso AWS. Terminata l’operazione, la chiave dovrà essere spostata all’interno della cartella spark-terraform ed è necessario cambiare i permessi di accesso alla chiave:
```
  chmod 400 amzkey.pem
```

#### Step 5
> Conclusi i passaggi precedenti, sarà necessario eseguire i seguenti comandi:
```
  ./terraform init
  ./terraform apply
```
> Attraverso AWS EC2 si può verificare se le macchine sono state create correttamente.

## AWS Setup

#### Step 1
> Una volta create le macchine, ci si collegherà al nodo master ‘s01’ tramite ssh, eseguendo il comando:
```
  ssh -i amzkey.pem ubuntu@<PUBLIC_DNS>
```
> Dove <PUBLIC_DNS> è l’indirizzo del master (s01) reperibile da AWS o dall’output di terraform. 

#### Step 2
> Se il collegamento ssh è andato a buon fine, eseguiamo i seguenti comandi sulla macchina del master:
```
  $HADOOP_HOME/sbin/start-dfs.sh
  $HADOOP_HOME/sbin/start-yarn.sh
  $HADOOP_HOME/sbin/mr-jobhistory-daemon.sh start historyserver
```
#### Step 3  
> Per verificare che i file siano presenti nel file system distribuito, è possibile eseguire il comando
```
  hadoop fs -ls
```
#### Step 4  
> Una volta verificata la presenza dei file, procediamo con l'avvio del master e degli slave: 
```
  $SPARK_HOME/sbin/start-master.sh
  $SPARK_HOME/sbin/start-slaves.sh spark://s01:7077
```
#### Step 5
> Per lanciare il file sentiment.py con la parte di test, è necessario eseguire il seguente comando:
```
  /opt/spark-3.0.1-bin-hadoop2.7/bin/spark-submit –master spark://s01:7077 --executor-cores 2 sentiment.py 5 true tweet_teams.csv tweet_teams_sentiment.csv 
```
