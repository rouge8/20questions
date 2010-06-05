#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
'''
    model.py
    
    Andy Freeland and Dan Levy
    5 June 2010
    
    Contains functions to handle database queries.
'''

import web
from config import db

def add_object(name):
    '''Adds an object with the given name to the objects table in the database.
       Also initializes weights for each question in the data table.'''
       
    object_id = db.insert('objects', name=name)
    # initialize weights for each question in data
    questions = get_questions()
    for question in questions:
        add_data(object_id, question.id)
    
    return object_id
        

def add_question(question):
    '''Adds a question with the given text to the questions table in the database.
       Also initializes weights for each object in the data table.'''
       
    question_id = db.insert('questions', text=question)
    # initialize weights for each object in data
    objects = get_objects()
    for object in objects:
        add_data(object.id, question_id)
    return question_id

def add_data(object_id, question_id, value=0):
    '''Inserts a weight with value=value for a specified object_id and question_id
       into data. Defaults to value=0.'''
       
    db.insert('data', object_id=object_id, question_id=question_id, value=value)

def update_data(object_id, question_id, value):
    '''Updates the weight for a specified object_id and question_id in data with
       the specified value.'''
       
    db.update('data', where='object_id = $object_id AND question_id = $question_id', vars=locals(), value=value)
    
#def update_weights(object_id, asked_questions):
    
    ## Dictionary {question: value}
    #for question in asked_questions:
        #value = asked_questions[question]
        #update_data(object_id, question, value)

def get_objects():
    '''Returns an IterBetter of all the objects in database, where each row is a Storage object.'''
    return db.select('objects')
    
def get_data():
    '''Returns an IterBetter of all the data in the database, where each row is a Storage object.'''
    return db.select('data')

def get_questions():
    '''Returns an IterBetter of all the quesitons in the database, where each row is a Storage object.'''
    return db.select('questions')

def get_value(object_id, question_id):
    '''Returns the weight for given object_id question_id from data. If the weight
       does not exist, returns None.'''
       
    where = 'object_id=%d AND question_id=%d' %(object_id, question_id)
    try:
        return db.select('data', vars=locals(), where=where)[0].value
    except IndexError:
        return None

def get_object_by_name(name):
    '''Returns a Storage object containing an object where name=name.'''
    try:
        return db.select('objects', vars=locals(), where='name=$name')[0]
    except IndexError:
        return None

def get_object_by_id(id):
    '''Returns a Storage object containing an object where id=id.'''
    try:
        return db.select('objects', vars=locals(), where='id = $id')[0]
    except IndexError:
        return None

def get_question_by_id(id):
    '''Returns a Storage object containing a question where id=id.'''
    try:
        return db.select('questions', vars=locals(), where='id=$id')[0]
    except IndexError:
        return None
        
def get_question_by_text(text):
    '''Returns Storage object containing a question where text=text.'''
    try:
        return db.select('questions', vars=locals(), where='text=$text')[0]
    except IndexError:
        return None

def get_data_by_question_id(question_id):
    '''Returns an IterBetter all weights for a particular question_id, where each
       row is a Storage object.'''
    try:
        return db.select('data', vars=locals(), where='question_id=$question_id')
    except IndexError:
        return None
        
def get_data_by_object_id(object_id):
    '''Returns an IterBetter of all weights for a particular object_id, where each
       row is a Storage object.'''
    try:
        return db.select('data', vars=locals(), where='object_id=$object_id')
    except IndexError:
        return None

def get_data_dictionary():
    '''Returns the data as a dictionary object, where keys are (object_id, question_id)
       tuples, and values are the weights for that pair.'''
       
    d = get_data()
    data = {}
    
    for row in d:
        data[(row.object_id, row.question_id)] = row.value
    
    return data

def get_num_unknowns(object_tuple, question_id):
    '''Returns the number of objects in the object_tuple where the value for the
       given question_id is zero, or unknown.'''
       
    assert type(object_tuple) == tuple
    
    where = 'object_id in %s AND question_id=%d AND value =0' %(object_tuple, question_id)
    try:
        rows = db.select('data', vars=locals(), where=where, what='count(*) AS count')
        return rows[0].count
    except IndexError:
        return 0

def get_num_positives(object_tuple, question_id):
    '''Returns the number of objects in the object_tuple where the value for the
       given question_id is positive.'''
       
    assert type(object_tuple) == tuple
    
    where = 'object_id IN %s AND question_id=%d AND value >0' %(object_tuple, question_id)
    try:
        rows = db.select('data', vars=locals(), where=where, what='count(*) AS count')
        return rows[0].count
    except IndexError:
        return 0

def get_num_negatives(object_tuple, question_id):
    '''Returns the number of objects in the object_tuple where the value for the
       given question_id is negative.'''
       
    assert type(object_tuple) == tuple
    
    where = 'object_id in %s AND question_id=%d AND value <0' %(object_tuple, question_id)
    try:
        rows = db.select('data', vars=locals(), where=where, what='count(*) AS count')
        return rows[0].count
    except IndexError:
        return 0

def delete_question(question_id):
    '''Deletes a question and its weights for a particular question_id.'''
    db.delete('questions', where='id=$question_id', vars=locals())
    db.delete('data', where='question_id=$question_id', vars=locals())
    
def delete_object(object_id):
    '''Deletes an object and its weights for a particular object_id.'''
    db.delete('objects', where='id=$object_id', vars=locals())
    db.delete('data', where='object_id=$object_id', vars=locals())

def update_times_played(object_id):
    '''Increments the number of times played for a particular object_id.'''
    current = db.select('objects', vars=locals(), where='id=$object_id')[0].times_played
    if current == None: current = 0
    db.update('objects', where='id = $object_id', vars=locals(), times_played=current+1)

def num_objects():
    '''Returns the number of objects in database.'''
    return db.query('select COUNT(*) from objects;')

def record_playlog(object_id, asked_questions, right):
    '''Records the questions and responses, and outcomes of each game. Allows us
       to experiment using different parameters without having to retrain from scratch.'''
    db.insert('playlog', object_id=object_id, data=str(asked_questions), right=right)

def flush_tables():
    '''Deletes everything from the database. BEWARE!'''
    db.query('DELETE FROM objects')
    db.query('DELETE FROM data')
    db.query('DELETE FROM questions')
