import netifaces as ni
import requests
import os

WLC50 = "WLC-HW-50"
WLC100 = "WLC-HW-100"


# ВЫБОР МОДЕЛИ СЕРВЕРА


class Server:
    def __init__(self, model):
        self.model = model
        self.ram_max = None
        self.ram_min = None
        self.cpu = None
        self.storage = None
        self.ram_default = None

    def set_params(self, model):
        if model == WLC50:
            self.ram_min = 15000
            self.ram_max = 17000
            self.cpu = 4
            self.storage = 500
            self.ram_default = 16000
        elif model == WLC100:
            self.ram_min = 23000
            self.ram_max = 25000
            self.cpu = 6
            self.storage = 1000
            self.ram_default = 24000

    def get_opposite(self):
        if self.model == WLC50:
            return WLC100
        elif self.model == WLC100:
            return WLC50


def choose_server():
    print("Необходимо выбрать номер модели сервера для проверки:")
    print("1. WLC-HW-50")
    print("2. WLC-HW-100")
    model = int(input())
    return WLC50 if model == 1 else WLC100


# ПРОВЕРКА ТЕХ.ХАРАКТЕРИСТИК СЕРВЕРА
def check_server_params(server_model):
    ram = int(os.popen("free | grep Mem | awk '{print int($2 / 1000)}'").read())
    cpu = os.cpu_count()
    storage = int((os.popen("parted -l | grep nvme0n1 | awk '{print $3}'").read())[:-3].split('.')[0])
    errors = 0
    if server.ram_min <= ram <= server.ram_max:
        print("Характеристики оперативной памяти в норме.")
    elif server_opposite.ram_min <= ram <= server_opposite.ram_max:
        print("\033[0;31m!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\033[0m")
        print("\033[0;31mВНИМАНИЕ! У ВАС НАХОДИТСЯ НЕ СЕРВЕР {}! ИЗМЕНИТЕ НАКЛЕЙКУ НА {}!\033[0m".format(
            server_model.model, server_model.get_opposite()))
        print("\033[0;31m!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\033[0m")
        exit()
    else:
        print(
            "\033[0;31mВНИМАНИЕ! Установлено {}Гб памяти, несоответствие характеристиркам модели! Необходимо - {}Гб\033[0m".format(
                (ram // 1000), (server_model.ram_default // 1000)))
        errors += 1
    if cpu < server.cpu:
        print(
            "\033[0;31mВНИМАНИЕ! Установлено {} ядра процессора, несоответствие характеристикам модели! Необходимо - {} ядра\033[0m".format(
                cpu, server_model.cpu))
        errors += 1
    if storage < server.storage:
        print(
            "\033[0;31mВНИМАНИЕ! Установлен накопитель емкостью {}Гб, несоответствие характеристикам модели! Необходимо не менее {}Гб\033[0m".format(
                storage, server_model.storage))
        errors += 1
    if errors != 0:
        print(
            "\033[0;31mВНИМАНИЕ! Установлены неверные комплектующие! Пожалуйста, замените их на требуемые согласно заявленным техническим характеристикам!\033[0m")
        exit()


# ПРОВЕРКА СОЕДИНЕНИЯ ЛК, КП, EMS
def check_connection():
    if len(ni.interfaces()) < 2:
        print("\033[0;31mВНИМАНИЕ! Отсутствует сетевой адаптер!\033[0m")
        exit()
    ip = 'localhost'
    print('Проверка соединения ЛК, КП, EMS\n')

    try:
        r = requests.get('http://{}:8080/wifi-cab'.format(ip))
        if r.status_code == 200:
            print('Личный кабинет успешно запущен!')
    except:
        print("\033[0;31mВНИМАНИЕ! Ошибка при соединении с личным кабинетом!\033[0m")

    try:
        r = requests.get('http://{}:8080/epadmin'.format(ip))
        if r.status_code == 200:
            print('Конструктор порталов успешно запущен!')
    except:
        print("\033[0;31mВНИМАНИЕ! Ошибка при соединении с конструктором порталов!\033[0m")

    try:
        r = requests.get('http://{}:8080/ems/jws'.format(ip))
        if r.status_code == 200:
            print('EMS успешно запущен!\n')
    except:
        print("\033[0;31mВНИМАНИЕ! Ошибка при соединении с EMS!\033[0m\n")


# ПРОВЕРКА РАБОТЫ СЕРВИСОВ
def check_services():
    errors = 0
    print("Проверка работы сервисов")
    services = (
        'eltex-airtune',
        'eltex-apb',
        'eltex-bruce',
        'eltex-disconnect-service',
        'eltex-ems',
        'eltex-jobs',
        'eltex-johnny',
        'eltex-logging-service',
        'eltex-mercury',
        'eltex-ngw',
        'eltex-pcrf',
        'eltex-portal',
        'eltex-portal-constructor',
        'eltex-radius',
        'eltex-wifi-cab'
    )
    for servs in services:
        if os.popen('systemctl show -p SubState --value {}'.format(servs)).read() != "running\n":
            errors += 1
    if errors != 0:
        print("Не работает(-ют) {} сервиса(-ов)".format(errors))
    else:
        print("Все сервисы успешно запущены!")
        print("Сервер можно упаковывать в коробку!")


def replace_netplan():
    uplink = ni.interfaces()[1]
    netplan_path = "/etc/netplan/" + os.listdir('/etc/netplan')[0]
    os.system('sed -i s/eno1/{}/ {}'.format(uplink, netplan_path))
    os.system('netplan apply')

if __name__ == "__main__":
    server = Server(choose_server())
    server.set_params(server.model)
    server_opposite = Server(server.get_opposite())
    server_opposite.set_params(server_opposite.model)
    check_server_params(server)
    replace_netplan()
    check_connection()
    check_services()