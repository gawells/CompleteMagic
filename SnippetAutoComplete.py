
# This Python file uses the following encoding: utf-8
#-----------------------------------------------------------------------------------
# Snippet Auto-Complete
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

class SnippetAutoComplete(sublime_plugin.EventListener):
    saved = False

    def read_completions(self, scope):
        completion_files = sublime.find_resources("*.snippet-completions")       

        for c in completion_files:
            compldata = json.loads(sublime.load_resource(c) )

            if compldata['scope'] in scope:
                return compldata

        return False

    def isFile(self, fname):        
        print(fname)
        return os.path.isfile(fname)

    def globComplete(self):
        pass

    def populate_autocomplete(self, prefix, completions, path=""):  
        complist = []
        for fieldname in completions['completions']:
            
            if (fieldname.lower().startswith(prefix.lower())):                
                globchars = set("*?[]|")
                for completion in completions['completions'][fieldname]:
                    if not any((c in globchars) for c in completion) :
                        complist.append(("%s: %s"%(fieldname, completion), completion))                    
                    else:                        
                        glist = glob.glob(path+"/"+completion)
                        complist = complist + [("%s: %s"%
                            (fieldname, basename(x)), basename(x)) for x in glist]

        if re.search('_-\w{3}',prefix):
            ext = prefix[-3:]
            print (path+"/*."+ext)
            glist = glob.glob(path+"/*"+ext+'*')
            complist = complist + [("%s: %s"%(prefix, basename(x)), basename(x)) for x in glist]
            print (complist)

        complist.append(("nested","true"))  
        return complist

                
    def on_query_completions(self, view, prefix, locations):

        path = './'
        scope_name = view.scope_name(0)   
        compldata = self.read_completions(scope_name)
        fname = view.file_name()
        if fname:
            path = os.path.dirname(fname)
            saved = True
        
        print(prefix)

        if compldata:           
            clist = self.populate_autocomplete(prefix, compldata, path)

            return clist
                    