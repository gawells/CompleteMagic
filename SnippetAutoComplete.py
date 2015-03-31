# This Python file uses the following encoding: utf-8
#-----------------------------------------------------------------------------------
# Snippet Auto-Complete
#-----------------------------------------------------------------------------------
#
# Modified from DictionaryAutocomplete by (c) Florian Zinggeler
#-----------------------------------------------------------------------------------
# is there some way to trigger the popup with non-matching strings? This would enable
# automatic default field insertion, but with an optional popup of alternatives.

import sublime             
import sublime_plugin   
import os
import json
import glob

class SnippetAutoComplete(sublime_plugin.EventListener):
    settings = None
    b_first_edit = True
    b_fully_loaded = True
    word_list = []

    def should_trigger(self, scope):
        completion_files = glob.glob("*.snippet-completions")
        for c in completion_files:
            with open(c) as data_file :
                compldata = json.load(data_file)
                if compldata['scope'] in scope:
                    return compldata

        return False

    def populate_autocomplete(self,prefix,completions):  
        complist = []
        for fieldname in completions['completions']:
            if fieldname.lower() in prefix.lower():
                complist = []
                for completion in completions['completions'][fieldname]:
                    complist.append(("%s: %s"%(fieldname,completion),completion))                    
                return complist

    def on_query_completions(self, view, prefix, locations):
        scope_name = sublime.windows()[0].active_view().scope_name(sublime.windows()[0].active_view().sel()[0].begin())       
        # print (scope_name)
        compldata = self.should_trigger(scope_name)

        if compldata:           
            return self.populate_autocomplete(prefix,compldata)

            