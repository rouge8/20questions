#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       admin.py

import web
import config, model
import twentyquestions as game

urls = (
    '', 'admin',
    '/dq', 'delete_question',
    '/do', 'delete_object'
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
        raise web.seeother('')

class delete_object:
    def GET(self):
        objects = model.get_objects()
        return render.delete_object(objects)
    def POST(self):
        object_ids = web.input()
        for id in object_ids:
            model.delete_object(id)
        raise web.seeother('')
        
