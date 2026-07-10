# -*- coding: utf-8 -*-
import jma


def get_data(code: str,
             latest_time: tuple[str, str, str],
             ) -> dict:
    yyyymmdd, HH, hh = latest_time
    url = f'https://www.jma.go.jp/bosai/amedas/data/point/{code}/{yyyymmdd}_{hh}.json'
    with jma.session.get(url) as r:
        return r.json()
