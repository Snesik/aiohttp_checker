import urllib
import mysql.connector
from utils import read_yaml
from urllib import parse


class Base:
    """Запросы в базу"""
    config = read_yaml('config.yaml')['BD']

    def __init__(self):
        self.host = self.config['host']
        self.login = self.config['login']
        self.passwd = self.config['passwd']
        self.bd = self.config['bd']

    def __enter__(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.login,
                passwd=self.passwd,
                database=self.bd
            )
        except Exception as e:
            print(f"The error '{e}' occurred")
        return self

    def take_in_base(self, choice):
        """Получаем все лоты из базы buy/sell"""
        cur = self.connection.cursor(dictionary=True)
        if choice == 'buy':
            cur.execute('SELECT id_steam, ss as href, buy, sell FROM all_lot '
                        'WHERE bot is not null and status_trade = 1 and status = 0')
        elif choice == 'sell':
            cur.execute('SELECT id_steam, ss as href, buy, sell FROM all_lot '
                        'WHERE status_trade = 3 and status = 0')
        all_lot = [Item(**i) for i in cur.fetchall()]
        cur.close()
        return all_lot

    def update_base(self, data):
        """Обновить базу по id_steam"""
        cur = self.connection.cursor()
        cur.executemany('UPDATE all_lot SET STATUS = 1, nowDate = CURRENT_TIMESTAMP() '
                        'WHERE id_steam = %s', data)
        self.connection.commit()
        print(f'Обновлененно записей: {len(data)}')
        cur.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()


class Item:
    """Класс предмета"""
    def __init__(self, id_steam, href, buy, sell):
        self.id_steam = id_steam
        self.href = href
        self.buy_base = buy
        self.sell_base = sell
        self.buy_steam = None
        self.sell_steam = None
        self.sell_steam_last = None
        self.buy_steam_last = None

    def __str__(self):
        """Возращаем только имя из ссылки"""
        href = self.href.split('/')
        return f'{urllib.parse.unquote(href[6])}'
