#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import re
import requests


def build_jma_prefs_master() -> dict or None:
    """気象庁からデータを取得・結合し、prefCodeと地方名のマッピング辞書を生成する"""
    amedas_url = "https://www.jma.go.jp/bosai/amedas/"
    area_url = "https://www.jma.go.jp/bosai/common/const/area.json"

    # 1. アメダス画面のHTMLから PREFS_TABLE を抽出
    try:
        res_amedas = requests.get(amedas_url, timeout=10)
        res_amedas.raise_for_status()
        html_content = res_amedas.text
    except requests.RequestException:
        return None

    if not isinstance(html_content, str) or not html_content:
        return None

    match = re.search(r"e\.PREFS_TABLE\s*=\s*(\s*\[.*?\])\s*", html_content)
    if not match:
        return None

    js_array = match.group(1)
    if not isinstance(js_array, str) or not js_array:
        return None

    # JSオブジェクトのキーをダブルクォートで囲み、JSONに補正
    json_valid_string = re.sub(
        r"([{,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:", r'\1"\2":', js_array
    )
    json_valid_string = json_valid_string.replace("'", '"')

    try:
        prefs_table = json.loads(json_valid_string)
    except json.JSONDecodeError:
        return None

    if not isinstance(prefs_table, list):
        return None

    # 2. area.json を取得してオフィス名マスタを準備
    try:
        res_area = requests.get(area_url, timeout=10)
        res_area.raise_for_status()
        area_data = res_area.json()
    except (requests.RequestException, ValueError):
        return None

    if not isinstance(area_data, dict):
        return None

    offices = area_data.get("offices")
    if not isinstance(offices, dict):
        return None

    # 3. 2つのマスタを officeCode でマッピング
    prefs_master = {}
    for item in prefs_table:
        if not isinstance(item, dict):
            continue

        pref_code = item.get("prefCode")
        office_code = item.get("officeCode")

        if (
            not isinstance(pref_code, str)
            or not pref_code
            or not isinstance(office_code, str)
            or not office_code
        ):
            continue

        office_info = offices.get(office_code)
        if not isinstance(office_info, dict):
            continue

        name = office_info.get("name")
        if not isinstance(name, str) or not name:
            continue

        prefs_master[pref_code] = name

    return prefs_master if prefs_master else None


def compare_with_current(current_prefs: dict, fetched_prefs: dict) -> dict or None:
    """手元のマスタと気象庁から取得した最新マスタを比較し、差分を返す"""
    if not isinstance(current_prefs, dict) or not current_prefs:
        return None
    if not isinstance(fetched_prefs, dict) or not fetched_prefs:
        return None

    diff = {"only_in_current": {}, "only_in_fetched": {}, "mismatched": {}}

    for code, current_name in current_prefs.items():
        if not isinstance(code, str) or not isinstance(current_name, str):
            continue

        if code not in fetched_prefs:
            diff["only_in_current"][code] = current_name
            continue

        fetched_name = fetched_prefs[code]
        if current_name != fetched_name:
            diff["mismatched"][code] = {
                "current": current_name,
                "fetched": fetched_name,
            }

    for code, fetched_name in fetched_prefs.items():
        if not isinstance(code, str) or not isinstance(fetched_name, str):
            continue

        if code not in current_prefs:
            diff["only_in_fetched"][code] = fetched_name

    return diff


if __name__ == "__main__":
    from jma.constant import PREFS

    latest = build_jma_prefs_master()

    if latest is None:
        print("[ERROR] Failed to fetch or parse JMA data.")
    else:
        result_diff = compare_with_current(PREFS, latest)

        if result_diff is not None:
            has_diff = any(result_diff.values())

            if not has_diff:
                print("OK: Master data is up to date.")
            else:
                print("[WARN] Master data mismatch detected.")
                print(json.dumps(result_diff, ensure_ascii=False, indent=4))
        else:
            print("[ERROR] Comparison failed.")
