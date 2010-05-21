#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       20q.py

'''DO WE WANT PROBABLY/DOUBTFUL OPTIONS?? WILL HAVE AN I DON'T KNOW'''

###################### COME UP WITH BETTER VARIABLE NAMES
###################### db.select returns list


import web
import config, model

yes = 1
no = -1
unsure = 0
objects_values = {}
asked_questions = {}


def guess():
    # return thing with highest weight from dictionary or top of heap
    if objects_values == {}: # nothing in the database :(
        print 'Oh snaps, I\'ve got nothing.'
        learn_character()
    else:
        #max = max([objects_values[object] for object in objects_values])
        max = float('-inf')
        for object in objects_values:
            value = objects_values[object]
            if value > max:
                max = value
                id = object
        chosen = config.db.select('objects', vars=locals(), where='id = $id')[0]
        print "I choose: %s" %(chosen.name)
        right = raw_input('Is this correct?')
        if right != 'y':
            learn_character()


def learn_character():
    name = raw_input("Won't you please tell me who you were thinking of?  ")
    model.add_object(name, asked_questions)
        

def ask_question(question_id=None):
    # pop 50 top things from heap
    # ask question such that it splits the data in halfish
    # half get negative weights, half get positive weights
    global asked_questions
    
    if question_id:
        question = config.db.select('questions', vars=locals(), where='id = $question_id')[0]
    else:
        pass
    
    
    answer=raw_input(question.text)
    weights = config.db.select('data', vars=locals(), where='question_id=$question_id')
    
    if answer == 'y':
        scale = yes # need better name
    elif answer == 'n':
        scale = no
    
    for weight in weights:
        objects_values[weight.object_id] += scale*weight.value
    
    # add question to local knowledgebase
    asked_questions[question_id] = scale
        

def play_game():
    # initialize list WITH ALL VALUES AT ZERO ##### this is a value for the object
    objects = model.get_objects()
    global objects_values
    for object in objects:
        objects_values[object.id] = 0
    # ask AN INITIAL QUESTION (or more than one?)
    ask_question(1) #### ask if character is real
    guess()
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

def initialize_questions():
    #FIX THIS
    model.add_question('Is the character real?')
    model.add_question('Does the character like trains?')
    model.add_question('Is the character dead?')

if __name__ == '__main__':
    #model.flush_tables()
    #initialize_questions()
    
    play_game()
    
    for thing in model.get_data():
        print thing.object_id, thing.question_id, thing.value
