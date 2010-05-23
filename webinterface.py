#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       whatnxt.py

import web
import config, model
import twentyquestions as game
count = 0

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
            count += 1
            if question == None or count == 20:
                raise web.seeother('/guess')
        return render.index(question)

class guess:
    def GET(self):
        # guess!
        chosen = game.guess()
        return render.guess(chosen)
    def POST(self, chosen_id=None):
        a = web.input().answer
        if a in ['no', 'teach me']:
            raise web.seeother('/learn')
        elif a in ['yes']:
            game.learn(int(chosen_id))
            game.reset_game()
            raise web.seeother('/')
            
class learn:
    def GET(self):
        return render.learn()
    def POST(self):
        name = web.input().name
        question = web.input().question
        game.learn_character(name)
        if question.strip() != '' and not(model.get_question_by_text(question.strip())):
            # makes sure the question is not already in the database
            model.add_question(question)
        game.reset_game()
        # resets game data and starts a new game
        raise web.seeother('/')

class begin:
    def POST(self):
        game.load_initial_questions()
        game.load_objects_values()
        raise web.seeother('/')

class answer:
    def POST(self, question_id):
        question_id = int(question_id) # otherwise it's unicode
        a = web.input().answer
        if a in ['yes','no','unsure']: answer = eval('game.' + a)
        else: answer = 0
        
        game.update_local_knowledgebase(question_id, answer)
        raise web.seeother('/')

if __name__ == '__main__':
    app = web.application(urls, globals())
    if web.config.debug:
        app.internalerror = web.debugerror
    app.run()
