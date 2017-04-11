# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------

from KeyWordSearcherModule.KeyWordSearcher import KeyWordSearcher
import json
import os

no_input_text = "123__NO_INPUT_TEXT__123"

def index():
    redirect(URL('matcher'))

def matcher():
    text_input = None
    if request.cookies.has_key('text_input') and request.cookies['text_input'].value == no_input_text:
        text_input = ""
    elif request.cookies.has_key('text_input') and request.cookies['text_input'].value != "":
        text_input = request.cookies['text_input'].value
        print text_input
    else:
        filepath = os.path.join(request.folder, 'uploads', 'keyWords.txt')
        with open(filepath, 'r') as text_input_file:
            text_input = text_input_file.read()
    keyWordSearcher = KeyWordSearcher(text_input)
    keyWordMatches = keyWordSearcher.matches
    # keyWordMatchString = '{"this_week": [], "next_week": [{"company_name": "Tocagen", "keyWordMatches": ["develop","dev","devel"], "description": "tocagen, inc. operates as a clinical-stage, cancer-selective gene therapy company. the company focuses on developing treatment of cancer using cancer-selective gene therapy products based on retroviral gene therapy platforms. tocagen serves patients in the united states."}],"future":[]}'
    # keyWordMatches = json.loads(keyWordMatchString)
    groups=[("This Week", "this_week"),("Next Week","next_week"),("Future","future")]
    return dict(message=T('IPO Matcher'),matches=keyWordMatches,groups=groups,text_area_input=text_input)

def submit_keyword_input():
    if request.vars.text_input:
        response.cookies['text_input'] = request.vars.text_input
        response.cookies['text_input']['expires'] = 1*3600 #expires in 1 hour
    elif request.vars.clear_text_input:
        response.cookies['text_input'] = no_input_text
    redirect(URL('matcher'))


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


