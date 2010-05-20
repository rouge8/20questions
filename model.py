#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       model.py

import web
import config
'''
def get_tasks():
    return config.db.select('tasks', order='id')

def new_task(text):
    return config.db.insert('tasks', title=text)

def complete_task(id):
    return config.db.update('tasks', where='id = $id', vars=locals(), done='t')

def empty_tasks():
    return config.db.query("DELETE FROM tasks")
'''

'''
We'll want to do things like this managing the database, and just calling our
functions from within the main program.
'''

pass
