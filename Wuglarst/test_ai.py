#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
r = requests.post('http://localhost:8001/api/futaba/chat', json={'message': 'ты правда ИИ?'})
with open('ai_test.txt', 'w', encoding='utf-8') as f:
    f.write(r.json()['response'])
print("done")
