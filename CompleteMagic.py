# This Python file uses the following encoding: utf-8
#-----------------------------------------------------------------------------------
# CompleteMagic
#-----------------------------------------------------------------------------------
#
# Originally derived from DictionaryAutocomplete by (c) Florian Zinggeler, now much 
# altered
#-----------------------------------------------------------------------------------

import sublime             
import sublime_plugin   
import os
import json
import glob
import re
import threading
import logging
import subprocess

from os.path import basename

PLUGIN_SETTINGS = sublime.load_settings("CompleteMagic.sublime-settings")
DEBUG = PLUGIN_SETTINGS.get("debug", False)

logging.basicConfig(format='%(message)s ')
logger = logging.getLogger(__name__)

if (DEBUG):
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.WARNING)

class ZshMagicCommand(sublime_plugin.TextCommand):
    
    def command_till_loc(self,cstr,pos):
        get_start = re.compile(r'[^\s^\n]+[$\w]+.+')
        stripnewline = (re.sub(r'^\n+','',cstr[0:pos]))
        self.partial_command = stripnewline

        path = './'
        fname = self.view.file_name()
        if fname:
            path = os.path.dirname(fname)
            os.chdir(path)

        proc = subprocess.Popen(["capture.zsh", self.partial_command], stdout=subprocess.PIPE)
        out = proc.communicate()[0]
        return out.decode("utf-8")


    def run(self,edit):
        script = self.view.substr(sublime.Region(0, self.view.size()))
        self.view.run_command("show_scope_name",{})
        loc = self.view.sel()[0].end()
        logger.debug("CompletMagic: Cursor position: %s"%loc)

        regex = re.compile(
            r'^[^#][\w\s]+(.+\\\s*\n)*'
            r'(.*(\n|\Z))',re.M
            )

        for prog_instance in regex.finditer(script):
            beg = prog_instance.start(0)
            end = prog_instance.end(0)

            if (loc >= beg) and (loc <= end):
                current_command = prog_instance.group(0)
                zsh_captures = self.command_till_loc(current_command,loc-beg)
                self.capture_list = zsh_captures.split('\r\n')
                prefix = script[loc-5:loc]
                # complist = [("%s: %s"%(prefix, x), x) for x in capture_list]

                sublime.active_window().show_quick_panel(self.capture_list,self.on_done)

    def on_done(self, index):
        # new_command = self.current_command + self.capture_list[index] # attempt to be more shell like
        self.view.run_command("insert_my_text", {"args":{'text':self.capture_list[index]}})


class CommitNextFieldCommand(sublime_plugin.TextCommand):
    '''
    Command to commit completion, move to next field, and call autocomplete
    popout within a snippet. To be bound to the tab key, preferably inside
    a user-defined syntax to prevent unexpected behaviour in normal shell/
    programming syntaxes.
    '''

    def run(self, edit):
        self.view.run_command("commit_completion", {})
        self.view.run_command("next_field", {})
        self.view.run_command("auto_complete", {
            'disable_auto_insert': True, 
            'next_completion_if_showing': False
        })


class TabIntoSnippetCommand(sublime_plugin.TextCommand):
    '''
    Command to commit completion, and call autocomplete popout within the 
    first field of a snippet. To be bound to the tab key, preferably inside
    a user-defined syntax to prevent unexpected behaviour in normal shell/
    programming syntaxes. Unfortunately this overrides the commit completion
    on autocomplete visible condition for hitting tab. There doesn't seem to
    be an appropriate event listener (e.g. on_commit_completion) to separate
    the two conditions.

    '''
    
    def run(self, edit):
        logger.debug("CompletMagic: *** Tab into snippet ***")
        self.view.run_command("commit_completion", {})
        self.view.run_command("auto_complete", {
            'disable_auto_insert': True, 
            'next_completion_if_showing': False
        })


class InsertFileNameCommand(sublime_plugin.TextCommand):
    '''
    Type and select a glob, then run this command to pull up list of matching
    files in a quick-panel, choose file and hit enter to replace the selected 
    text. Because autocomplete only matches alphanumerics + '_' for its triggering
    prefix, it doesn't seem to be possible to do this via the autocomplete popout. 
    '''
    
    def run(self, edit):
        sel = self.view.substr(self.view.sel()[0])
        globchars = set("*?[]|")

        path = './'
        fname = self.view.file_name()
        absolute = False
        if sel[0] == '/': 
            path = ''
            absolute = True
        elif fname:
            path = os.path.dirname(fname)

        if not any((c in globchars) for c in sel) :
            glist = glob.glob("%s/*%s*"%(path,sel))        
        else:
            glist = glob.glob("%s/%s"%(path,sel)) 
        
        if absolute:            
            self.complist = [re.sub('\/+','/',x)  for x in glist]
        else:        
            self.complist = [os.path.relpath(x,path) for x in glist]
            # self.complist = [os.path.relpath(x,path)+basename(x) for x in glist]

        sublime.active_window().show_quick_panel(self.complist,self.on_done)

    def on_done(self, index):        
        self.view.run_command("insert_my_text", {"args":{'text':self.complist[index]}})

