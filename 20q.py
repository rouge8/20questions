#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       20q.py

'''DO WE WANT PROBABLY/DOUBTFUL OPTIONS?? WILL HAVE AN I DON'T KNOW'''

import web
import config, model

def guess():
    # return thing with highest weight from dictionary or top of heap
    pass

def ask_question():
    # pop 50 top things from heap
    # ask question such that it splits the data in halfish
    # half get negative weights, half get positive weights
    
    pass

def play_game():
    # initialize heap WITH ALL WEIGHTS AT SOME VALUE OR ZERO
    # ask AN INITIAL QUESTION (or more than one?)
    # eg. plant/animal/thing or real/fictional, etc.
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
    pass

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

if __name__ == '__main__':
    pass
