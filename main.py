import time
import aiohttp
import asyncio
from itertools import islice
from utils import create_connection, sql_select_buy, sql_select_sell, \
    headers, rotation, read_yaml

CONFIG = read_yaml('config.yaml')

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def get_page(session, parsing_adress, id_steam):
    # proxy = 'http://192.168.0.222:5003'
    proxy = 'http://192.168.0.100:5003'
    proxy_auth = aiohttp.BasicAuth('snesik1', 'L!f2y3b4k5')
    async with session.get(parsing_adress, proxy=proxy, proxy_auth=proxy_auth) as s:  #
        if s.status == 200:
            data = await s.json()
            if data['success'] == 1:
                await ss(data, id_steam)


async def ss(data, id_steam):
    if not data['buy_order_graph']:
        result_bd[id_steam]['buy_steam'] = 0
    else:
        result_bd[id_steam]['buy_steam'] = data['buy_order_graph'][0][0]
        if len(data['buy_order_graph']) >= 2:
            result_bd[id_steam]['buy_steam_last'] = data['buy_order_graph'][1][0]
        else:
            result_bd[id_steam]['buy_steam_last'] = 0

    if not data['sell_order_graph']:
        result_bd[id_steam]['sell_steam'] = 0
    else:
        result_bd[id_steam]['sell_steam'] = data['sell_order_graph'][0][0]
        if len(data['sell_order_graph']) >= 2:
            result_bd[id_steam]['sell_steam_last'] = data['sell_order_graph'][1][0]
        else:
            result_bd[id_steam]['sell_steam_last'] = 0


async def get_all(session, in_base_item):
    tasks = []
    for id_steam, info in in_base_item.items():
        parsing_adress = f'https://steamcommunity.com/market/itemordershistogram?country=RU&' \
                         f'language=russian&currency=5&item_nameid={id_steam}&two_factor=0&format=json'
        task = asyncio.create_task(get_page(session, parsing_adress, id_steam))
        tasks.append(task)
    await asyncio.gather(*tasks)


async def main(in_base_item):
    # connector = aiohttp.TCPConnector(force_close=True)
    # connector = aiohttp.TCPConnector(force_close=True, limit=100, limit_per_host=100)
    async with aiohttp.ClientSession() as session:  # connector=connector
        session.header = headers
        await get_all(session, in_base_item)


def compare(in_base_item, buy_or_sell):
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


def request_in_base(buy_or_sell):
    in_base_item = {}
    mydb = create_connection(**CONFIG['BD'])
    mycursor = mydb.cursor(dictionary=True)
    if buy_or_sell == 'buy':
        mycursor.execute(sql_select_buy)

    elif buy_or_sell == 'sell':
        mycursor.execute(sql_select_sell)

    for i in mycursor.fetchall():
        in_base_item[i['id_steam']] = {'buy': i['buy'], 'sell': i['sell'], 'ss': i['ss']}
    mydb.close()
    return in_base_item


def add_in_base(id_steam):
    a = [(i,) for i in id_steam]
    print(len(a))
    mydb = create_connection(**CONFIG['BD'])
    mycursor = mydb.cursor()
    mycursor.executemany(f"""UPDATE all_lot SET STATUS = 1, nowDate = CURRENT_TIMESTAMP() WHERE id_steam = %s""", a)
    mydb.commit()
    mydb.close()


def chunks(data, SIZE=4000):
    it = iter(data)
    for i in range(0, len(data), SIZE):
        yield {k: data[k] for k in islice(it, SIZE)}


def take_items():
    get_item_info = {}
    # how_mach = 0
    # how_mach_once = math.ceil(len(result_bd) / 4000)
    for item in chunks(result_bd, 4000):
        # for i in item:
        #     get_item_info[i] = item[i]
        asyncio.run(main(item))
        rotation()



while True:
    result_bd = request_in_base('buy')
    take_items()

    result_compare = compare(result_bd, 'buy')
    add_in_base(result_compare)

    result_bd = request_in_base('sell')

    asyncio.run(main(result_bd))

    result_compare = compare(result_bd, 'sell')
    add_in_base(result_compare)
