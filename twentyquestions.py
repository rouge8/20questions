#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       twentyquestions.py

'''DO WE WANT PROBABLY/DOUBTFUL OPTIONS??'''

###################### COME UP WITH BETTER VARIABLE NAMES
###################### db.select returns list
############################## USE db.select(what=)!!!!!!!!


import web
import config, model

yes = 1
no = -1
unsure = 0
objects_values = {}
asked_questions = {}
initial_questions = []


def guess():
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
            
def learn_character(name):
    object = model.get_object_by_name(name)
    if object: # character in database
        learn(object.id)
    else:
        model.add_object(name, asked_questions) # maybe scale the numbers so more than 1
        
def add_question(object):
    question = raw_input("Question: ")
    model.add_question(question)
        
def learn(object_id):
    for question in asked_questions:
        current_weight = model.get_value(object_id, question)
        if (current_weight > 0 and asked_questions[question] > 0) or (current_weight <= 0 and asked_questions[question] <= 0):
            new_weight = current_weight + asked_questions[question]
        else:
            if current_weight == 1:
                new_weight = 0
            else:
                new_weight = current_weight / 2
        model.update_data(object_id, question, new_weight)
        model.update_times_played(object_id)

def choose_question():    
    
    if initial_questions:
        question = initial_questions.pop(0)
    else:
        sorted_objects_values = sorted([(value,key) for (key,value) in objects_values.items()])
        if len(sorted_objects_values) <= 50:
            max = len(sorted_objects_values)
        else:
            max = 50
        
        sorted_objects_values.reverse()
        most_likely_objects = sorted_objects_values[:max]
        
        
        questions = model.get_questions()
        best_question_entropy = abs(float('inf'))
        best_question = None
        
        
        for question in questions: # loop through all the questions
            if not(question.id in asked_questions): # if we have not already asked it, condider it
                question_entropy = 0
                for object in most_likely_objects:
                    #print object
                    if model.get_value(object[1], question.id) > 0: # do we add values or should we count yeses and no's
                        question_entropy += 1
                    else:
                        question_entropy -= 1
                if abs(question_entropy) <= best_question_entropy:
                    best_question_entropy = abs(question_entropy)
                    best_question = question
        question = best_question
    
    return question

def update_local_knowledgebase(question_id, answer):
    if not(answer in [yes, no, unsure]):
        raise Exception('Invalid Answer')
    else:
        weights = model.get_data_by_question_id(question_id)
        #print objects_values
        for weight in weights:
            objects_values[weight.object_id] += answer*weight.value
        #print objects_values
        asked_questions[question_id] = answer

def ask_question():
    # pop 50 top things from heap
    # ask question such that it splits the data in halfish
    # half get negative weights, half get positive weights
    #global asked_questions
    #print asked_questions
    
    question = choose_question()
    
    if question == None:
        guess_and_learn()
        return
    
    answer=raw_input(question.text + ' ')
    
    if answer == 'y':
        answer = yes # need better name
    elif answer == 'n':
        answer = no
    else:
        answer = unsure
    
    update_local_knowledgebase(question.id, answer)
    
def guess_and_learn():
    chosen = guess()
    if chosen == None:
        print 'Oh snaps, I\'ve got nothing.' ############ THIS SECTION NEEDS TO BE REWORKED
    else:
        print "I choose: %s" %(chosen.name)
    right = raw_input('Is this correct?')
    if right == 'n':
        name = raw_input("Won't you please tell me who you were thinking of?  ")
        learn_character(name)
    elif right == 'y':
        learn(chosen.id)

def play_game():
    load_objects_values()
    load_initial_questions()
    for i in range(10):
        ask_question()
    guess_and_learn()
    # then ask questions until 20 reached #### maybe in a function with parameter = number of questions to ask
    #   ######################### this way if wrong: ask_questions(10) or something like that
    #   get input from user
    #   do magic
    #       if it 'knows':
    #           ask random questions for more info. (sneaky)
    # when 20:
    #   guess
    #   right?
    #       increase weights for object/questions (learn function)
    #   wrong?
    #       decrease weights for things
    #       offer choices:
    #           continue?
    #               ask 10ish more questions? OR UNTIL VALUE REACHES SOMETHING? eg. it knows
    #           tell answer?
    #               add new thing, give it weights
    #               also offer chance for new/useful question
    #                   DON'T AUTOMATICALLY ADD THE QUESTION or obj

''' LEARNING ALGORITHM TIME
inputs: object, set of questions, responses, correct/incorrect
if correct:
    increase weights by X ?????????????
if wrong:
    HALVE weights ??????????????? //can still have negative weights, this brings closer to zero
    // if weight is 1, cut in half
'''

''' ASKING ALGORITHM
'''

def load_initial_questions(): ############## CLEAN THIS UP
    global initial_questions
    initial_questions.append(model.get_question_by_id(1))

def load_objects_values():
    global objects_values
    objects = model.get_objects()
    for object in objects:
        objects_values[object.id] = 0

def initialize_questions():
    #FIX THIS
    model.add_question('Is the character real?')
    model.add_question('Does the character like trains?')
    model.add_question('Is the character dead?')

def reset_game():
    global asked_questions
    global initial_questions
    global objects_values
    
    asked_questions = {}
    initial_questions = []
    objects_values = {}

if __name__ == '__main__':
    play_game()
