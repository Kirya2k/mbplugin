# -*- coding: utf8 -*-
'Модуль для хранения сессий и настроек а также чтения настроек из ini от MobileBalance'
import os, sys, time, io, re, json, pickle, requests, configparser, pprint, zipfile, logging
import settings


def session_folder(storename):
    storefolder = options('storefolder')     
    os.path.join(storefolder, storename)

class Session():
    'Класс для сессии с дополнительными фишками для сохранения и проверки'
    def __init__(self, storename, headers=None):
        self.storename = storename
        self.storefolder = options('storefolder')
        self.pagecounter = 1  # Счетчик страниц для сохранения
        self.json_response = {}  # Сохраняем json ответы
        self.headers = headers
        try:
            with open(os.path.join(self.storefolder, self.storename), 'rb') as f:
                self.session = pickle.load(f)
                self.headers = self.session.headers
        except Exception:
            self.session = requests.Session()
            if self.headers:
                self.session.headers.update(self.headers)

    def update_headers(self, headers):
        self.headers.update(headers)
        self.session.headers.update(self.headers)

    def drop_and_create(self, headers=None):
        'удаляем сессию и создаем новую'
        try:
            os.remove(os.path.join(self.storefolder, self.storename))
        except Exception:
            pass
        self.session = requests.Session()
        if headers:
            self.headers = headers
        if self.headers:
            self.session.headers.update(self.headers)

    def save_session(self):
        'Сохраняем сессию в файл'
        with open(os.path.join(self.storefolder, self.storename), 'wb') as f:
            pickle.dump(self.session, f)

    def save_response(self, url, response):
        'debug save response'
        # Сохраняем по старинке в режиме DEBUG каждую страницу в один файл
        if not hasattr(response, 'content'):
            return
        if options('logginglevel') == 'DEBUG':
            fld = options('loggingfolder')
            fn = os.path.join(fld, f'{self.storename}_{self.pagecounter}.html')
            open(fn, mode='wb').write(response.content)
        # Новый вариант сохранения - все json в один файл
        if options('logginglevel') == 'DEBUG' or str(options('log_responses')) == '1':
            try:
                js = response.json()
                self.json_response[f'{url}_{self.pagecounter}'] = js
                text = '\n\n'.join([f'{k}\n{pprint.PrettyPrinter(indent=4).pformat(v)}' for k, v in self.json_response.items()])
                open(os.path.join(options('loggingfolder'), self.storename + '.log'), 'w', encoding='utf8', errors='ignore').write(text)
            except Exception:
                pass
        self.pagecounter += 1

    def get(self, url, **kwargs):
        response = self.session.get(url, **kwargs)
        self.save_response(url, response)
        return response
        
    def post(self, url, data=None, json=None, **kwargs):
        response = self.session.post(url, data, json, **kwargs)
        self.save_response(url, response)
        return response

    def put(self, url, data=None, **kwargs):
        response = self.session.put(url, data, **kwargs)
        self.save_response(url, response)
        return response


def options(param, default=None, section='Options', listparam=False, mainparams={}):
    'Читаем параметр из mbplugin.ini либо дефолт из settings'
    'Если listparam=True, то читаем список из всех, что начинается на param'
    'mainparams - перекрывает любые другие варианты, если в нем присутствует - берем его'
    if param in mainparams and listparam == False:
        return mainparams[param]
    if default is None:
        default = settings.ini[section].get(param.lower(), None)
    options_all_sec = ini().read()
    if section in options_all_sec:
        options_sec = options_all_sec[section]
    else:
        options_sec = {}
    if listparam:
        return [v for k,v in options_sec.items() if k.startswith(param)]
    else:
        return options_sec.get(param, default)
    
