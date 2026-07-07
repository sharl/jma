# -*- coding: utf-8 -*-
import jma


def get_latest_data(code: str,
                    latest_time: tuple[str, str, str],
                    ) -> tuple[str, dict]:
    yyyymmdd, HH, hh = latest_time
    url = f'https://www.jma.go.jp/bosai/amedas/data/point/{code}/{yyyymmdd}_{hh}.json'
    with jma.session.get(url) as r:
        data = r.json()
        base_key = f'{yyyymmdd}{HH}0000'        # 天気・積雪は1時間毎
        last_key = list(data.keys())[-1]
        _vars = data.get(base_key, {})
        _last = data.get(last_key, {})
        # 最新のデータで上書き
        for k in _last:
            _vars[k] = _last[k]

        return last_key, _vars
