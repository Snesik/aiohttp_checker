import time
from huawei_lte_api.Client import Client
from huawei_lte_api.Connection import Connection
from utils import read_yaml


class Modem:
    """Класс для работы с модемом"""
    config = read_yaml('config.yaml')['Modem']

    def __init__(self):
        self.login = self.config['login']
        self.password = self.config['password']
        self.ip = self.config['ip']

    def __enter__(self):
        self.connection = Connection(
            f'http://{self.login}:{self.password}@{self.ip}/')
        self.client = Client(self.connection)
        return self

    def rotation(self):
        try:
            self.client.net.set_register('1', '25002', '7')
            print('Ротация модема')
            time.sleep(7)
        except:
            self.client.device.reboot()
            time.sleep(60)
            self.client.net.set_register('1', '25002', '7')
            print('Ротация модема, была ошибкаб перезагрузил модем')

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.connection.close()