class ini():
    def __init__(self, fn=settings.mbplugin_ini):
        'файл mbplugin.ini ищем в вышележащих папках либо в settings.mbplugin_root_path если он не пустой'
        'остальные ini ищем в пути прописанном в mbplugin.ini\\MobileBalance\\path'
        self.ini = configparser.ConfigParser()
        self.fn = fn
        if self.fn.lower() == settings.mbplugin_ini:
            self.inipath = self.find_files_up(self.fn)        
        else:
            path = ini(settings.mbplugin_ini).read()['MobileBalance']['path']
            self.inipath = os.path.join(path, fn)
            
    def find_files_up(self, fn):
        'Ищем файл вверх по дереву путей'
        'Для тестов можно явно указать папку с mbplugin.ini в settings.mbplugin_root_path '
        if hasattr(settings,'mbplugin_root_path') and settings.mbplugin_root_path != '':
            return os.path.abspath(os.path.join(settings.mbplugin_root_path, fn))
        allroot = [os.getcwd().rsplit(os.path.sep, i)[0] for i in range(len(os.getcwd().split(os.path.sep)))]
        all_ini = [i for i in allroot if os.path.exists(os.path.join(i, fn))]
        if all_ini != []:
            return os.path.join(all_ini[0], fn)
        else:
            return os.path.join('..', fn)
        
    def read(self):
        'Читаем ini из файла'
        'phones.ini и phones_add.ini- нечестный ini читать приходится с извратами'
        'replace [Phone] #123 -> [123]'
        'Для чтения phones.ini с добавлением данных из phones_add.ini см метод ini.phones'
        if os.path.exists(self.inipath):
            if self.fn.lower() == 'phones.ini' or self.fn.lower() == 'phones_add.ini':
                with open(self.inipath) as f_ini:
                    prep1 = re.sub(r'(?usi)\[Phone\] #(\d+)', r'[\1]', f_ini.read())
                # TODO костыль N1, мы подменяем p_pluginLH на p_plugin чтобы при переключении плагина не разъезжались данные
                prep2 = re.sub(r'(?usi)(Region\s*=\s*p_\S+)LH', r'\1', prep1)
                # TODO костыль N2, у Number то что идет в конце вида <пробел>#<цифры> это не относиться к логину а 
                # сделано для уникальности логинов - выкидываем, оно нас только сбивает - мы работаем по паре Region_Number
                prep3 = re.sub(r'(?usi)(Number\s*=\s*\S+) #\d+', r'\1', prep2)
                self.ini.read_string(prep3)
            else:
                self.ini.read(self.inipath)
        elif not os.path.exists(self.inipath) and self.fn.lower() == settings.mbplugin_ini:
            self.create()
            self.write()
        elif not os.path.exists(self.inipath) and self.fn.lower() == 'phones_add.ini':
            self.ini.read_string('')  # Если нет - тихо вернем пустой
        else:
            raise RuntimeError(f'Not found {self.fn}')
        return self.ini

    def create(self):
        'Только создаем в памяти, но не записываем'
        # Создаем mbplugin.ini - он нам нужен для настроек и чтобы знать где ini-шники от mobilebalance
        mbpath = self.find_files_up('phones.ini')
        if os.path.exists(mbpath):
            # Если нашли mobilebalance - cоздадим mbplugin.ini и sqlite базу там же где и ini-шники mobilebalance
            self.inipath = os.path.join(os.path.split(mbpath)[0], self.fn)
            dbpath = os.path.abspath(os.path.join(os.path.split(mbpath)[0], os.path.split(settings.ini['Options']['dbfilename'])[1]))
        else:
            # иначе создадим mbplugin.ini и базу в корне папки mbplugin
            self.ini['MobileBalance'] = {'path': ''}
            dbpath = settings.ini['Options']['dbfilename']
        self.ini['MobileBalance'] = {'path': os.path.split(mbpath)[0]}
        # self.ini.update(settings.ini) # TODO in future
        self.ini['MobileBalance'] = {'path': os.path.split(mbpath)[0]}
        self.ini['Options'] = {'logginglevel': settings.ini['Options']['logginglevel'],
                          'sqlitestore': settings.ini['Options']['sqlitestore'],
                          'dbfilename': dbpath,
                          'createhtmlreport': settings.ini['Options']['createhtmlreport'],
                          'balance_html': os.path.abspath(settings.ini['Options']['balance_html']),
                          'updatefrommdb': settings.ini['Options']['updatefrommdb'],
                          'updatefrommdbdeep': settings.ini['Options']['updatefrommdbdeep'],
                          }
        self.ini['HttpServer'] = {'port': settings.ini['HttpServer']['port'],
                             'host': settings.ini['HttpServer']['host'],
                             'table_format': settings.ini['HttpServer']['table_format']
                             }    

    def save_bak(self):
        'Сохраняем резервную копию файла в папку с логами в zip'
        if not os.path.exists(self.inipath): # Сохраняем bak, только если файл есть
            return
        # Делаем резервную копию ini перед сохранением
        undozipname = os.path.join(options('storefolder'), 'mbplugin.ini.bak.zip')
        arc = []
        if os.path.exists(undozipname):
            # Предварительно читаем сохраненные варианты, открываем на чтение
            with zipfile.ZipFile(undozipname, 'r', zipfile.ZIP_DEFLATED) as zf1:
                for i in zf1.infolist(): # Во временную переменную прочитали
                    arc.append((i, zf1.read(i)))
        arc = sorted(arc, reverse=True, key=lambda i: i[0].filename)[0:int(options('httpconfigeditundo'))]
        name_bak = f'{os.path.split(self.inipath)[-1]}_{time.strftime("%Y%m%d%H%M%S", time.localtime())}'
        # Если быстро менять конфиг - то успеваем в одну секунду сохранить несколько раз - это лишнее
        # Если в эту секунду уже сохраняли - пропускаем
        if name_bak in [i[0].filename for i in arc]:
            print('We create undo too often - lets skip this one')
            return
        with zipfile.ZipFile(undozipname+'~tmp', 'w', zipfile.ZIP_DEFLATED) as zf2:
            # Sic! Для write write(filename, arcname) vs writestr(arcname, data)
            zf2.write(self.inipath, f'{name_bak}')
            for a_name, a_data in arc:
                zf2.writestr(a_name, a_data)
        if os.path.exists(undozipname):
            os.remove(undozipname)  # Удаляем первоначальный файл
        os.rename(undozipname+"~tmp", undozipname) # Переименовываем временный на место первоначального

    def write(self):
        'Сохраняем только mbplugin.ini для остальных - игнорим'
        if self.fn.lower() != settings.mbplugin_ini:
            return  # only mbplugin.ini
        sf = io.StringIO()
        self.ini.write(sf)
        raw = sf.getvalue().splitlines()  # инишник без комментариев
        if os.path.exists(self.inipath):  # Если файл ini на диске есть сверяем с предыдущей версией
            self.save_bak()
            # TODO если сохраняем коменты:
            with open(self.inipath, encoding='cp1251') as f_ini_r:
                for num,line in enumerate(f_ini_r.read().splitlines()):
                    if line.startswith(';'):
                        raw.insert(num, line)
        with open(self.inipath, encoding='cp1251', mode='w') as f_ini_w:
            f_ini_w.write('\n'.join(raw))
        # TODO Если просто сохраняем то так
        # self.ini.write(open(self.inipath, 'w'))

    def ini_to_json(self):
        'Преобразуем ini в js для редактора editcfg'
        result = {}
        for sec in self.ini.values():
            if sec.name != 'DEFAULT':
                # Кидаем ключи из ini после Добавляем дефолтные ключи из settings если их не было в ini
                # TODO продумать, может их помечать цветом и сделать кнопку вернуть к дефолту, т.е. удалить ключ из ini
                for key,val in list(sec.items()) + list(settings.ini.get(sec.name, {}).items()):
                    if key.endswith('_'):
                        continue
                    param = settings.ini.get(sec.name, {}).get(key+'_', {})
                    param = {k:v for k,v in param.items() if k not in ['validate']}
                    line = {'section': sec.name, 'id': key, 'type': 'text', 'descr': f'DESC {sec.name}_{key}', 
                            'value': val, 'default': key not in sec, 'default_val': settings.ini.get(sec.name, {}).get(key, None)}
                    line.update(param)
                    if f'{sec.name}_{key}' not in result:
                        result[f'{sec.name}_{key}'] = line
        return json.dumps(result, ensure_ascii=False)

    def phones(self):
        'Читает phones.ini добавляет данные из phones_add.ini дополнительную инфу'
        'И возвращает словарь с ключами в виде пары вида (number,region)'
        if self.fn.lower() != 'phones.ini':
            raise RuntimeError(f'{self.fn} is not phones.ini')
        # Читаем вспомогательный phones_add.ini - из него возьмем данные если они там есть, они перекроют данные в phones.ini
        phones_add = ini('phones_add.ini').read()
        data = {}
        for secnum,el in self.read().items():
            if secnum.isnumeric() and 'Monitor' in el:
                key = (re.sub(r' #\d+','',el['Number']),el['Region'])
                data[key] = {}
                data[key]['NN'] = int(secnum)
                data[key]['Alias'] = el.get('Alias','')
                data[key]['Region'] = el.get('Region','')
                data[key]['Number'] = el.get('Number','')
                data[key]['PhoneDescription'] = el.get('PhoneDescription','')
                data[key]['Monitor'] = el.get('Monitor','')
                data[key]['BalanceLessThen'] = float(el.get('BalanceLessThen', options('BalanceLessThen')))
                data[key]['TurnOffLessThen'] = int(el.get('TurnOffLessThen', options('TurnOffLessThen')))
                data[key]['BalanceNotChangedMoreThen'] = int(el.get('BalanceNotChangedMoreThen', options('BalanceNotChangedMoreThen')))
                data[key]['BalanceChangedLessThen'] = int(el.get('BalanceChangedLessThen', options('BalanceChangedLessThen')))
                data[key]['Password2'] = el.get('Password2','')
                if secnum in phones_add:
                    try:
                        # Проблема - configparser возвращает ключи в lowercase - так что приходится перебирать 
                        # ключи чтобы не оказалось два одинаковых ключа с разным кейсом
                        for k in data[key].keys():
                            if k in phones_add[secnum]:
                                data[key][k] = phones_add[secnum][k]
                    except Exception:
                        raise RuntimeError(f'Parse phones_add.ini error in section{secnum}')
        return data


