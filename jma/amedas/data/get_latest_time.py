# -*- coding: utf-8 -*-
import datetime


def get_latest_time() -> tuple[str, str, str]:
    import jma

    # get latest time
    url = 'https://www.jma.go.jp/bosai/amedas/data/latest_time.txt'
    with jma.session.get(url) as r:
        latest_time = r.content.decode('utf-8')
        dt = datetime.datetime.strptime(latest_time, '%Y-%m-%dT%H:%M:%S%z')
        yyyymmdd = dt.strftime('%Y%m%d')
        HH = dt.strftime('%H')
        hh = f'{int(HH) // 3 * 3:02d}'

        return yyyymmdd, HH, hh
