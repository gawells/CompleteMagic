
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
import re

class SnippetAutoComplete(sublime_plugin.EventListener):
    complD = None

    def read_completions(self, scope):
        completion_files = sublime.find_resources("*.snippet-completions")       

        for c in completion_files:
            compldata = json.loads(sublime.load_resource(c) )

            if compldata['scope'] in scope:
                complD = compldata
                return compldata

        return False

    def isFile(self,fname):        
        print(fname)
        return os.path.isfile(fname)

    def populate_autocomplete(self,prefix,completions,path=""):  
        complist = []
        for fieldname in completions['completions']:
            
            # if fieldname.lower() == prefix.lower():
            # complist = []
            if (fieldname.lower().startswith(prefix.lower())):                
                globchars = set("*?[]|")
                for completion in completions['completions'][fieldname]:
                    if not any((c in globchars) for c in completion) :
                        complist.append(("%s: %s"%(fieldname,completion),completion))                    
                    else:                        
                        glist = glob.glob(path+"/"+completion)
                        complist = complist + [("%s: %s"%(fieldname,basename(x)),basename(x)) for x in glist]

            elif re.search('__all\w{3}',prefix):
                ext = prefix[-3:]
                print (path+"/*."+ext)
                glist = glob.glob(path+"/*."+ext)
                complist = complist + [("%s: %s"%(prefix,basename(x)),basename(x)) for x in glist]
                print (complist)
                # print (complist)
                # return complist
            # elif (fieldname.lower().startswith(prefix.lower())):
            #     print (fieldname)
            #     complist.append((fieldname,fieldname))
        
        # print (complist)  
        complist.append(("nested","true"))  
        return complist

                
    def on_query_completions(self, view, prefix, locations):
        # print (self.isFile(prefix))
        scope_name = view.scope_name(0)   
        compldata = self.read_completions(scope_name)
        fname = view.file_name()
        path = os.path.dirname(fname)
        print(prefix)

        if compldata:           
            clist = self.populate_autocomplete(prefix,compldata,path)
            # print (clist) 
            # if (clist[-1][0] == "nested"):
            #     pass
                # how do I retrigger the popup?
                # view.run_command("auto_complete") # crashes

            return clist
                    