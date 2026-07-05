# -*- coding: utf-8 -*-
import jma

def get_amedas_table():
    url = 'https://www.jma.go.jp/bosai/amedas/const/amedastable.json'
    with jma.session.get(url) as r:
        return r.json()
