#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       cli.py

import config, model
import twentyquestions as game

def ask_question():    
    question = game.choose_question()
    
    if question == None:
        game.guess_and_learn()
        return
    
    answer=raw_input(question.text + ' ')
    
    if answer == 'y':
        answer = yes # need better name
    elif answer == 'n':
        answer = no
    else:
        answer = unsure
    
    game.update_local_knowledgebase(question.id, answer)
    
def guess_and_learn():
    chosen = game.guess()
    if chosen == None:
        print 'Oh snaps, I\'ve got nothing.' ############ THIS SECTION NEEDS TO BE REWORKED
    else:
        print "I choose: %s" %(chosen.name)
    right = raw_input('Is this correct?')
    if right == 'n':
        name = raw_input("Won't you please tell me who you were thinking of?  ")
        game.learn_character(name)
    elif right == 'y':
        game.learn(chosen.id)

def play_game():
    game.load_objects_values()
    game.load_initial_questions()
    for i in range(10):
        game.ask_question()
    game.guess_and_learn()

if __name__ == '__main__':
    play_game()
