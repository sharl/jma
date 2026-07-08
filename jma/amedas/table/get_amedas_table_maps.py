
# -*- coding: utf-8 -*-
import csv
from io import BytesIO, StringIO
import zipfile
from jma import session

# (flake8 extend-ignore = E501)
MASTER_ZIP_URL = "https://www.jma.go.jp/jma/kishou/know/amedas/ame_master.zip"

# 酸ヶ湯トラップから生まれた秘伝の表記揺れ変換テーブル
TRANS_TABLE = {
    "ケ": "ヶ",
    "ヶ": "ケ",
    "鰺": "鯵",
    "桧枝岐": "檜枝岐",
}


def expand_variations(word: str) -> list[str]:
    """Perl版の trans 関数を完全再現: 表記揺れパターンをすべて網羅して返す"""
    if not isinstance(word, str):
        return []

    results = {word}

    # 1次変換
    for orig, rep in TRANS_TABLE.items():
        if orig in word:
            tmp = word.replace(orig, rep)
            results.add(tmp)
            # 2次変換（複合的な変換に対応）
            for orig2, rep2 in TRANS_TABLE.items():
                if orig2 in tmp:
                    results.add(tmp.replace(orig2, rep2))

    return sorted(list(results))


def get_amedas_table_maps() -> tuple[dict[str, str], dict[str, list[str]]]:
    """Perl版の魂を継承した完全自律型ツインマップ生成ロジック。
    ZIPをキャッシュ経由で取得・メモリ上でdeflateし、重複対策済みのマップを構築する。
    """
    code_to_display: dict[str, str] = {}
    name_to_codes: dict[str, list[str]] = {}

    try:
        response = session.get(MASTER_ZIP_URL)
        if response.status_code != 200:
            return code_to_display, name_to_codes
    except Exception:
        # ネットワークエラー時もプロセスを落とさず生存権（透過性）を確保
        return code_to_display, name_to_codes

    codes = {}
    raw_data = []
    dup_counts: dict[str, int] = {}

    # 1. ZIPをインメモリで解凍してパース
    try:
        with zipfile.ZipFile(BytesIO(response.content)) as z:
            csv_filename = z.namelist()[0]
            with z.open(csv_filename) as f:
                # 気象庁の生CSVは cp932 (Shift_JIS)
                csv_text = f.read().decode("cp932", errors="ignore")
    except Exception:
        return code_to_display, name_to_codes

    # 2. 1週目のスキャン：重複カウントと基本データの収集
    reader = csv.reader(StringIO(csv_text))
    try:
        next(reader)  # ヘッダーをスキップ
    except StopIteration:
        return code_to_display, name_to_codes

    for row in reader:
        if len(row) < 6:
            continue
        pref, st_code, _, point, _, airport = row[0], row[1], row[2], row[3], row[4], row[5]
        if not st_code or not point:
            continue

        # CSV に複数同一地点コードが登録されている場合があるので多重登録をガード
        # 風速・日照が分離して複数行になっている場合がある(八戸など)
        if st_code not in codes:
            codes[st_code] = 0
            raw_data.append((pref, st_code, point, airport))
            dup_counts[point] = dup_counts.get(point, 0) + 1

    # 3. 2週目のスキャン：表記揺れ・空港名・名寄せの反映
    for pref, st_code, point, airport in raw_data:
        # 金山問題の救済：重複がある場合は「金山(上川)」のように地方名を添える
        if dup_counts.get(point, 0) > 1:
            display_name = f'{point}({pref})'
        else:
            display_name = point

        # コード -> 表示名の確定 (Viewが一撃で楽できる形)
        code_to_display[st_code] = display_name

        # 地名の表記揺れバリエーションをすべて展開して逆引きに登録
        for kpoint in expand_variations(point):
            if kpoint not in name_to_codes:
                name_to_codes[kpoint] = []
            if st_code not in name_to_codes[kpoint]:
                name_to_codes[kpoint].append(st_code)

        # 空港名エイリアスの救済ロジック (成田空港等でも引けるように)
        if isinstance(airport, str) and airport.endswith("空港") and point != airport:
            for kairport in expand_variations(airport):
                if kairport not in name_to_codes:
                    name_to_codes[kairport] = []
                if st_code not in name_to_codes[kairport]:
                    name_to_codes[kairport].append(st_code)

    return code_to_display, name_to_codes
