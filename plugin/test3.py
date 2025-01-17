#!/usr/bin/python3
# -*- coding: utf8 -*-
import pyppeteeradd as pa

login_url = 'https://lk.saures.ru/dashboard'
user_selectors = {'chk_lk_page_js': "document.querySelector('form input[type=password]') == null",
                  'chk_login_page_js': "document.querySelector('form input[type=password]') !== null",
                  'login_clear_js': "document.querySelector('form input[type=text]').value=''",
                  'login_selector': 'form input[type=text]', }

# введите логин demo@saures.ru и пароль demo вручную
class test3_over_puppeteer(pa.balance_over_puppeteer):
    def data_collector(self):
        self.do_logon(url=login_url, user_selectors=user_selectors)
        # Здесь мы берет данные непосредственно с отрендеренной страницы, поэтому url_tag не указан
        self.wait_params(params=[{
            'name': 'Balance',
            'jsformula': r"parseFloat(document.querySelector('div.card-body div.counter__row').innerText.replace(/[^\d,.-]/g, '').replace(',','.'))",
        }, {
            'name': 'BlockStatus',
            'jsformula': r"document.querySelector('div.devices p.small').innerText",
        }])


def get_balance(login, password, storename=None):
    ''' На вход логин и пароль, на выходе словарь с результатами '''
    return test3_over_puppeteer(login, password, storename).main()


if __name__ == '__main__':
    print('This is module test3 for test chrome on puppeteer with class balance_over_puppeteer')