def read_stocks(stocks_name):
    'Читаем список стоков для плагина stock.py из mbplugin.ini'
    ini_all_sec = ini().read()
    if 'stocks_'+stocks_name not in ini_all_sec:
        raise RuntimeError(f'section {"stocks_"+stocks_name} not in mbplugin.ini')
    stock_sec_ini = ini_all_sec['stocks_'+stocks_name]
    stocks = {'stocks': [], 'remain': {}, 'currenc': ''}
    items = stock_sec_ini.items()
    stocks_str = [list(map(str.strip, v.split(','))) for k, v in items if k.startswith('stock')]
    remain_str = [list(map(str.strip, v.split(','))) for k, v in items if k.startswith('remain')]
    stocks['currenc'] = stock_sec_ini['currenc'].strip()
    stocks['stocks'] = [(i[0].upper(), int(i[1]), i[2].upper()) for i in stocks_str if len(i) == 3 and i[1].isnumeric()]
    stocks['remain'] = {i[0].upper(): int(i[1]) for i in remain_str if len(i) == 2 and i[1].isnumeric()}
    return stocks


def result_to_xml(result):
    'Конвертирует словарь результатов в готовый к отдаче вид '
    # Коррекция SMS и Min (должны быть integer)
    if 'SMS' in result:
        result['SMS'] = int(result['SMS'])
    if 'Min' in result:
        result['Min'] = int(result['Min'])
    for k, v in result.items():
        if type(v) == float:
            result[k] = round(v, 2)  # Чтобы не было паразитных микрокопеек
    body = ''.join([f'<{k}>{v}</{k}>' for k, v in result.items()])
    return f'<Response>{body}</Response>'


