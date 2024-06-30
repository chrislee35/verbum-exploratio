#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 23 15:41:30 2024

@author: chris
"""
import requests
from lxml import html

def get_wikipedia_article(subject):
    #subject = 'Python (programming language)'
    url = 'https://en.wikipedia.org/w/api.php'
    params = {
            'action': 'parse',
            'format': 'json',
            'page': subject,
            'prop': 'text',
            'redirects':''
        }

    response = requests.get(url, params=params).json()
    raw_html = response['parse']['text']['*']
    document = html.document_fromstring(raw_html)

    text = ''
    for p in document.xpath('//p'):
        text += p.text_content() + '\n'
    return text

def get_wikipedia_extract(subject):
    url = 'https://en.wikipedia.org/w/api.php'
    params = {
            'action': 'query',
            'format': 'json',
            'titles': subject,
            'prop': 'extracts',
            'exintro': True,
            'explaintext': True,
        }

    response = requests.get(url, params=params)
    data = response.json()

    page = next(iter(data['query']['pages'].values()))
    return page['extract']
