# -*- coding: utf8 -*-
''' Файл с общими установками, распространяется с дистрибутивом '''
UNIT = {'GB': 1048576, 'ГБ': 1048576, 'GByte': 1048576,
        'MB': 1024, 'МБ': 1024, 'MByte': 1024,
        'KB': 1, 'КБ': 1, 'KByte': 1}

#Значения по умолчанию, здесь ничего не меняем, если хотим поменять меняем в mbplugin.ini

# имя ini файла
mbplugin_ini = 'mbplugin.ini'
# Папка для хранения сессий
storefolder = '..\\store'
# Уровень логгирования
logginglevel='INFO'
# Записывать результаты в sqlite БД 0 нет, 1 да
sqlitestore = '0'
# Создавать файлик html отчета, после получения данных
createhtmlreport = '0'
# путь к БД sqlite если нужно поменять - mbplugin.ini Option dbfilename
dbfilename = '..\\BalanceHistory.sqlite'
# путь к html файлу, который создается после получения баланса
balance_html = '..\\DB\\balance.html'
# Количество дней для расчета среднего по истории, если не смогли взять из options.ini
average_days = 30

# порт http сервера с отчетами
port = '8000'
# host '127.0.0.1' - доступ только локально, '0.0.0.0' - разрешить доступ к по сети
host = '127.0.0.1'
# формат вывода по умолчанию
table_format = 'PhoneNumber,Operator,UslugiOn,Balance,RealAverage,BalDelta,BalDeltaQuery,NoChangeDays,CalcTurnOff,SpendMin,SMS,Internet,Minutes,TarifPlan,BlockStatus' # ? UserName
