# -*- coding: utf-8 -*-
def get_latest_time_yyyymmddHHMM(delta: int = 0) -> tuple[str, str, str]:
    import datetime
    import jma

    # get latest time
    url = 'https://www.jma.go.jp/bosai/amedas/data/latest_time.txt'
    with jma.session.get(url) as r:
        latest_time = r.content.decode('utf-8')
        dt = datetime.datetime.strptime(latest_time, '%Y-%m-%dT%H:%M:%S%z') - datetime.timedelta(hours=delta)
        yyyymmdd = dt.strftime('%Y%m%d')
        HH = dt.strftime('%H')
        MM = dt.strftime('%M')

        return yyyymmdd, HH, MM


def get_latest_time(delta: int = 0) -> tuple[str, str, str]:
    yyyymmdd, HH, _ = get_latest_time_yyyymmddHHMM(delta=delta)
    hh = f'{int(HH) // 3 * 3:02d}'

    return yyyymmdd, HH, hh
