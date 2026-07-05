# -*- coding: utf-8 -*-
from pathlib import Path
from requests_cache import DO_NOT_CACHE, CachedSession

# cache directory
_cache_path = Path('~/.cache/amedas').expanduser()

# expires
_urls_expire_after = {
    '*/amedas/const/*': 86400,
    '*/amedas/data/*': 300,
    '*': DO_NOT_CACHE,
}

# cache settings
session = CachedSession(
    _cache_path,
    backend='filesystem',
    urls_expire_after=_urls_expire_after,
    use_cache_dir=True,
    stale_if_error=True,
)
# timeout (connect, read)
session.timeout = (5, 10)