class InsertMyText(sublime_plugin.TextCommand):
    '''
    Command to insert filename from glob list via InsertFileNameCommand
    '''
    
    def run(self, edit, args):
        for s in self.view.sel():
            self.view.replace(edit, s, args['text'])


class InsertCmdLine(sublime_plugin.TextCommand):
    '''
    Command to insert filename from glob list via InsertFileNameCommand
    '''
    
    def run(self, edit, args):
        for s in self.view.sel():
            line = self.view.line(s)
            print (line)
            # if s.empty():    
            self.view.replace(edit, s, args['text'])


class ProcessComps(threading.Thread):
    '''
    Background thread to read user-defined completions
    '''

    def __init__(self):
        self.result = None
        threading.Thread.__init__(self)


    def run(self):
        self.result = None
        self.completion_sets = []
        completion_files = sublime.find_resources("*.cm-completions")       
        logger.debug("CompletMagic: reading completion files %s"%completion_files)

        for c in completion_files:
            logger.debug("CompletMagic, loading completion set: "+c)
            compldata = json.loads(sublime.load_resource(c) )
            # logger.debug(compldata)
            self.completion_sets.append(compldata)

        self.result = self.completion_sets


class RereadCompletionsCommand(sublime_plugin.TextCommand):
    '''
    Only way I can think of to do this. Would like to have a thread
    watching for changes to .cm-copmletions files
    '''
   
    def run(self, edit):
        sublime_plugin.reload_plugin("CompleteMagic.CompleteMagic")


class CompleteMagic(sublime_plugin.EventListener):
    def __init__(self):
        logger.debug("CompletMagic: Initializing")
        updateCompletions = ProcessComps()
        updateCompletions.start()
        self.loadCompletions(updateCompletions)


    def loadCompletions(self, thread):
        '''
        Load user defined completions into array
        '''

        if thread.is_alive():
            logger.debug("CompletMagic: reread is running")
            sublime.set_timeout(lambda: self.loadCompletions(thread),100)            
            return

        logger.debug("CompletMagic: reread finished")
        self.completion_sets = thread.result
        # logger.debug(self.completion_sets)


    def read_completions(self, scope):
        '''
        Return completion set for current scope
        '''        

        completions = []

        for c in self.completion_sets:
            if c['scope'] in scope:
                logger.debug("CompletMagic, scope: %s"%c['scope'])
                completions.append(c)
                # return c

        if len(completions ) > 0:
            return completions
        else:
            return False


    def isFile(self, fname):        
        return os.path.isfile(fname)


    def populate_autocomplete(self, prefix, completions, path=""):  
        '''
        Populate autocomplete triggered by prefix. Start of entry names must 
        match prefix, but associated text to be inserted can be anything
        '''

        complist = []
        if prefix == '':
            return complist

        # Fill autocomplete with .cm-completions derived entries
        for fieldname in completions['completions']:            
            if (fieldname.lower().startswith(prefix.lower())):                
                globchars = set("*?[]|")
                for completion in completions['completions'][fieldname]:
                    # Predefined list:
                    if not any((c in globchars) for c in completion) :
                        complist.append(("%s\t %s"%(fieldname, completion), completion))                    
                    # Predefined glob:
                    else:                        
                        glist = glob.glob(path+"/"+completion)
                        complist = complist + [("%s\t%s"%
                            (fieldname, basename(x)), basename(x)) for x in glist]
                
                logger.debug("CompleteMagic, predefined: "+str(complist))  

        # Trigger glob based autocomplete by typing _-xyz ( = *.xyz)
        # using '_-' because sublime considers them potential word characters, unlike './'

        # if re.search('_-\w{2}',prefix):
        if re.search('_-\w{2}',prefix):
            ext = prefix[-2:]
            glist = glob.glob(path+"/*"+ext+'*')
            logger.debug("CompleteMagic: glob insertion from %s -> %s"%(path,glist))
            complist = complist + [("%s: %s"%(prefix, basename(x)), basename(x)) for x in glist]

        return complist

                
    def on_query_completions(self, view, prefix, locations):
        '''
        Inject user-defined autocompletions
        '''

        path = './'
        scope_name = view.scope_name(0)   
        compldata = self.read_completions(scope_name)
        logger.debug("CompleteMagic, all completions: "+str(compldata))
        fname = view.file_name()
        if fname:
            path = os.path.dirname(fname)

        clist = []
        
        if compldata:           
            for compl in compldata:
                clist +=  self.populate_autocomplete(prefix, compl, path)
            
            return clist

