Projeto para coletar e listar informações de configuação do MongoDB em ambiente replicaset fornecidos pelo comando administrativo db.serverStatus().

O projeto utiliza Python junto com Pymongo para obter as informações de status dos servidores participantes do replicaset de forma individual, por meio do parâmetro de conexão "directConnection=true".
As informações obtidas serão tratadas para um formato em listas no Python e gravadas em algum SGBR relacional, no script é direcionado a gravação dos resultados obtidos para os bancos de dados relacionais SQLite e Sql Server/AzureSql Database.
Também tem uma função de gravação dos resultados em formato Json, essa função pode ser usada para uso também para gravação em outro SGBD de sua preferência.

O Projeto tem por objetivo facilitar a visualização das informações obtidas usando algum sistema de exibição de dados em formato tabular, no meu caso usei o Grafana para consumir os dados gravados em AzureSql Database. 
Esses dados exibidos no Grafana facilitam a leitura das informações de configuração dos servidores MongoDB participantes do replicaset.

No script eu obtenho os seguintes campos: 
 - Nome do host
 - Versão mongodb
 - Quantidade de coleções
 - Quantidade de views
 - ReadConcern configurado
 - WriteConcern configurado
 - Informações flowControl
 - Informações de índices - Quantidade
 - Quantidade de sessões lógicas ativas
 - Nome do replicaset
 - Hosts participantes do replicaset
 - Tipo de armazenamento usado - WiredTiger

Abaixo exemplo dos dados obtidos e apresentados em formato tabular pelo SQLite.
![image](https://github.com/user-attachments/assets/d4fd6b64-0eca-4f29-9eae-c8f606fe8f50)
