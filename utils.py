import yaml
import urllib.parse
from itertools import islice


def read_yaml(path: str):
    """Загрузить из yaml"""
    with open(path, 'r') as c:
        return yaml.safe_load(c)


def chunks(data: list, size: int):
    """Разделения списка на части"""
    it = iter(data)
    for i in range(0, len(data), size):
        yield {k for k in islice(it, size)}


"""Заголовок для запросов"""
headers = ({'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Host': 'steamcommunity.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache'})
