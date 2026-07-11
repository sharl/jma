# -*- coding: utf-8 -*-
from pathlib import Path
from requests_cache import DO_NOT_CACHE, CachedSession

# cache backend
_backend = 'filesystem'
# cache directory
_cache_path = Path('~/.cache/amedas').expanduser()

# cache durations
_SEC_1_DAY = 86400
_SEC_3_HOURS = 3 * 60 * 60

# expires
_urls_expire_after = {
    '*/amedas/const/*': _SEC_1_DAY,
    '*/amedas/data/latest_time.txt': 3,
    '*/amedas/data/*': 300,
    '*/forecast/data/forecast/*': _SEC_3_HOURS,
    '*/forecast/const/*': _SEC_1_DAY,
    '*/common/const/*': _SEC_1_DAY,
    '*': DO_NOT_CACHE,
}


class JMASession(CachedSession):
    def request(self, method: str, url: str, *args, **kwargs):
        # Respect the setting if the caller explicitly specifies it.
        if 'expire_after' in kwargs:
            return super().request(method, url, *args, **kwargs)

        if '/amedas/data/point/' in url:
            url_date, url_hour = url.split('/')[-1].removesuffix('.json').split('_')

            try:
                from jma.amedas.data.get_latest_time import get_latest_time
                yyyymmdd, _, hh = get_latest_time()

                # 厳格な型判定と存在チェック
                if (isinstance(yyyymmdd, str) and isinstance(hh, str)
                        and yyyymmdd and hh):

                    # 最新ファイルなら300秒、過去ログなら1日
                    if url_date == yyyymmdd and url_hour == hh:
                        kwargs['expire_after'] = 300
                    else:
                        kwargs['expire_after'] = _SEC_1_DAY
            except Exception:
                # 早期脱出（フォールバック）
                kwargs['expire_after'] = 300

        return super().request(method, url, *args, **kwargs)


# cache settings
session = JMASession(
    _cache_path,
    backend=_backend,
    urls_expire_after=_urls_expire_after,
    use_cache_dir=True,
    match_headers=True,
    stale_if_error=True,
)
# timeout (connect, read)
session.timeout = (5, 10)

if _backend == 'filesystem':
    # delete expired cache
    session.cache.delete(expired=True)
