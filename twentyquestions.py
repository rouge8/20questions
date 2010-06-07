#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
'''
    twentyquestions.py
    
    Andy Freeland and Dan Levy
    5 June 2010
    
    Contains the game logic for a twenty questions player.
'''


import web
import config, model
import random, math

yes = 1 # value of a yes answer
no = -1 # value of a no answer
unsure = 0 # value of an unsure answer
WEIGHT_CUTOFF = 10 # caps weights in knowledgebase
RETRAIN_SCALE = 2 # scale for weights set through the admin interface
NEW_QUESTION_SCALE = 5 # scale for weights learned through the new question/guess page

def load_initial_questions():
    '''Loads questions we always want to ask as well as some random ones so that we can learn more
       about the objects.'''
    
    initial_questions = []
    initial_questions.append(model.get_question_by_id(1)) # is character real
    questions = list(model.get_questions()) # converts from webpy's IterBetter to a list
    
    for i in range(2): # up to 2 initial random questions
        q = random.choice(questions)
        if not(q in initial_questions) and not(q.id in [1,6]): # real/man
            initial_questions.append(q)
    
    initial_questions.append(model.get_question_by_id(6)) # is the character a man
    
    return initial_questions

def load_objects_values():
    '''Initializes objects values, a list with an entry for each object, initialized at 0.'''
    
    objects_values = {}
    objects = model.get_objects()
    for object in objects:
        objects_values[object.id] = 0
    
    return objects_values

def sort_objects_values(objects_values):
    '''Returns a list of the objects with the highest values in the local knowledge base.'''
    
    sorted_objects_values = sorted([(value, key) for (key, value) in objects_values.items()])
    sorted_objects_values.reverse()
    
    return sorted_objects_values
    
def get_nearby_objects(objects_values, how_many=10):
    '''Returns how_many objects with the highest values in the local knowledge base.
       Default: how_many=10.'''
       
    sorted_objects_values = sort_objects_values(objects_values)
    
    if how_many > len(sorted_objects_values):
        how_many = len(sorted_objects_values)
    
    if sorted_objects_values:
        nearby_objects = [model.get_object_by_id(sorted_objects_values[i][1]) for i in range(how_many)]
    else:
        nearby_objects = []
        
    return nearby_objects

def get_nearby_objects_values(objects_values, how_many=10):
    '''Returns how_many (value, object) pairs with the highest values in the local
       knowledge base. Default: how_many=10.'''
       
    sorted_objects_values = sort_objects_values(objects_values)
    
    if how_many > len(sorted_objects_values):
        how_many = len(sorted_objects_values)
    
    if sorted_objects_values:
        nearby_objects_values = [(sorted_objects_values[i][0], model.get_object_by_id(sorted_objects_values[i][1])) for i in range(how_many)]
    else:
        nearby_objects_values = []
        
    return nearby_objects_values

def entropy(objects, question):
    '''Returns an entropy value. This algorithm for entropy is heavily modeled
       on the ID3 decision tree algorithm for entropy. The difference is that here,
       we want what would traditionally be a high entropy. To adjust for this,
       we take the reciprocal of entropy before returning it.'''
       
    objects = tuple(objects) # necessary for SQL IN statement to work
    positives = model.get_num_positives(objects, question.id) *1.0
    negatives = model.get_num_negatives(objects, question.id) *1.0
    total = len(objects)
    
    if positives != 0:
        frac_positives = (-1*positives)/total * math.log(positives/total, 2)
    else:
        frac_positives = 0
    if negatives != 0:
        frac_negatives = (-1*negatives)/total * math.log(negatives/total, 2)
    else:
        frac_negatives = 0
    
    entropy = frac_positives + frac_negatives
    
    entropy *= (positives + negatives)/total # weighted average
    
    if entropy != 0: entropy = 1/entropy # minimizes rather than maximizes
    else: entropy = float('inf')
    
    return entropy

def simple_entropy(objects,question):
    '''Returns an entropy value for a question based on the weights for all the
       objects. Entropy is low if for a given question, the number of yes and no
       answers is about even, and the number of unsure answers is low.'''
    
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
    '''Returns a question with the lowest entropy.'''
    
    if initial_questions:
        question = initial_questions.pop(0)
    else:
        sorted_objects_values = sorted_objects_values = sort_objects_values(objects_values)
        if len(sorted_objects_values) <= how_many: ### possibly some proportion of the objects in the database
            max = len(sorted_objects_values)
        else:
            max = how_many
        
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
                    
        question = best_question
    return question

def update_local_knowledgebase(objects_values, asked_questions, question_id, answer):
    '''Updates the the values for the current candidates based on the previus
       question and reply by the user.'''
    
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
                elif weight.value < -1 * WEIGHT_CUTOFF:
                    value = -1 * WEIGHT_CUTOFF
                elif weight.value < unsure:
                    value = weight.value / 2 # lessens impact of strong negatives
                else:
                    value = weight.value
                
                if (answer == no and value > 0) or (answer == yes and value < 0):
                    value *= 5 # penalizes disagreement more
                    
                objects_values[weight.object_id] += answer*value
        asked_questions[question_id] = answer

def guess(objects_values):
    '''Returns the object with the highest value.'''
    
    if objects_values == {}: # nothing in the database :(
        return None
    else:
        chosen = get_nearby_objects(objects_values, how_many=1)[0]     
        return chosen
            
def learn_character(asked_questions, name):
    '''Adds a new object to the database and then learns that object. Returns
       the id of that object.'''
    if name.strip() != '':
        object = model.get_object_by_name(name)
        if object: # character in database
            learn(asked_questions, object.id)
            return object.id
        else:
            new_object_id = model.add_object(name) ### adds to database and trains
            learn(asked_questions, new_object_id)
            return new_object_id
        
def learn(asked_questions, object_id):
    '''Updates the data for the correct object based on information in asked_questions.
       Also updates times played for the object and stores the playlog.'''
    for question in asked_questions:
        current_weight = model.get_value(object_id, question)
        if not(current_weight): current_weight = 0
        
        new_weight = current_weight + asked_questions[question]
        model.update_data(object_id, question, new_weight)
        
    model.update_times_played(object_id)
        
    model.record_playlog(object_id, asked_questions, True)


if __name__ == '__main__':
    ##### Tests entropy! #####
    objects = model.get_objects()
    objects = [object.id for object in objects]
    objects = tuple(objects)
    questions = model.get_questions()
    
    for question in questions:
        print question.id
        print 'DAN:', simple_entropy(objects, question)
        print 'ANDY:', entropy(objects, question)
