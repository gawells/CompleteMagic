# This Python file uses the following encoding: utf-8
#-----------------------------------------------------------------------------------
# Snippet Auto-Complete
#-----------------------------------------------------------------------------------
#
# Modified from DictionaryAutocomplete by (c) Florian Zinggeler
#-----------------------------------------------------------------------------------
import sublime             
import sublime_plugin   

ST3 = int(sublime.version()) > 3000

import os


class SnippetAutoComplete(sublime_plugin.EventListener):
    settings = None
    b_first_edit = True
    b_fully_loaded = True
    word_list = []

    # on first modification in comments, get the dictionary and save items.
    def on_modified(self, view):
        if self.b_first_edit and self.b_fully_loaded:
            self.b_fully_loaded = False
            sublime.set_timeout(lambda: self.load_completions(view), 3)

    def load_completions(self, view):
        scope_name = view.scope_name(view.sel()[0].begin())       # sublime.windows()[0].active_view()
        if self.should_trigger(scope_name):
            if not self.settings:
                self.settings = sublime.load_settings('Preferences.sublime-settings')
                encoding = sublime.load_settings('SnippetAutoComplete.sublime-settings').get('encoding')
                if ST3:
                    words = sublime.load_binary_resource(self.settings.get('dictionary')).decode(encoding).splitlines()
                    for word in words:
                        word = word.split('/')[0].split('\t')[0]
                        self.word_list.append(word)
                elif not ST3:
                    self.dict_path = os.path.join(sublime.packages_path()[:-9], self.settings.get('dictionary'))
                    with open(self.dict_path, 'r') as dictionary:
                        words = dictionary.read().decode(encoding).splitlines()
                        for word in words:
                            word = word.split('/')[0].split('\t')[0]
                            self.word_list.append(word)
                self.b_first_edit = False
        else:
            self.b_fully_loaded = True

    # This will return all words found in the dictionary
    def get_autocomplete_list(self, word):
        autocomplete_list = []
        # filter relevant items:
        for w in self.word_list:
            try:
                if word.lower() in w.lower():
                    if len(word) > 0 and word[0].isupper():
                        W = w.title()
                        autocomplete_list.append((W, W))
                    else:
                        autocomplete_list.append((w, w))
            except UnicodeDecodeError:
                print(w)
                # autocomplete_list.append((w, w))
                continue

        return autocomplete_list

    def should_trigger(self, scope):
        return True
        if "comment" in scope or "string.quoted" in scope or "text" == scope[:4]:
            return True
        return False

    # gets called when auto-completion pops up.
    def on_query_completions(self, view, prefix, locations):
        scope_name = sublime.windows()[0].active_view().scope_name(sublime.windows()[0].active_view().sel()[0].begin())
        
        if self.should_trigger(scope_name):
            if "trigger".lower() in prefix.lower():
                print ('Triggered')
                return [('trigger1','trigger1a'),('trigger3','trigger3'),('trigger4','arb')] ##why can't I make the list arbitrary??
            elif "hostname".lower() in prefix.lower():
                return [('hostname: riddley','riddley'),('hostname: fx8150','fx8150'),('trigger4','arb')] 
            else:
                return self.get_autocomplete_list(prefix)
                pass
    