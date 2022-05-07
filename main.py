import time
import os
import colorama as color
import aiohttp
import asyncio
from itertools import islice
from models import Base
from utils import create_connection, sql_select_buy, sql_select_sell, \
    headers, read_yaml
from modem import Modem
from tqdm import tqdm

CONFIG = read_yaml('config.yaml')

sql_select_buy1 = 'SELECT id_steam, buy, sell, ss FROM all_lot ' \
                 'WHERE bot is not null and status_trade = 1 and status = 0 limit 10000'


# with Base(CONFIG['BD']) as a:
#      bbb = a.take_in_base('buy')
# print()
# for i in tqdm(bbb, desc='Считаем', colour='green'):
#     time.sleep(0.5)
#     bb = 'ss'


asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def get_page(session, parsing_adress, item):
    # proxy = 'http://192.168.0.222:5003'
    proxy = 'http://192.168.0.100:5003'
    proxy_auth = aiohttp.BasicAuth('snesik1', 'L!f2y3b4k5')
    #try:
    async with session.get(parsing_adress, proxy=proxy, proxy_auth=proxy_auth) as s:  #
        if s.status == 200:
            data = await s.json()
            if data['success'] == 1:
                #await ss(data, item)
                return await ss(data, item)
    # except:
    #     print(item)
async def ss(data, item):
    if not data['buy_order_graph']:
        item.buy_steam = 0
    else:
        item.buy_steam = data['buy_order_graph'][0][0]
        if len(data['buy_order_graph']) >= 2:
            item.buy_steam_lats = data['buy_order_graph'][1][0]
        else:
            item.buy_steam_lats = 0

    if not data['sell_order_graph']:
        item.sell_steam = 0
    else:
        item.sell_steam = data['sell_order_graph'][0][0]
        if len(data['sell_order_graph']) >= 2:
            item.sell_steam_last = data['sell_order_graph'][1][0]
        else:
            item.sell_steam_last = 0
    return item

async def get_all(session, in_base_item):
    tasks = []
    for item in in_base_item:
        parsing_adress = f'https://steamcommunity.com/market/itemordershistogram?country=RU&' \
                         f'language=russian&currency=5&item_nameid={item.id_steam}&two_factor=0&format=json'
        task = asyncio.create_task(get_page(session, parsing_adress, item))
        tasks.append(task)
    return await asyncio.gather(*tasks)


async def main(in_base_item):
    # connector = aiohttp.TCPConnector(force_close=True)
    # connector = aiohttp.TCPConnector(force_close=True, limit=100, limit_per_host=100)
    async with aiohttp.ClientSession() as session:  # connector=connector
        session.header = headers
        return await get_all(session, in_base_item)


def compare(in_base_item, buy_or_sell):
    if cho
    a = [i for i in in_base_item if not i.buy_base or not i.buy_steam or not i.buy_steam_lats]
    b = [i for i in in_base_item if i.buy_base != i.buy_steam or i.buy_steam - 0.05 > i.buy_steam_lats]
    we_give_status_1 = []
    if buy_or_sell == 'buy':
        for key, values in in_base_item.items():
            if in_base_item[key].get('buy_steam', None) == None:
                continue
            elif values['buy'] != values['buy_steam']:
                we_give_status_1.append(key, )
            if in_base_item[key].get('buy_steam_last', None) == None:
                continue
            elif values['buy'] - 0.05 > values['buy_steam_last'] and values['buy_steam_last'] != 0:
                we_give_status_1.append(key, )
            elif values['buy_steam'] == 0:
                we_give_status_1.append(key, )


    elif buy_or_sell == 'sell':
        for key, values in in_base_item.items():
            if in_base_item[key].get('sell_steam', None) == None:
                continue
            elif values['sell'] != values['sell_steam']:
                we_give_status_1.append(key, )
            if in_base_item[key].get('sell_steam_last', None) == None:
                continue
            elif values['sell'] + 0.05 < values['sell_steam_last'] != 0:
                we_give_status_1.append(key, )
            elif values['sell_steam'] == 0:
                we_give_status_1.append(key, )
    return we_give_status_1


# def request_in_base(buy_or_sell):
#     in_base_item = {}
#     mydb = create_connection(**CONFIG['BD'])
#     mycursor = mydb.cursor(dictionary=True)
#     if buy_or_sell == 'buy':
#         mycursor.execute(sql_select_buy)
#
#     elif buy_or_sell == 'sell':
#         mycursor.execute(sql_select_sell)
#
#     for i in mycursor.fetchall():
#         in_base_item[i['id_steam']] = {'buy': i['buy'], 'sell': i['sell'], 'ss': i['ss']}
#     mydb.close()
#     return in_base_item


# def add_in_base(id_steam):
#     a = [(i,) for i in id_steam]
#     print(len(a))
#     mydb = create_connection(**CONFIG['BD'])
#     mycursor = mydb.cursor()
#     mycursor.executemany(f"""UPDATE all_lot SET STATUS = 1, nowDate = CURRENT_TIMESTAMP() WHERE id_steam = %s""", a)
#     mydb.commit()
#     mydb.close()


def chunks(data, SIZE=4000):
    it = iter(data)
    for i in range(0, len(data), SIZE):
        yield {k for k in islice(it, SIZE)}


def take_items():
    get_item_info = {}
    # how_mach = 0
    # how_mach_once = math.ceil(len(result_bd) / 4000)
    for item in chunks(result_bd, 4000):
        # for i in item:
        #     get_item_info[i] = item[i]
        asyncio.run(main(item))
        with Modem(CONFIG['Modem']) as client:
            client.rotation()



while True:



    with Base(CONFIG['BD']) as bd:
        all_buy_bd = bd.take_in_base('buy')


    all_result = []
    for item in tqdm(chunks(all_buy_bd, 3000), ascii='_$', colour='green'):
        all_result += asyncio.run(main(item))
        print(f'Запросов сделали: {len(all_result)}')
        with Modem(CONFIG['Modem']) as m:
            m.rotation()

    a = compare(all_result, 'buy')
    print()
    result_bd = request_in_base('buy')
    take_items()

    result_compare = compare(result_bd, 'buy')
    add_in_base(result_compare)

    result_bd = request_in_base('sell')
    asyncio.run(main(result_bd))

    result_compare = compare(result_bd, 'sell')
    add_in_base(result_compare)
