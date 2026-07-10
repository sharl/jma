# -*- coding: utf-8 -*-
from jma.amedas.data.get_data import get_data


def get_latest_data(code: str,
                    latest_time: tuple[str, str, str],
                    ) -> tuple[str, dict]:
    yyyymmdd, HH, _ = latest_time

    data = get_data(code, latest_time)
    base_key = f'{yyyymmdd}{HH}0000'        # 天気・積雪は1時間毎
    last_key = list(data.keys())[-1]
    _vars = data.get(base_key, {})
    if base_key != last_key:
        _last = data.get(last_key, {})

        # 最新のデータで上書き
        for k in _last:
            _vars[k] = _last[k]

    return last_key, _vars
