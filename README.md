# CompleteMagic
Sublime Text 3 plugin for custom autocomplete lists. 

Originally intended to augment placeholder values for snippet fields with custom lists of default values. Custom 
lists are store in json files with the .cm-completions extension as prefix:array pairs. As you tab into each field 
of a snippet, the autocomplete popup is triggered with the appropriate custom list. These lists will be triggered
during normal typing as well.

Additional functionality includes the insertion of filenames from the current directory, either by entering:
"\_-xyz" which will glob for *xyz* or by selecting a more complex pattern (sublime only recognises alphanumeric + "_" 
for autocomplete triggers) and running the insert_file_name command.
