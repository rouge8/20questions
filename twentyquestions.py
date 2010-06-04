#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       twentyquestions.py


import web
import config, model
import random, math

yes = 1
no = -1
unsure = 0
WEIGHT_CUTOFF = 25
RETRAIN_SCALE = 2
NEW_QUESTION_SCALE = 5


def guess(objects_values):
    # return thing with highest weight from dictionary or top of heap
    if objects_values == {}: # nothing in the database :(
        return None
    else:
        max = float('-inf')
        for object in objects_values:
            value = objects_values[object]
            if value > max:
                max = value
                id = object
        chosen = model.get_object_by_id(id)
        
        return chosen
            
def learn_character(asked_questions, name):
    if name.strip() != '':
        object = model.get_object_by_name(name)
        if object: # character in database
            learn(asked_questions, object.id)
            return object.id
        else:
            new_object_id = model.add_object(name) ### adds to database and trains
            learn(asked_questions, new_object_id)
            # maybe scale the numbers so more than 1
            return new_object_id
        
def learn(asked_questions, object_id):
    for question in asked_questions:
        current_weight = model.get_value(object_id, question)
        if not(current_weight): current_weight = 0
        
        new_weight = current_weight + asked_questions[question]
        model.update_data(object_id, question, new_weight)
        
    model.update_times_played(object_id)
        
    model.record_playlog(object_id, asked_questions, True)

def get_nearby_objects(objects_values, how_many=10):
    sorted_objects_values = sorted([(value,key) for (key,value) in objects_values.items()])
    sorted_objects_values.reverse()
    
    if sorted_objects_values:
        nearby_objects = [model.get_object_by_id(sorted_objects_values[i][1]) for i in range(how_many)]
    else:
        nearby_objects = []
        
    return nearby_objects
    

def entropy(objects, question):
    objects = tuple(objects) # necessary for SQL IN statement to work
    positives = model.get_num_positives(objects, question.id) *1.0
    negatives = model.get_num_negatives(objects, question.id) *1.0
    unknowns = model.get_num_unknowns(objects, question.id) *1.0
    total = positives + negatives + unknowns
    
    if positives != 0:
        frac_positives = (-1*positives)/total * math.log(positives/total, 2)
    else:
        frac_positives = 0
    if negatives != 0:
        frac_negatives = (-1*negatives)/total * math.log(negatives/total, 2)
    else:
        frac_negatives = 0
    if unknowns != 0:
        frac_unknowns = (-1*unknowns)/total * math.log(unknowns/total, 2)
    else:
        frac_unknowns = 0
    
    entropy = frac_positives + frac_negatives + frac_unknowns
    
    if entropy != 0: entropy = 1/entropy #minimizes rather than maximizes
    else: entropy = float('inf')
    
    return entropy

def dan_entropy(objects,question):
    objects = tuple(objects) # necessary for SQL IN statement to work
    positives = model.get_num_positives(objects, question.id)
    negatives = model.get_num_negatives(objects, question.id)
    unknowns = model.get_num_unknowns(objects, question.id)
    
    question_entropy = 0
    
    question_entropy += positives * 1
    question_entropy -= negatives * 1
    question_entropy += unknowns * 5 # arbitrary weight to discourage questions with lots of unknowns
    
    return abs(question_entropy)
                        
def choose_question(initial_questions, objects_values, asked_questions, how_many=10):
    
    if initial_questions:
        question = initial_questions.pop(0)
    else:
        sorted_objects_values = sorted([(value,key) for (key,value) in objects_values.items()])
        if len(sorted_objects_values) <= how_many: ### possibly some proportion of the objects in the database
            max = len(sorted_objects_values)
        else:
            max = how_many
        
        sorted_objects_values.reverse()  ######### change way it sorts
        most_likely_objects = sorted_objects_values[:max]
        
        objects = [object[1] for object in most_likely_objects]
        
        questions = model.get_questions()
        best_question_entropy = abs(float('inf'))
        best_question = None
        
        for question in questions: # loop through all the questions
            if not(question.id in asked_questions): # if we have not already asked it, condider it
                question_entropy = entropy(objects, question)
                if question_entropy <= best_question_entropy:
                    best_question_entropy = question_entropy
                    best_question = question
                    
                    print best_question_entropy, question.text
                    
        question = best_question
    return question

def update_local_knowledgebase(objects_values, asked_questions, question_id, answer):
    if not(answer in [yes, no, unsure]):
        raise Exception('Invalid Answer')
    else:
        weights = model.get_data_by_question_id(question_id)
        for weight in weights:
            if weight.object_id in objects_values:
                '''This if statement solves a keyerror exception that occurs when
                   an object is added to the database at the same time another player
                   is playing, but before weights is created. If this happens,
                   weights contains objects that aren't in objects_values, so you
                   get a keyerror when trying to update the weight of that object.
                   This could also be fixed by only retreiving weights for objects
                   in objects_values, but that is probably slower.'''
                if weight.value > WEIGHT_CUTOFF:
                    value = WEIGHT_CUTOFF
                else:
                    value = weight.value
                
                if answer == no and value > 0 or answer == yes and value < 0:
                    answer *= 10 # penalizes disagreement more
                objects_values[weight.object_id] += answer*value
        asked_questions[question_id] = answer

def load_initial_questions():
    initial_questions = []
    initial_questions.append(model.get_question_by_id(1)) # is character real
    questions = list(model.get_questions()) # converts from webpy's IterBetter to a list
    
    for i in range(2): # up to 2 initial random questions
        q = random.choice(questions)
        if not(q in initial_questions):
            initial_questions.append(q)
    
    initial_questions.append(model.get_question_by_id(6)) # is the character a man
    
    return initial_questions

def load_objects_values():
    objects_values = {}
    objects = model.get_objects()
    for object in objects:
        objects_values[object.id] = 0
    
    return objects_values

if __name__ == '__main__':
    ##### Tests entropy! #####
    objects = model.get_objects()
    objects = [object.id for object in objects]
    objects = tuple(objects)
    questions = model.get_questions()
    
    for question in questions:
        print question.id
        print 'DAN:', dan_entropy(objects, question)
        print 'ANDY:', entropy(objects, question)
