#!/usr/bin/env python
# -*- coding: utf-8 -*-
from jma.amedas.table.get_amedas_table_maps import get_amedas_table_maps


lines = []
codes, locs = get_amedas_table_maps()
for loc in locs:
    _codes = locs[loc]
    if len(_codes) > 1:
        for code in _codes:
            prefs = codes[code].removesuffix(')').split('(')
            if len(prefs) > 1:
                lines.append(f'{loc} {code} {prefs[1]}')
            else:
                lines.append(f'{loc} {code}')
    else:
        lines.append(f'{loc} {locs[loc][0]}')

print('\n'.join(sorted(lines, key=lambda x: x.split()[1])))
