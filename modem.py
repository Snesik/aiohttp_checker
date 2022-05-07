import time
from huawei_lte_api.Client import Client
from huawei_lte_api.Connection import Connection


class Modem:
    def __init__(self, config):
        self.login = config['login']
        self.password = config['password']
        self.ip = config['ip']

    def __enter__(self):
        self.connection = Connection(
            f'http://{self.login}:{self.password}@{self.ip}/')
        self.client = Client(self.connection)
        return self

    def rotation(self):
        self.client.net.set_register('1', '25002', '7')
        print('Ротация модема')
        time.sleep(7)

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.connection.close()
