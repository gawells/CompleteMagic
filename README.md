# CompleteMagic

Sublime Text 3 plugin for custom autocomplete lists. 

Originally intended to augment placeholder values for snippet fields with custom lists of default values. Custom 
lists are store in json files with the .cm-completions extension as prefix:array pairs. As you tab into each field 
of a snippet, the autocomplete popup is triggered with the appropriate custom list. These lists will be triggered
during normal typing as well.

Additional functionality includes the insertion of filenames from the current directory, either by entering:
"\_-xyz" which will glob for \*xyz\* or by selecting a more complex pattern (sublime only recognises alphanumeric + "_" 
for autocomplete triggers) and running the insert_file_name command.


![animation](https://github.com/gawells/CompleteMagic/blob/master/ani.gif)

### Keybindings
In order for the auto-complete menu to be triggered when pressing tab you need a corresponding `.sublime-keymap` file to bind the appropriate `CompleteMagic` functions. In this example I use a syntax for `.namd` that is a `source.tcl` derivative:
```
[
	{ "keys": ["tab"], "command": "tab_into_snippet", "context":
		[
			// { "key": "has_prev_field", "operator": "equal", "operand": false },
			// Prevent triggering of second autocomplete when last inserted word
			// matches snippet trigger etc
			{ "key": "auto_complete_visible" },
			{ "key": "setting.auto_complete_commit_on_tab" },
			{ "key": "selector", "operator": "equal", "operand": "source.namd"}
		]
	},

	{ "keys": ["tab"], "command": "commit_next_field", "context":
		[
			{ "key": "has_next_field", "operator": "equal", "operand": true },
			{ "key": "selector", "operator": "equal", "operand": "source.namd"},
			{ "key": "text", "operator": "not_regex_contains", "operand": "endsnip"},
		]
	},

	{ "keys": ["enter"], "command": "commit_completion", "context":
		[
			{ "key": "auto_complete_visible" },
			{ "key": "setting.auto_complete_commit_on_tab"}
		]
	},
	
	{ "keys": ["ctrl+alt+i"], "command": "insert_file_name"},

]
```

