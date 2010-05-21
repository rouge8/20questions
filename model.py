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

def add_object(name):
    # WHY THE RETURNS?
    config.db.insert('objects', name=name)
    # initialize weights for each question in data

def add_question(question):
    config.db.insert('questions', question=question)
    # initialize weights for each object in data

def update_data(object_id, question_id, value):
    config.db.update('data', where='object_id = $object_id AND question_id = $questoin_id', vars=locals(), value=value)
    # LOOK UP THE SYNTAX FOR THIS SO WE UNDERSTAND WHAT IS GOING ON
    
def update_weights(object_id, questions, values):
    # list of questions by id eg. [1,2,3,5,61] with corresponding list
    # of values eg. [100,2,5,6,14]
    # MAYBE USE A DICTIONARY INSTEAD? Andy likes.
    for i in range(len(questions)):
        question_id = questions[i]
        value = values[i]
        update_data(object_id, question_id, value)