def result_to_html(result):
    'Конвертирует словарь результатов в готовый к отдаче вид '
    # Коррекция SMS и Min (должны быть integer)
    if 'SMS' in result:
        result['SMS'] = int(result['SMS'])
    if 'Min' in result:
        result['Min'] = int(result['Min'])
    body = json.dumps(result, ensure_ascii=False)
    return f'<html><meta charset="windows-1251"><p id=response>{body}</p></html>'    


def logging_restart():
    'Останавливаем логирование и откидываем в отдельный файл'
    'Чтобы можно было почистить'
    filename = options('logginghttpfilename')
    filename_new = filename + time.strftime('%Y%m%d%H%M%S.log',time.localtime())
    logging.shutdown()
    os.rename(filename, filename_new)
    logging.info(f'Old log was renamed to {filename_new}')


if __name__ == '__main__':
    print('Module store')
    # print(list(ini('phones.ini').read().keys()))
    # print(list(ini('options.ini').read().keys()))
    # print(list(ini('mbplugin.ini').read().keys()))

    #ini = ini().read()
    #if ini['MobileBalance']['path'] == '':
    #    print('MobileBalance folder unknown')
    #print(list(ini('phones.ini').read().keys()))

    #stocks_name = 'broker_ru'
    #print(read_stocks(stocks_name))

    # import io;f = io.StringIO();ini.write(f);print(f.getvalue())
    #{'STOCKS':(('AAPL',1,'Y'),('TATNP',16,'M'),('FXIT',1,'M')), 'REMAIN': {'USD':5, 'RUB':536}, 'CURRENC': 'USD'}
    #p=ini('phones.ini').read()
    # import store;ini=store.ini();ini.read();ini.ini['Options']['httpconfigedit']='1';ini.write()