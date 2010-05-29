#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       config.py

import web
web.config.debug = False
db = web.database(dbn='sqlite', db='20q.db')
RECORD_USER = True
