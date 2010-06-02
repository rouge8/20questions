#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       admin.py

import web
import config, model
import twentyquestions as game

urls = (
    '', 'admin',
    '/', 'admin',
    '/dq', 'delete_question',
    '/do', 'delete_object',
    '/data', 'data',
    '/retrain/(\d+)', 'retrain'
)

render = web.template.render('templates', base='base')
app = web.application(urls, locals())

class admin:
    def GET(self):
        return render.admin()

class delete_question:
    def GET(self):
        questions = model.get_questions()
        return render.delete_question(questions)
    def POST(self):
        question_ids = web.input()
        for id in question_ids:
            model.delete_question(id)
        raise web.seeother('/')

class delete_object:
    def GET(self):
        objects = model.get_objects()
        return render.delete_object(objects)
    def POST(self):
        object_ids = web.input()
        for id in object_ids:
            model.delete_object(id)
        raise web.seeother('/')
        
class data:
    def GET(self):
        objects = model.get_objects()
        
        return render.data(list(objects))

class retrain:
    def GET(self, object_id):
        object = model.get_object_by_id(object_id)
        questions = model.get_questions()
        data = model.get_data_dictionary()
        if object:
            return render.retrain(object, list(questions), data)
        else:
            raise web.seeother('/') # returns to admin page
            
    def POST(self, object_id):
        inputs = web.input()
        for question_id in inputs:
            answer = inputs[question_id]
            if answer in ['yes','no','unsure']:
                value = eval('game.' + answer) * game.RETRAIN_SCALE # STRONGLY weights values learned this way
                model.update_data(object_id, question_id, value)
        
        raise web.seeother('/data')
