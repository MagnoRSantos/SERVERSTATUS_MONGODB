# -*- coding: utf-8 -*-

## IMPORTS PYTHON MODULES
import dotenv
import os, json
import io
import sqlite3
import socket
from pymongo import MongoClient
from datetime import datetime

## IMPORTS PROPRIOS
from sendMsgChatGoogle import sendMsgChatGoogle
from removeLogAntigo import removeLogs



### Variaveis do local do script e log mongodb
dirapp = os.path.dirname(os.path.realpath(__file__))

## Carrega os valores do .env
dotenvFile = os.path.join(dirapp, '.env.dev')
dotenv.load_dotenv(dotenvFile)


## funcao que retorna data e hora Y-M-D H:M:S
def obterDataHora():
    """
        OBTEM DATA E HORA
    """
    datahora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return datahora


## funcao para verificar os valores do dotenv
def getValueEnv(valueEnv):
    """
    OBTEM VALORES DO ARQUIVO .ENV
    """
    v_valueEnv = os.getenv(valueEnv)
    
    if not v_valueEnv:
        msgLog = "Variável de ambiente '{0}' não encontrada.".format(valueEnv)
        gravaLog(msgLog, 'a')

    return v_valueEnv


## funcao de gravacao de log
def gravaLog(strValue, strAcao):
    """
    FUNCAO DE GRAVACAO DO ARQUIVO DE LOG
    """

    ## Path LogFile
    datahoraLog = datetime.now().strftime('%Y-%m-%d')
    pathLog = os.path.join(dirapp, 'log')
    pathLogFile = os.path.join(pathLog, 'logServerStatusMongoDB_{}.txt'.format(datahoraLog))

    if not os.path.exists(pathLog):
        os.makedirs(pathLog)
    else:
        pass

    msg = strValue
    with io.open(pathLogFile, strAcao, encoding='utf-8') as fileLog:
        fileLog.write('{0}\n'.format(strValue))

    return msg


## funcao de remocao de arquivos de logs antigos
def removerLogAntigo(v_diasRemover):
    """
    FUNCAO DE REMOCAO DE ARQUIVOS DE LOG ANTIGOS
    ACIMA DE X DIAS: v_diasRemover
    """
    ## remocao dos logs antigos acima de xx dias
    pathLog = os.path.join(dirapp, 'log')
    msgLog = "Removendo logs acima de {0} dias.".format(v_diasRemover)
    gravaLog(msgLog, 'a')
    msgLog = removeLogs(v_diasRemover, pathLog)
    gravaLog(msgLog, 'a')


## funcao de envio de alerta de exception ao google chat via webhook
def enviaExceptionGChat(msgGChat):
    """
    FUNCAO DE ENVIO DE DADOS REFERENTE E EXECEPTION
    ESSES DADOS SAO ENVIADOS AO GOGGLE CHAT DA EQUIPE RESPONSAVEL
    CRIADO PARA QUANDO DER FALHA A EQUIPE SER AVISADA
    """
    URL_WEBHOOK_DBA = getValueEnv("URL_WEBHOOK_DBA")
    datahora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    myhost = socket.gethostname()

    msgWebHook = 'Host: {0} - EXCEPTION - MONITORAMENTO DADOS SERVERSTATUS MONGODB - {1}\nMensagem: {2}'.format(myhost, datahora, msgGChat)
    sendMsgChatGoogle(URL_WEBHOOK_DBA, msgWebHook)


