
# This Python file uses the following encoding: utf-8
#-----------------------------------------------------------------------------------
# CompleteMagic
#-----------------------------------------------------------------------------------
#
# Originally derived from DictionaryAutocomplete by (c) Florian Zinggeler
#-----------------------------------------------------------------------------------
# is there some way to trigger the popup with non-matching strings? This would enable
# automatic default field insertion, but with an optional popup of alternatives.

import sublime             
import sublime_plugin   
import os
from os.path import basename
import json
import glob
import re
import threading

class CommitNextFieldCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.run_command("commit_completion", {})
        self.view.run_command("next_field", {})
        self.view.run_command("auto_complete", {})


class TabIntoSnippetCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        print("*** Tab into snippet ***")
        self.view.run_command("commit_completion", {})
        self.view.run_command("auto_complete", {
            'disable_auto_insert': True, 
            'next_completion_if_showing': False
        })

class InsertFileNameCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        sel = self.view.substr(self.view.sel()[0])

        path = './'
        fname = self.view.file_name()
        if fname:
            path = os.path.dirname(fname)

        glist = glob.glob("%s/*%s*"%(path,sel))
        
        self.complist = [basename(x) for x in glist]

        sublime.active_window().show_quick_panel(self.complist,self.on_done)

    def on_done(self, index):
        self.view.run_command("insert_my_text", {"args":{'text':self.complist[index]}})

class InsertMyText(sublime_plugin.TextCommand):
    def run(self, edit, args):
        self.view.replace(edit, self.view.sel()[0], args['text'])

class ProcessComps(threading.Thread):
    def __init__(self):
        self.result = None
        threading.Thread.__init__(self)


    def run(self):
        # while True:
        self.result = None
        completion_sets = []
        completion_files = sublime.find_resources("*.cm-completions")       

        for c in completion_files:
            compldata = json.loads(sublime.load_resource(c) )
            completion_sets.append(compldata)

        self.result = completion_sets


class CompleteMagic(sublime_plugin.EventListener):
    def __init__(self):
        self.completion_sets = []

        updateCompletions = ProcessComps()
        updateCompletions.start()
        self.rereadCompletions(updateCompletions)


    def rereadCompletions(self, thread):
        if thread.is_alive():
            print ("reread is running")
            sublime.set_timeout(lambda: self.rereadCompletions(thread),100)            
            return

        print ("reread finished")
        self.completion_sets = thread.result


    def read_completions(self, scope):        
        for c in self.completion_sets:
            if c['scope'] in scope:
                return c

        return False


    def isFile(self, fname):        
        print(fname)
        return os.path.isfile(fname)


    def globComplete(self):
        pass


    def populate_autocomplete(self, prefix, completions, path=""):  
        complist = []
        if prefix == '':
            return complist

        for fieldname in completions['completions']:
            
            if (fieldname.lower().startswith(prefix.lower())):                
                globchars = set("*?[]|")
                for completion in completions['completions'][fieldname]:
                    if not any((c in globchars) for c in completion) :
                        complist.append(("%s: %s"%(fieldname, completion), completion))                    
                    else:                        
                        glist = glob.glob(path+"/"+completion)
                        complist = complist + [("%s\t%s"%
                            (fieldname, basename(x)), basename(x)) for x in glist]

        if re.search('_-\w{3}',prefix):
            ext = prefix[-3:]
            print (path+"/*."+ext)
            glist = glob.glob(path+"/*"+ext+'*')
            complist = complist + [("%s: %s"%(prefix, basename(x)), basename(x)) for x in glist]

        return complist

                
    def on_query_completions(self, view, prefix, locations):

        # print("Prefix>"+prefix+"<EndPrefix")
        # print (view.extract_completions(prefix))
        # print (view.command_history(0))
        
        path = './'
        scope_name = view.scope_name(0)   
        compldata = self.read_completions(scope_name)
        fname = view.file_name()
        if fname:
            path = os.path.dirname(fname)
        
        if compldata:           
            clist = self.populate_autocomplete(prefix, compldata, path)
            return clist

    # def on_query_context(self, view, key, operator, operand, match_all):
    #     print ("QUERY CONTEXT")

    # def on_window_command(self,window,name,args):
    #     print(name+" :: "+str(args))