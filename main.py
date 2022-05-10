import os
import time
import datetime
import aiohttp
import asyncio
from models import Base
from utils import headers, chunks
from modem import Modem
from tqdm import tqdm

#asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def get_page(session, parsing_adress, item):
    proxy = 'http://192.168.0.222:5003'
     #proxy = 'http://192.168.0.100:5003'
    proxy_auth = aiohttp.BasicAuth('snesik1', 'L!f2y3b4k5')
    async with session.get(parsing_adress, proxy=proxy, proxy_auth=proxy_auth) as s:  #
        if s.status == 200:
            data = await s.json()
            if data['success'] == 1:
                return await ss(data, item)


async def ss(data, item):
    if not data['buy_order_graph']:
        item.buy_steam = 0
    else:
        item.buy_steam = data['buy_order_graph'][0][0]
        if len(data['buy_order_graph']) >= 2:
            item.buy_steam_last = data['buy_order_graph'][1][0]
        else:
            item.buy_steam_last = 0

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
    # connector = aiohttp.TCPConnector(force_close=True, limit=100, limit_per_host=100)
    async with aiohttp.ClientSession() as session:  # connector=connector
        session.header = headers
        return await get_all(session, in_base_item)


def compare(data, choice):
    update = []
    data = [i for i in data if i is not None]
    if choice == 'buy':
        for item in tqdm(data, ascii='_$', colour='green', desc='Ищем перебитые, завышеные лоты', ncols=200):
            if not item.buy_base:
                continue
            elif item.buy_base != item.buy_steam:
                update.append(item.id_steam, )
            elif not item.buy_steam_last:
                continue
            elif item.buy_steam - 0.05 > item.buy_steam_last != 0:
                update.append(item.id_steam, )
            elif item.buy_steam == 0:
                update.append(item.id_steam, )
    elif choice == 'sell':
        for item in tqdm(data, ascii='_$', colour='green', desc='Ищем перебитые, завышеные лоты', ncols=200):
            if not item.sell_base:
                continue
            elif item.sell_base != item.sell_steam:
                update.append(item.id_steam, )
            elif not item.sell_steam_last:
                continue
            elif item.sell_steam + 0.05 < item.sell_steam_last != 0:
                update.append(item.id_steam, )
            elif item.sell_steam == 0:
                update.append(item.id_steam, )
    print(datetime.datetime.now(), '\nНайдено: ', len(update))
    return [(i,) for i in update]


if __name__ == "__main__":

    with Modem() as m:
        m.rotation()

    while True:
        try:
            #os.system('clear')
            start_time = time.time()

            all_result = []
            with Base() as bd:
                all_buy_bd = bd.take_in_base('buy')
            for item in chunks(all_buy_bd, size=3000):
                all_result += asyncio.run(main(item))
                print(datetime.datetime.now(), f'Запросов сделали, Покупки: {len(all_result)}')
                with Modem() as m:
                    m.rotation()
            data = compare(all_result, 'buy')
            with Base() as bd:
                bd.update_base(data)

            all_result = []
            with Base() as bd:
                all_sell_bd = bd.take_in_base('sell')
            for item in chunks(all_sell_bd, size=3000):
                all_result += asyncio.run(main(item))
                print(datetime.datetime.now(), f'Запросов сделали, Продажи: {len(all_result)}')
                with Modem() as m:
                    m.rotation()
            data = compare(all_result, 'sell')
            with Base() as bd:
                bd.update_base(data)

            print("--- %s seconds ---" % (time.time() - start_time))
        except:
            time.sleep(60)
            with Modem() as m:
                m.rotation()