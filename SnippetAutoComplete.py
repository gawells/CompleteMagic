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
from os.path import basename
import json
import glob

class SnippetAutoComplete(sublime_plugin.EventListener):
    settings = None
    b_first_edit = True
    b_fully_loaded = True
    word_list = []
    complD = None

    def should_trigger(self, scope):
        completion_files = sublime.find_resources("*.snippet-completions")

        for c in completion_files:
            compldata = json.loads(sublime.load_resource(c) )

            if compldata['scope'] in scope:
                complD = compldata
                return compldata

        return False

    def populate_autocomplete(self,prefix,completions,path=""):  
        complist = []
        for fieldname in completions['completions']:
            if (fieldname.lower().startswith(prefix.lower())):
            # if prefix.lower().startswith(fieldname.lower()): # don't understand why this doesn't work after first character
                complist = []
                for completion in completions['completions'][fieldname]:
                    if not "*" in completion:
                        complist.append(("%s: %s"%(fieldname,completion),completion))                    
                    else:                        
                        glist = glob.glob(path+"/"+completion)
                        complist = complist + [("%s: %s"%(fieldname,basename(x)),basename(x)) for x in glist]
                return complist

    def on_query_completions(self, view, prefix, locations):
        scope_name = view.scope_name(0)   
        compldata = self.should_trigger(scope_name)
        fname = view.file_name()
        path = os.path.dirname(fname)

        if compldata:           
            return self.populate_autocomplete(prefix,compldata,path)
                    