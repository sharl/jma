# -*- coding: utf-8 -*-
import jma
from jma.amedas.data.get_latest_time import get_latest_time_yyyymmddHHMM


def get_map_data() -> dict:
    yyyymmdd, HH, MM = get_latest_time_yyyymmddHHMM()

    url = f'https://www.jma.go.jp/bosai/amedas/data/map/{yyyymmdd}{HH}{MM}00.json'
    with jma.session.get(url) as r:
        return r.json()
