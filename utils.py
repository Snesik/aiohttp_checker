
import yaml
import mysql.connector
import urllib


def read_yaml(path: str):
    with open(path, 'r') as c:
        return yaml.safe_load(c)

def bild_hash_name_apid_game(ss):
    ss = ss.split('/')
    hash_name = urllib.parse.unquote(ss[6])
    #appid_game = ss[5]
    return hash_name

def create_connection(host, login, passwd, bd):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host,
            user=login,
            passwd=passwd,
            database=bd
        )
    except Exception as e:
        print(f"The error '{e}' occurred")
    return connection


headers = ({'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Host': 'steamcommunity.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache'})

sql_select_buy = 'SELECT id_steam, buy, sell, ss FROM all_lot ' \
                 'WHERE bot is not null and status_trade = 1 and status = 0 limit 10000'
sql_select_sell = 'SELECT id_steam, buy, sell, ss FROM all_lot WHERE status_trade = 3 and status in (0)'
sql_update_buy = "UPDATE all_lot SET STATUS = %s, nowDate = CURRENT_TIMESTAMP() WHERE ss = %s"



