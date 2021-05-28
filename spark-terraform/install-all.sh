#/bin/bash

# Se la macchina non è completamente operativa attende, altrimenti alcuni comandi possono fallire
until [[ -f /var/lib/cloud/instance/boot-finished ]]; do
  sleep 1
done

# Aggiornamento dei pacchetti 
sudo apt-get -y update

# Installazione di Python3
sudo apt-get -y install python3
sudo apt-get -y install python3-pip

# Installazione librerie
pip3 install pandas
pip3 install pyspark
pip3 install nltk
pip3 install tweepy

# Installazione Java
sudo apt-get -y install openjdk-8-jdk
export JAVA_HOME="/usr/lib/jvm/java-8-openjdk-amd64"
pip3 install --user pydoop

# IP del master e degli slave
echo '
172.31.0.241 s01
172.31.0.242 s02
172.31.0.243 s03
172.31.0.244 s04
172.31.0.245 s05
172.31.0.246 s06' | sudo tee --append /etc/hosts > /dev/null

sudo chmod 700 /home/ubuntu/.ssh
sudo chmod 600 /home/ubuntu/.ssh/id_rsa

# Impostazioni per Java
echo '
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export PATH=$PATH:$JAVA_HOME/bin
export PYSPARK_PYTHON=python3' | sudo tee --append /home/ubuntu/.bashrc > /dev/null

# Installazione di Hadoop 2.7.7
cd /opt/
sudo wget https://archive.apache.org/dist/hadoop/common/hadoop-2.7.7/hadoop-2.7.7.tar.gz > /dev/null
sudo tar zxvf hadoop-2.7.7.tar.gz > /dev/null

# Configurazione di Hadoop
echo '
export HADOOP_HOME=/opt/hadoop-2.7.7
export PATH=$PATH:$HADOOP_HOME/bin
export HADOOP_CONF_DIR=/opt/hadoop-2.7.7/etc/hadoop' | sudo tee --append /home/ubuntu/.bashrc > /dev/null

# Modifica del file core-site.xml
echo '<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<!--
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License. See accompanying LICENSE file.
-->

<!-- Put site-specific property overrides in this file. -->
<configuration>
  <property>
    <name>fs.defaultFS</name>
    <value>hdfs://s01:9000</value>
  </property>
</configuration>' | sudo tee /opt/hadoop-2.7.7/etc/hadoop/core-site.xml > /dev/null

# Modifica del file yarn-site.xml
echo '<?xml version="1.0"?>
<!--
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License. See accompanying LICENSE file.
-->

<!-- Put site-specific property overrides in this file. -->
<configuration>
  <property>
    <name>yarn.nodemanager.aux-services</name>
    <value>mapreduce_shuffle</value>
  </property>
  <property>
    <name>yarn.nodemanager.aux-services.mapreduce.shuffle.class</name>
    <value>org.apache.hadoop.mapred.ShuffleHandler</value>
  </property>
  <property>
    <name>yarn.resourcemanager.hostname</name>
    <value>s01</value>
  </property>
</configuration>' | sudo tee /opt/hadoop-2.7.7/etc/hadoop/yarn-site.xml > /dev/null

# Modifica del file mapred-site.xml
sudo cp /opt/hadoop-2.7.7/etc/hadoop/mapred-site.xml.template /opt/hadoop-2.7.7/etc/hadoop/mapred-site.xml

echo '<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<!--
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License. See accompanying LICENSE file.
-->

<!-- Put site-specific property overrides in this file. -->
<configuration>
  <property>
    <name>mapreduce.jobtracker.address</name>
    <value>s01:54311</value>
  </property>
  <property>
    <name>mapreduce.framework.name</name>
    <value>yarn</value>
  </property>
</configuration>' | sudo tee /opt/hadoop-2.7.7/etc/hadoop/mapred-site.xml > /dev/null

# Modifica del file hdfs-site.xml
echo '<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<!--
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License. See accompanying LICENSE file.
-->

<!-- Put site-specific property overrides in this file. -->
<configuration>
  <property>
    <name>dfs.replication</name>
    <value>5</value>
  </property>
  <property>
    <name>dfs.namenode.name.dir</name>
    <value>file:///opt/hadoop-2.7.7/hadoop_data/hdfs/namenode</value>
  </property>
  <property>
    <name>dfs.datanode.data.dir</name>
    <value>file:///opt/hadoop-2.7.7/hadoop_data/hdfs/datanode</value>
  </property>
</configuration>' | sudo tee /opt/hadoop-2.7.7/etc/hadoop/hdfs-site.xml > /dev/null

# Settaggio del master su Hadoop
echo '
s01' | sudo tee --append /opt/hadoop-2.7.7/etc/hadoop/masters > /dev/null

# Settaggio degli slave su Hadoop
echo '
s02
s03
s04
s05
s06
' | sudo tee /opt/hadoop-2.7.7/etc/hadoop/slaves > /dev/null

# Settaggio di Hadoop
sudo sed -i -e 's/export\ JAVA_HOME=\${JAVA_HOME}/export\ JAVA_HOME=\/usr\/lib\/jvm\/java-8-openjdk-amd64/g' /opt/hadoop-2.7.7/etc/hadoop/hadoop-env.sh

sudo mkdir -p /opt/hadoop-2.7.7/hadoop_data/hdfs/namenode
sudo mkdir -p /opt/hadoop-2.7.7/hadoop_data/hdfs/datanode

sudo chown -R ubuntu /opt/hadoop-2.7.7


# Installazione di Spark
cd /opt/
sudo wget https://archive.apache.org/dist/spark/spark-3.0.1/spark-3.0.1-bin-hadoop2.7.tgz > /dev/null
 
sudo tar -xvzf spark-3.0.1-bin-hadoop2.7.tgz > /dev/null

echo '
export SPARK_HOME=/opt/spark-3.0.1-bin-hadoop2.7
export PATH=$PATH:$SPARK_HOME/bin' | sudo tee --append /home/ubuntu/.bashrc > /dev/null

sudo chown -R ubuntu /opt/spark-3.0.1-bin-hadoop2.7

cd spark-3.0.1-bin-hadoop2.7

cp conf/spark-env.sh.template conf/spark-env.sh  


# Configurazione di Spark
echo '
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export SPARK_MASTER_HOST=s01
export HADOOP_CONF_DIR=/opt/hadoop-2.7.7/etc/hadoop
export HADOOP_HOME=/opt/hadoop-2.7.7' | sudo tee --append conf/spark-env.sh > /dev/null

# Settaggio degli slave su Spark
echo '
s02
s03
s04
s05
s06
' | sudo tee --append conf/slaves > /dev/null

cp conf/spark-defaults.conf.template conf/spark-defaults.conf

# Download dei file necessari a nltk
python3 -m nltk.downloader popular

# Avvio di tutti i nodi
echo -e '$HADOOP_HOME/sbin/start-dfs.sh && $HADOOP_HOME/sbin/start-yarn.sh && $HADOOP_HOME/sbin/mr-jobhistory-daemon.sh start historyserver' > /home/ubuntu/hadoop-start-master.sh

echo '$SPARK_HOME/sbin/start-master.sh' > /home/ubuntu/spark-start-master.sh

echo '$SPARK_HOME/sbin/start-slave.sh spark://s01:7077' > /home/ubuntu/spark-start-slave.sh
