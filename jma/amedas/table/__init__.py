# -*- coding: utf-8 -*-
def get():
    import jma

    url = 'https://www.jma.go.jp/bosai/amedas/const/amedastable.json'
    with jma.session.get(url) as r:
        return r.json()
