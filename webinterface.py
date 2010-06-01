#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       webinterface.py

import web
import config, model
import twentyquestions as game
import admin

urls = (
    '/', 'index',
    '/begin', 'begin',
    '/answer/(\d+)', 'answer',
    '/guess', 'guess',
    '/guess/(\d+)', 'guess',
    '/learn', 'learn',
    '/restart', 'restart',
    '/admin', admin.app
)

session_vars = {'count': 1, 'asked_questions': {}, 'initial_questions': [], 'objects_values': {}}
app = web.application(urls, globals())
session = web.session.Session(app, web.session.DiskStore('sessions'), initializer=session_vars)


render = web.template.render('templates', base='base')

def reset_game():
    session.kill()
    

class index:
    def GET(self):
        # show the index!
        
        if config.DEBUG_MODE: # clean up this section somehow
            nearby_objects = game.get_nearby_objects(session.objects_values, how_many=5)
        else:
            nearby_objects = None
        
        if not(session.get('asked_questions')) and not(session.get('initial_questions')):
            question = 'begin'
        else:
            question = game.choose_question(session.initial_questions, session.objects_values, session.asked_questions)
            if question == None or session.count > 20:
                raise web.seeother('/guess')
        return render.index(question, session.get('count'), nearby_objects)

class restart:
    def POST(self):
        reset_game()
        raise web.seeother('/')

class guess:
    def GET(self, chosen_id=None):
        # guess!
        chosen = game.guess(session.objects_values)
        return render.guess(chosen)
        
    def POST(self, chosen_id=None):
        a = web.input().answer
        
        if not(chosen_id):
            chosen_id=1
        if a in ['no', 'teach me']:
            game.learn(session.asked_questions, int(chosen_id), False) # learns that the guess was wrong
            
            raise web.seeother('/learn')
        elif a in ['yes']:
            game.learn(session.asked_questions, int(chosen_id))
            
            reset_game()
            
            raise web.seeother('/')
            
class learn:
    def GET(self):
        nearby_objects = game.get_nearby_objects(session.objects_values, 20)
        return render.learn(nearby_objects)
        
    def POST(self):
        inputs = web.input()
        
        name = inputs.get('name')
        if name == "new":
            name = inputs.get('new_character')
            
        question = inputs.get('question', '')
        if question:
            new_question_answer = inputs.get('new_question_answer')
            if new_question_answer in ['yes','no','unsure']:
                answer = eval('game.' + new_question_answer) * 5
                # strongly weights new answer
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
        
        if name:
            new_object_id = game.learn_character(session.asked_questions, name)
        else:
            new_object_id = None
        
        if new_question_id and new_object_id:
            model.update_data(new_object_id, new_question_id, answer)
            
        reset_game()
        # resets game data and starts a new game
                
        raise web.seeother('/')

class begin:
    def POST(self):
                
        session.initial_questions = game.load_initial_questions()
        session.objects_values = game.load_objects_values()
                        
        raise web.seeother('/')

class answer:
    def POST(self, question_id):
        
        question_id = int(question_id) # otherwise it's unicode
        a = web.input().answer
        if a in ['yes','no','unsure']: answer = eval('game.' + a)
        else: answer = game.unsure
        session.count += 1
        game.update_local_knowledgebase(session.objects_values, session.asked_questions, question_id, answer)
        raise web.seeother('/')



if __name__ == '__main__':
    if web.config.debug:
        app.internalerror = web.debugerror
    app.run()
