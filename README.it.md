# Sentiment Analysis mediante Lexicon utilizzando tweet in italiano

### Autori: [Carlo Nuvole](https://github.com/CarloNuvole) & [Luca Sedda](https://github.com/seddaluca)

## Terraform Setup (ITA)

#### Step 1
> Per poter lanciare il progetto è necessario installare [Terraform](https://www.terraform.io/downloads.html) sulla propria macchina. A seconda del sistema operativo, potrebbe essere necessario spostare dalla cartella di download il file eseguibile terraform nella cartella del progetto. In questo caso, bisogna utilizzare il comando `./terraform <comando>` invece di `terraform <comando>`. I comandi riportati di seguito riporteranno la prima forma, in quanto i test sono stati effettuati su Mac OS il quale opera in questo modo. 
  
#### Step 2  
> Dopo aver scaricato il progetto dalla repository, posizionarsi all’interno dalla cartella `spark-terraform` e creare il file `terraform.tfvars` e al suo interno incollare le seguenti stringhe:
```
  access_key="<AWS ACCESS KEY>"
  secret_key="<AWS SECRET KEY>"
  token="<AWS TOKEN>"
```
> Dove `AWS ACCESS KEY`, `AWS SECRET KEY` e `AWS TOKEN` sono le chiavi di AWS reperibili nella Workbench di Vocareum (la pagina che viene aperta subito dopo aver fatto il login su AWS Educate). Questi dati sono reperibili cliccando sul bottone "Account Details" e successivamente sul tasto "AWS CLI show".

#### Step 3
> Il passo successivo sarà quello di creare all’interno della cartella `spark-terraform` una chiave ssh attraverso il comando:
```
  ssh-keygen -f localkey
```
#### Step 4
> Una volta creata la chiave ssh, sarà necessario creare una `nuova coppia di chiavi PEM su AWS`. Terminata l’operazione, la chiave dovrà essere spostata all’interno della cartella `spark-terraform` ed è necessario cambiare i permessi di accesso alla chiave attraverso il comando:
```
  chmod 400 amzkey.pem
```
> Attenzione: il nome della chiave nel filesystem deve corrispondere al nome scelto su AWS, in caso contrario Terraform non potrà verificare l'autenticità della chiave.

#### Step 5
> Prima di avviare Terraform, è necessario creare una `subnet-id` nella Dashboard di EC2. Per farlo, è necessario recarsi nel tab Rete & Sicurezza e successivamente in Interfacce di rete, scegliendo come area `us-east-1a` e come indirizzo personalizzato IPv4 `172.31.0.64`. Come ultima cosa, è necessario selezionare almeno un gruppo di sicurezza (ad esempio `default`. Se è già presente un gruppo di sicurezza chiamato "Hadoop_cluster_sc" **non utilizzarlo**).
<img src="https://github.com/CarloNuvole/Sentiment-Analysis-Big-Data/blob/main/images/photo_2021-05-28%2018.59.29.jpeg">

> Subito dopo aver creato la subnet, è necessario copiare il valore `Subnet ID` dentro il file `main.tf` alle `righe 39 e 106`.

#### Step 6
> Conclusi i passaggi precedenti, sarà necessario eseguire i seguenti comandi:
```
  ./terraform init
  ./terraform apply
```
> Attraverso AWS EC2 si può verificare se le macchine sono state create correttamente.

## AWS Setup (ITA)

#### Step 1
> Una volta create le macchine, ci si collegherà al nodo master `‘s01’` tramite ssh, eseguendo il comando:
```
  ssh -i amzkey.pem ubuntu@<PUBLIC_DNS>
```
> Dove `<PUBLIC_DNS>` è l’indirizzo del master (s01) reperibile da AWS o dall’output di terraform. 

#### Step 2
> Se il collegamento ssh è andato a buon fine, eseguiamo i seguenti comandi sulla macchina del master (s01):
```
  $HADOOP_HOME/sbin/start-dfs.sh
  $HADOOP_HOME/sbin/start-yarn.sh
  $HADOOP_HOME/sbin/mr-jobhistory-daemon.sh start historyserver
```
#### Step 3  
> Una volta avviato Hadoop, è necessario procedere alla copia dei file e dataset d'esempio all'interno del file system distribuito. Abbiamo realizzato uno script per semplificare questi passaggi, per avviarlo basterà eseguire il seguente comando:
```
  bash setup_hadoop.sh
```
> Al termine dell'esecuzione nell'elenco dovrebbero comparire 6 file

#### Step 4  
> Una volta verificata la presenza dei file, procediamo con l'avvio del master e degli slave: 
```
  $SPARK_HOME/sbin/start-master.sh
  $SPARK_HOME/sbin/start-slaves.sh spark://s01:7077
```
#### Step 5
> Per lanciare il file `sentiment.py con la parte di test`, è necessario eseguire il seguente comando:
```
  /opt/spark-3.0.1-bin-hadoop2.7/bin/spark-submit --master spark://s01:7077 --executor-cores 2 sentiment.py 5 true tweet_teams.csv tweet_teams_sentiment.csv 
```
> Al termine dell'esecuzione, è possibile lanciare il file `test.py` provvedendo prima a spostare il file `Comparison_%date%.csv` su Hadoop (dove `%date%` corrisponde alla data con cui è stato eseguito il file `sentiment.py`):
```
  hadoop fs -put Comparison_%date%.csv
  /opt/spark-3.0.1-bin-hadoop2.7/bin/spark-submit --master spark://s01:7077 --executor-cores 2 test.py 5 Comparison_%Date%.csv
``` 
> Se si è eseguito il file `sentiment.py senza la modalità test`, è possibile scaricare il file `Valutation_%date%.csv` sulla propria macchina locale utilizzando il seguente comando (**sulla propria macchina locale**):
``` 
scp -i amzkey.pem ubuntu@<PUBLIC_DNS>:~/Valutation_%date%.csv <PATH_ON_YOUR_MACHINE> 
``` 
> Dove `<PATH_ON_YOUR_MACHINE>` è il percorso sul proprio computer (i.e `~/Documents` per scaricare il file nella propria cartella Documenti) e `%date%` è la data di esecuzione dello script.
#### Step 6
> Al termine dei test, è possibile eliminare tutte le istanze create utilizzando il seguente comando:

```
  ./terraform destroy
``` 

## Informazioni aggiuntive
> A partire dal 10 Maggio 2021, Amazon ha apportato delle modifiche per l'utilizzo di AWS Educate. A causa di queste modifiche alcuni passaggi illustrati precedentemente potrebbero non funzionare.

> Le chiavi per l'API di Twitter nel file `twitter.py` sono state omesse per motivi di sicurezza. Per utilizzare questo script, è necessario utilizzare un `Account Sviluppatore Twitter` oppure è possibile utilizzare quelle presenti all'interno della relezione del progetto.