def serverStatusMongoDB(v_MONGO_HOST):
    """
    FUNCAO PARA OBTER DADOS DO MONGODB
    OBTEM INFORMACOES DA FUNCAO serverStatus DO MONGODB

    OBS.: CONNSTRING USADA COM DIRECTCONNECTION PARA OBTER DE SERVIDORES ESPECIFICOS
    """

    try:
       
        DBUSERNAME = getValueEnv("USERNAME_MONGODB")
        DBPASSWORD = getValueEnv("PASSWORD_MONGODB")
        #MONGO_HOST = getValueEnv("SERVER_MONGODB")
        MONGO_HOST = v_MONGO_HOST
        DBAUTHDB   = getValueEnv("DBAUTHDB_MONGODB")

        
        #connstr = 'mongodb://' + DBUSERNAME + ':' + DBPASSWORD + '@' + DBPASSWORD + '/' + DBAUTHDB + '?directConnection=true'
        connstr = 'mongodb://{0}:{1}@{2}/{3}?directConnection=true'.format(DBUSERNAME, DBPASSWORD, MONGO_HOST, DBAUTHDB)

        with MongoClient(connstr) as client:

            #=======================================================

            #print(client)

            db = client ['admin']
            v_serverStatus = db.command("serverStatus")

            # nome do host
            v_host = v_serverStatus["host"]

            # versao mongodb
            v_version = v_serverStatus["version"]

            # quantidade de colecoes
            v_collections = v_serverStatus["catalogStats"]["collections"]

            # quantidade de views
            v_views = v_serverStatus["catalogStats"]["views"]

            # ReadConcern configurado
            v_defaultReadConcernLevel = v_serverStatus["defaultRWConcern"]["defaultReadConcern"]["level"]

            # WriteConcern configurado
            v_defaultWriteConcernW = v_serverStatus["defaultRWConcern"]["defaultWriteConcern"]["w"]
            v_defaultWriteConcernWTIMEOUT = v_serverStatus["defaultRWConcern"]["defaultWriteConcern"]["wtimeout"]

            # Informacoes flowControl
            v_flowControl = v_serverStatus["flowControl"]["enabled"]
            v_flowControltargetRateLimit = v_serverStatus["flowControl"]["targetRateLimit"]

            # Informacoes de indices - Quantidade
            v_indexStats = v_serverStatus["indexStats"]["count"]

            # Quantidade de sessoes logicas ativas
            v_activeSessionsCount = v_serverStatus["logicalSessionRecordCache"]["activeSessionsCount"]

            # Nome do replicaset
            v_replsetName = v_serverStatus["repl"]["setName"]

            # Hosts participantes do replicaset
            v_replhosts = v_serverStatus["repl"]["hosts"]

            # Tipo de armazenamento usado - WiredTiger
            v_storageEngine = v_serverStatus["storageEngine"]["name"]

            

            listValuesServerStatus = '{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}, {12}, {13}'.\
                format(
                    v_host,
                    v_version,
                    v_collections, 
                    v_views,
                    v_defaultReadConcernLevel,
                    v_defaultWriteConcernW,
                    v_defaultWriteConcernWTIMEOUT,
                    v_flowControl,
                    v_flowControltargetRateLimit,
                    v_indexStats,
                    v_activeSessionsCount,
                    v_replsetName,
                    v_replhosts,
                    v_storageEngine,
                    obterDataHora()
                )
            
            # cria a lista auxiliar vazia
            listReturnMongoDBAux = []

            # insere valores na lista auxiliar
            listReturnMongoDBAux.insert(0, v_host)
            listReturnMongoDBAux.insert(1, v_version)
            listReturnMongoDBAux.insert(2, v_collections)
            listReturnMongoDBAux.insert(3, v_views)
            listReturnMongoDBAux.insert(4, v_defaultReadConcernLevel)
            listReturnMongoDBAux.insert(5, v_defaultWriteConcernW)
            listReturnMongoDBAux.insert(6, v_defaultWriteConcernWTIMEOUT)
            listReturnMongoDBAux.insert(7, v_flowControl)
            listReturnMongoDBAux.insert(8, v_flowControltargetRateLimit)
            listReturnMongoDBAux.insert(9, v_indexStats)
            listReturnMongoDBAux.insert(10, v_activeSessionsCount)
            listReturnMongoDBAux.insert(11, v_replsetName)
            listReturnMongoDBAux.insert(12, str(v_replhosts))
            listReturnMongoDBAux.insert(13, v_storageEngine)
            listReturnMongoDBAux.insert(14, obterDataHora())

            #gravaLog(listValuesServerStatus)
            #print(gravaLog(msg))     

    except Exception as e:
        datahora = obterDataHora()
        msgException = "Error: {0}".format(e)
        msgLog = 'Obter dados MongoDB [ServerStatusMongoDB] [Erro]: {0}\n{1}'.format(datahora, msgException)
        print(gravaLog(msgLog, 'a'))
        enviaExceptionGChat(msgLog)

    finally:
        return listReturnMongoDBAux 
    

def listToJson(v_listReturnMongoDB):
    """
    FUNCAO CRIADA PARA TRANSFORMA OS DADOS OBTIDOS EM FORMATO DE LISTA PARA JSON
    """

    # Definição das chaves do JSON
    chaves = ["Host", 
              "Version", 
              "CollectionsQtde", 
              "ViewsQtde", 
              "defaultReadConcernLevel", 
              "defaultWriteConcernW", 
              "defaultWriteConcernWTIMEOUT", 
              "flowControl", 
              "flowControltargetRateLimit", 
              "indexStatsQtde", 
              "activeSessionsCount", 
              "replsetName", 
              "replhosts", 
              "storageEngine",
              "DataHora"
            ]
    
    # Transformação dos dados em JSON
    json_lista = [dict(zip(chaves, item)) for item in v_listReturnMongoDB]

    # Convertendo para JSON formatado
    json_str = json.dumps(json_lista, indent=4)
    gravaLog(json_str, 'a')

    # Exibir resultado
    return json_str



