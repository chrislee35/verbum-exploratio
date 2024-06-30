#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 22 22:09:58 2024

@author: chris
"""
import csv
#import random # for testing
import gzip
import pickle
from collections import Counter

data = {}

with gzip.open('etymology.csv.gz', 'rt') as zfh:
    cols = zfh.readline().strip().split(',')
    c = csv.DictReader(zfh, fieldnames=cols)
    for rec in c:
        if rec['lang'] not in data: data[rec['lang']] = {}
        lang = data[rec['lang']]
        if rec['term'] not in lang: lang[rec['term']] = []
        term = lang[rec['term']]
        new_rec = {
            'type': rec['reltype'],
            'lang': rec['related_lang'],
            'term': rec['related_term']
        }
        term.append(new_rec)

for lang in data.keys():
    derlangs = Counter()
    for word in data[lang]:
        for rel in data[lang][word]:
            if rel['type'] != 'derived_from': continue
            derlangs.update([rel['lang']])
    data[lang]["DERIVED_FROM"] = derlangs

    with gzip.open(f'etymology-{lang}.pckl.gz', 'w') as zfh:
        pickle.dump(data[lang], zfh)
