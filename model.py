#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       model.py

import web
from config import db

def add_object(name):
    # WHY THE RETURNS?
    object_id = db.insert('objects', name=name)
    # initialize weights for each question in data
    questions = get_questions()
    for question in questions:
        add_data(object_id, question.id) # this is inconsistent
        

def add_question(question):
    question_id = db.insert('questions', question=question)
    # initialize weights for each object in data
    objects = get_objects()
    for object in objects:
        add_data(object.id, question_id)
        

def add_data(object_id, question_id, value=0):
    db.insert('data', object_id=object_id, question_id=question_id, value=value)

def update_data(object_id, question_id, value):
    db.update('data', where='object_id = $object_id AND question_id = $question_id', vars=locals(), value=value)
    # LOOK UP THE SYNTAX FOR THIS SO WE UNDERSTAND WHAT IS GOING ON
    
def update_weights(object_id, questions, values):
    # list of questions by id eg. [1,2,3,5,61] with corresponding list
    # of values eg. [100,2,5,6,14]
    # MAYBE USE A DICTIONARY INSTEAD? Andy likes.
    for i in range(len(questions)):
        question_id = questions[i]
        value = values[i]
        update_data(object_id, question_id, value)

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