## Funcao de criacao do database e tabela caso nao exista
def create_tables(dbname_sqlite3):
    """
    script sql de criacao da tabela
    pode ser adicionado a criacao de mais de uma tabela
    separando os scripts por virgulas
    """
    sql_statements = [
        """
        CREATE TABLE ServerStatusMongoDB(
            Host VARCHAR(60), 
            Version VARCHAR(10), 
            CollectionsQtde INTEGER, 
            ViewsQtde INTEGER, 
            defaultReadConcernLevel VARCHAR(15), 
            defaultWriteConcernW VARCHAR(15), 
            defaultWriteConcernWTIMEOUT INTEGER, 
            flowControl BIT, 
            flowControltargetRateLimit INTEGER, 
            indexStatsQtde INTEGER, 
            activeSessionsCount INTEGER, 
            replsetName VARCHAR(20),
            replhosts VARCHAR(300), 
            storageEngine VARCHAR(20),
            dataHora DATETIME
        )       
        """
    ]

    # variaveis da conexão ao database
    path_dir_db = os.path.join(dirapp, 'db')
    path_full_dbname_sqlite3 = os.path.join(path_dir_db, dbname_sqlite3)
    
    # cria o diretorio caso nao exista
    if not os.path.exists(path_dir_db):
        os.makedirs(path_dir_db)
    else:
        pass
    

    try:
        with sqlite3.connect(path_full_dbname_sqlite3) as conn:
            cursor = conn.cursor()
            for statement in sql_statements:
                cursor.execute(statement)
            
            conn.commit()

    except sqlite3.Error as e:
        datahora = obterDataHora()
        msgException = "Error: {0}".format(e)
        msgLog = 'Criar tabela SQlite3 [ServerStatusMongoDB] [Erro]: {0}\n{1}'.format(datahora, msgException)
        print(gravaLog(msgLog, 'a'))
        enviaExceptionGChat(msgLog)

    finally:
        msgLog = 'Criado tabela [ServerStatusMongoDB] no database [{0}]'.format(dbname_sqlite3)
        print(gravaLog(msgLog, 'a'))


## gera comandos de inserts conforme valores da lista passada
def gravaDadosSqlite(v_listWebhook):
    """
    FUNCAO PARA GRAVAR OS DADOS OBTIDOS EM UM BANCO DE DADOS SQLITE
    """
    
    dbname_sqlite3 = getValueEnv("DATABASE_SQLITE3")
    path_dir_db = os.path.join(dirapp, 'db')
    path_full_dbname_sqlite3 = os.path.join(path_dir_db, dbname_sqlite3)
    RowCount = 0

    ## verifica se banco de dados existe 
    # caso não exista realizada a chamada da funcao de criacao
    if not os.path.exists(path_full_dbname_sqlite3):
        create_tables(dbname_sqlite3)
    else:
        pass

    
    try:
        with sqlite3.connect(path_full_dbname_sqlite3) as conn:

            cursor = conn.cursor()
            
            ## sql statement DELETE
            sql_statements = ["DELETE FROM ServerStatusMongoDB"]
            for statement in sql_statements:
                cursor.execute(statement)  
            
            conn.commit()
            RowCountDelete = conn.total_changes
            print("Registros deletados: {}".format(RowCountDelete))
            

            sql_statement = """INSERT INTO ServerStatusMongoDB 
                (   Host, 
                    Version, 
                    CollectionsQtde, 
                    ViewsQtde, 
                    defaultReadConcernLevel, 
                    defaultWriteConcernW, 
                    defaultWriteConcernWTIMEOUT, 
                    flowControl, 
                    flowControltargetRateLimit, 
                    indexStatsQtde, 
                    activeSessionsCount, 
                    replsetName,
                    replhosts, 
                    storageEngine,
                    dataHora
                ) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            for params in v_listWebhook:
                print(params)
                cursor.execute(sql_statement, params)


            conn.commit()
            RowCountInsert = conn.total_changes
    
    except sqlite3.Error as e:
        datahora = obterDataHora()
        msgException = "Error: {0}".format(e)
        msgLog = 'Fim Insert tabelas SQlite3 [Erro]: {0}\n{1}'.format(datahora, msgException)
        print(gravaLog(msgLog, 'a'))
        enviaExceptionGChat(msgLog)

    finally:
        RowCount = RowCountInsert - RowCountDelete
        msgLog = 'Quantidade de Registros Inseridos no SQlite3: {0} registro(s)'.format(RowCount)
        print(gravaLog(msgLog, 'a'))
        

## funcao inicial
def main():
    # grava inicio do log
    datahora = obterDataHora()
    msg = '***** List Info ServerStatus MongoDB ***** BEGIN: ' + datahora
    print(msg)
    gravaLog(msg, 'a')

    ## remover logs antigos acima de xx dias
    diasRemover = 10
    removerLogAntigo(diasRemover)

    ## cria lista geral vazia
    listReturnMongoDB = []

    MONGO_HOST = getValueEnv("SERVER_MONGODB")

    ## iteracao por cada servidor da lista
    listServers = [item.strip(" '") for item in MONGO_HOST.split(",")]
    for server in listServers:
        print(server)
        listServerStatus = serverStatusMongoDB(server)

        # insere na lista final
        listReturnMongoDB.append(listServerStatus)


    ## chama a funcao para gravar os dados no Sqlite
    gravaDadosSqlite(listReturnMongoDB)

    ## exibe os dados em formato Json
    jsonData = listToJson(listReturnMongoDB)
    print('\n',jsonData)

    # grava final do log
    datahora = obterDataHora()
    msg = '***** List Info ServerStatus MongoDB ***** END: ' + datahora + '\n'
    print(msg)
    gravaLog(msg, 'a')

#inicio da aplicacao
if __name__ == "__main__":
    
    ## chamada da funcao inicial
    main()

