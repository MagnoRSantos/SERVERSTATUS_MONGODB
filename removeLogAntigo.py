# -*- coding: utf-8 -*-

import os, time

## Variaveis
now = time.time()

## Funcao de remocao dos logs
def removeLogs(days, dirlogfile):
    msg = 'Executado a remoção de logs acima de {0} dias do diretório: [{1}]'.format(days, dirlogfile)
    for filename in os.listdir(dirlogfile):
        #print(filename)
        if os.path.getmtime(os.path.join(dirlogfile, filename)) < now - days * 86400:
            if os.path.isfile(os.path.join(dirlogfile, filename)):
                #print(os.path.join(dirlogfile, filename))
                os.remove(os.path.join(dirlogfile, filename))

    return msg
