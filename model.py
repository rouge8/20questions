#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       model.py

import web
from config import db

def add_object(name, asked_questions = {}):
    object_id = db.insert('objects', name=name)
    # initialize weights for each question in data
    questions = get_questions()
    for question in questions:
        if question.id in asked_questions: # learning from user
            value = asked_questions[question.id]
        else:
            value = 0
        add_data(object_id, question.id, value) # this is inconsistent
        

def add_question(question):
    question_id = db.insert('questions', text=question)
    # initialize weights for each object in data
    objects = get_objects()
    for object in objects:
        add_data(object.id, question_id)
        

def add_data(object_id, question_id, value=0):
    db.insert('data', object_id=object_id, question_id=question_id, value=value)

def update_data(object_id, question_id, value):
    db.update('data', where='object_id = $object_id AND question_id = $question_id', vars=locals(), value=value)
    # LOOK UP THE SYNTAX FOR THIS SO WE UNDERSTAND WHAT IS GOING ON
    
def update_weights(object_id, asked_questions):
    # Dictionary {question: value}
    for question in asked_questions:
        value = asked_questions[question]
        update_data(object_id, question, value)

def get_value(object_id, question_id):
    where = 'object_id=%d AND question_id=%d' %(object_id, question_id)
    try:
        return db.select('data', vars=locals(), where=where)[0].value
    except IndexError:
        return None

def get_objects():
    return db.select('objects')
    
def get_data():
    return db.select('data')

def get_questions():
    return db.select('questions')

def flush_tables():
    db.query('DELETE FROM objects')
    db.query('DELETE FROM data')
    db.query('DELETE FROM questions')
    
def get_object_by_name(name):
    try:
        return db.select('objects', vars=locals(), where='name=$name')[0]
    except IndexError:
        return None

