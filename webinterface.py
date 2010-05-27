#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       whatnxt.py

import web
import config, model
import twentyquestions as game
count = 1

urls = (
    '/', 'index',
    '/begin', 'begin',
    '/answer/(\d+)', 'answer',
    '/guess', 'guess',
    '/guess/(\d+)', 'guess',
    '/learn', 'learn'
)

render = web.template.render('templates', base='base')

class index:
    def GET(self):
        # show the index!
        global count
                
        if game.asked_questions == {} and game.initial_questions == []:
            question = 'begin'
        else:
            question = game.choose_question()
            if question == None or count > 20:
                raise web.seeother('/guess')
        return render.index(question,count)

class guess:
    def GET(self, chosen_id=None):
        # guess!
        chosen = game.guess()
        return render.guess(chosen)
    def POST(self, chosen_id=None):
        a = web.input().answer
        
        if not(chosen_id):
            chosen_id=1
            print 'CHOOSING NONE!!!!!!!'
            print 'asked questions: ', game.asked_questions
        if a in ['no', 'teach me']:
            game.learn(int(chosen_id), False) # learns that the guess was wrong
            
            raise web.seeother('/learn')
        elif a in ['yes']:
            game.learn(int(chosen_id))
            
            game.reset_game()
            
            #print 'ASKED QUESTION:', game.asked_questions
            #print 'INITIAL QUESTION:', game.initial_questions
            #print 'OBJECTS VALUES:', game.objects_values
            
            raise web.seeother('/')
            
class learn:
    def GET(self):
        nearby_objects = game.get_nearby_objects(10)
        return render.learn(nearby_objects)
    def POST(self):
        inputs = web.input()
        
        name = inputs.get('name')
        if name == "new":
            name = inputs.get('new_character')
            
        question = inputs.get('question', '')
        if question:
            new_question_answer = inputs.get('new_question_answer')
            if new_question_answer in ['yes','no','unsure']: answer = eval('game.' + new_question_answer)
            else: answer = game.unsure
        
        if question.strip() != '' and not(model.get_question_by_text(question.strip())):
            # makes sure the question is not already in the database
            new_question_id = model.add_question(question)
        else:
            new_question = model.get_question_by_text(question.strip())
            # if question already in DB, returns question. else returns None.
        if new_question:
            new_question_id = new_question.id
        else:
            new_question_id = None

        new_object_id = game.learn_character(name)
        
        if new_question_id and new_object_id:
            model.update_data(new_object_id, new_question_id, answer)
            
        game.reset_game()
        # resets game data and starts a new game
                
        raise web.seeother('/')

class begin:
    def POST(self):
        global count
        count = 1
        game.reset_game()
        
        game.load_initial_questions()
        game.load_objects_values()
                
        raise web.seeother('/')

class answer:
    def POST(self, question_id):
        global count
        
        question_id = int(question_id) # otherwise it's unicode
        a = web.input().answer
        print 'FORM VALUE IS' ,a
        if a in ['yes','no','unsure']: answer = eval('game.' + a)
        else: answer = game.unsure
        count += 1
        game.update_local_knowledgebase(question_id, answer)
        raise web.seeother('/')

if __name__ == '__main__':
    app = web.application(urls, globals())
    if web.config.debug:
        app.internalerror = web.debugerror
    app.run()
