# -*- coding: utf-8 -*-

import requests
import json
import time
import fnmatch
import subprocess

# -----------------------Задаем параметры---------------------

# Адрес fr24feed
addr = 'http://192.168.64.128:8754/flights.json?time={0}'

# Выборка необходимых позывных
mask_callsign = {
    'RSD*': 'В небе Правительственный борт',
    'GZP*': 'Рейс Газпромавиа',
    'AFL*': 'Рейс Аэрофлот',
    'SDM*': 'Рейс Россия'
}

# Выборка необходимых HEX
mask_hex = {
    '155*':'В небе SSJ',
    '154*':'Обнаружена нынче редкая птица Ту-154',
    '14A*':'На радаре Як-42'
}
# Через сколько времени считать появление борта новым (секунды)
ttl_max = 3600

# Путь к скрипту, который будет запущен при совпадении масок
script = '/home/denzenarm/bin/./tgbot_sendtext.sh'

# Период сканирования (time to scan)
tts = 30

msg = "Радар ULSS7:"

# -----------------------------------------------------------

# Watched flights
flights_hex = {}
flights_callsign = {}

headers = {
    'User-Agent': 'FR24 JSON ALARM PARSER',
}


def check_ttl():
    global flights_hex
    global flights_callsign
    cp_flights_hex = flights_hex.copy()
    cp_flights_callsign = flights_callsign.copy()
    for i in cp_flights_hex:
        ttl = time.time() - cp_flights_hex[i]
        if ttl > ttl_max:
            del flights_hex[i]
    for i in cp_flights_callsign:
        ttl = time.time() - cp_flights_callsign[i]
        if ttl > ttl_max:
            del flights_callsign[i]


def update_dict_hex(hex):
    if hex not in flights_hex:
        flights_hex[hex] = time.time()
        return True
    else:
        return False


def update_dict_callsign(hex):
    if hex not in flights_callsign:
        flights_callsign[hex] = time.time()
        return True
    else:
        return False


def is_valid_jet(hex, callsign):
    for mask in mask_hex:
        if fnmatch.fnmatch(hex, mask):
            if update_dict_hex(hex):
                cmd = '{0} \"{1} {2} HEX={3}\"'.format(script, msg, mask_hex[mask], hex)
                #print(cmd)
                subprocess.call(cmd, shell=True)
    for mask in mask_callsign:
        if fnmatch.fnmatch(callsign, mask):
            if update_dict_callsign(hex):
                cmd = '{0} \"{1} {2} {3}\"'.format(script, msg, mask_callsign[mask], callsign)
                #print(cmd)
                subprocess.call(cmd, shell=True)

if __name__ == '__main__':
    while True:
        s = requests.get(addr.format(int(time.time())), headers=headers)
        flights_json = json.loads(s.text)
        check_ttl()
        for x in flights_json:
            is_valid_jet(flights_json[x][0], flights_json[x][16])
        time.sleep(tts)
