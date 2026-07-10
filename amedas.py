#!/usr/bin/env python
# -*- coding: utf-8 -*-
from concurrent.futures import ThreadPoolExecutor
import os
import sys

from jma.amedas.data.get_latest_data import get_latest_data
from jma.amedas.data.get_latest_time import get_latest_time
from jma.constant import WIND_DIRECTIONS as WD, WEATHER_INFO, AQC_OK

# codes format:
#
#       spotname code [region]
#
# 札幌 14163
# 東京 44132
# 清水 50261 静岡
# 清水 65121 和歌山
# 清水 74516 高知
#
# from
#       http://www.jma.go.jp/jma/kishou/know/amedas/kaisetsu.html
#       http://www.jma.go.jp/jma/kishou/know/amedas/ame_master.zip
#       make_amedas.py
basename = os.path.splitext(os.path.basename(sys.argv[0]))[0]
codes = []
with open(f"{os.environ.get('HOME', '.')}/.{basename}") as fd:
    for line in fd.read().strip().split('\n'):
        t = f'{line} '.split(' ')
        codes.append([t[0], t[1], t[2]])

# get latest time
latest_time = get_latest_time()

# parse arguments
AMEDAS = os.environ.get('AMEDAS', '44132').split()
if len(sys.argv) > 1:
    _args = []
    for arg in sys.argv[1:]:
        for _arg in arg.split():
            if _arg:
                _args.append(_arg)
    if _args:
        AMEDAS = _args

# check errors
errs = []
for arg in AMEDAS:
    count = 0
    for loc, code, pref in codes:
        if arg.isdigit():
            if code == arg:
                count += 1
        else:
            if loc == arg:
                count += 1
    if not count:
        errs.append(arg)


def fetch_data(loc, code, lines):
    try:
        last_key, _vars = get_latest_data(code, latest_time)

        h = last_key[8:10]
        if h == '00':
            h = '24'
        m = last_key[10:12]
        _lines = [f'{loc} {h}:{m}']
        for x in [
                '天気 weather -',
                '気温 temp 度',
                '降水量 precipitation1h mm/h',
                '風向 windDirection -',
                '風速 wind m/s',
                '積雪 snow cm',
                '降雪 snow1h cm/h',
                '湿度 humidity %',
                '気圧 pressure hPa',
                '最低気温 minTemp 度',
                '最高気温 maxTemp 度',
        ]:
            t, k, u = x.split()
            if k in _vars:
                v, aqc = _vars[k]
                if isinstance(v, float):
                    if v == int(v):
                        v = int(v)
                if aqc not in AQC_OK:
                    continue
                else:
                    if k == 'windDirection':
                        _lines.append(f'{t} {WD[v]}')
                    elif k == 'weather':
                        _lines.append(f'{t} {WEATHER_INFO[v]}')
                    elif 'Temp' in k:
                        h, m = _vars[f'{k}Time'].values()
                        if (h or m) is not None:
                            _lines.append(f"{t} {v}{u} ({(h + 9) % 24:02d}:{m:02d})")
                        else:
                            _lines.append(f"{t} {v}{u}")
                    else:
                        _lines.append(f'{t} {v}{u}')
        lines[loc] = ' '.join(_lines)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# points: { key: name, value: code}
points = {}
for name in AMEDAS:
    loc = None
    code = None
    for _loc, _code, _pref in codes:
        if _loc == name or name == _code:
            if _pref and _pref != '東京':
                loc = f'{_loc}({_pref})'
            else:
                loc = _loc
            code = _code
        if loc and code:
            points[loc] = code


if True:
    def fetch_data_worker(loc, code):
        lines = {}
        fetch_data(loc, code, lines)
        return loc, lines.get(loc, None)

    with ThreadPoolExecutor(max_workers=len(points)) as executor:
        results = executor.map(
            lambda loc: fetch_data_worker(loc, points[loc]),
            points
        )

    for _, line in results:
        if line:
            print(line)
else:
    lines = {}
    for loc in points:
        fetch_data(loc, points[loc], lines)
    print('\n'.join([lines[loc] for loc in lines]))

if errs:
    print(f"{' '.join(errs)} が見つかりませんでした。https://www.jma.go.jp/bosai/map.html#contents=amedas から観測地点を指定してください。")
