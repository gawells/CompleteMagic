# CompleteMagic

Sublime Text 3 plugin for custom autocomplete lists. 

In addition to generating boilerplate code, snippets are useful for generating input files for scientific software and batch queue submissions. However, I wanted to be able to select from predefined lists during snippet completion, and Sublime only allows for one default value in a field. Hence this plugin: placeholder values for snippet fields are used to trigger custom autocomplete lists via api-injection. Custom lists are stored in json formatted files with the `.cm-completions` extension as `"prefix":[array]` pairs. As you tab into each field of a snippet, the autocomplete popup is triggered with the appropriate custom list. These lists will be triggered during normal typing as well, therefore it may be more convenient to limit them to custom scope definitions (see below)

Additional functionality includes the insertion of filenames from the current directory, either by entering: `\_-xyz` which will glob for **xyz*) or by selecting a more complex pattern (sublime only recognises alphanumeric + "_" for autocomplete triggers) and running the `insert_file_name command`.

### Demo

![animation](https://github.com/gawells/demos/blob/master/complM-demo1.gif)

### .cm-completions example
The following completions operate in conjunction with a snippet designed for torque/maui batch queue submission, stored in something like `<sublime-user-config>/Packages/User/CustomCompletions/qsub.cm-completions`. The scope `source.pbs` is derived from `source.shell` to use the `.pbs` file extension.

#### Completions file
```
{
        "scope" : "source.pbs",
        "completions" : {
                "PBS" : ["PBS_O_QUEUE",
                "PBS_QUEUE",
                "PBS_JOBID",
                "PBS_JOBNAME",
                "PBS_NODEFILE",
                "PBS_ARRAYID",
                "PBS_VNODENUM",
                "PBS_O_PATH",
                "PBS_O_WORKDIR",
                "PBS_NUM_PPN"],
                "runmsj":[" "],
                "nodenumber":["1","2","4","8","16","32","64"],
                "ppnnumber":["0","1","2","4","8","16","32","64"],
                "jobtimehours":["0","1","2","4","8","12","24"],
                "jobtimedays":["1","2","4","7","14","21","28"],
                "allcfg":["*.cfg"],
                "allmsj":["*.msj"],
                "allcms":["*.cms"],
                "allcpt":["*.cpt"],
                "allnamd":["*.namd"]
        }
}


```

#### Snippet example
An example snippet that triggers the completions described above. Take note of the `#${n:endsnippet}` field, which the plugin uses to prevent a popup being triggered when tabbing out of snippet (Otherwise Sublime pops up a list using it's own internal completion logic for an empty string).
```
<snippet>
        <content><![CDATA[
export SCHRODINGER_RSH=/usr/bin/ssh
export SCHRODINGER_RCP=/usr/bin/scp
export SCHRODINGER=/opt/Desmond_2014.2
export SCHRODINGER_NICE=yes
export SCHRODINGER_TMPDIR=/home/user/dscratch

\$SCHRODINGER/utilities/multisim -WAIT \\
        -JOBNAME ${1:runmsj} \\
        -HOST ${2:localhost} \\
        -cpu ${3:\$PBS_NUM_PPN} \\
        -mode umbrella \\
        -m ${4:allmsj} \\
        ${5:allcms} \\
        -o ${1}-out.cms

#${6:endsnip}
]]></content>
        <!-- <tabTrigger>desmond-msj</tabTrigger> -->
        <!-- Optional: Set a tabTrigger to define how to trigger the snippet -->
        <tabTrigger>msj_caf</tabTrigger>
        <!-- Optional: Set a scope to limit where the snippet will trigger -->
        <scope>source.pbs</scope>
</snippet>
```

### Keybindings
In order for the auto-complete menu to be triggered when pressing tab you need a corresponding `Default.sublime-keymap` file to bind the appropriate `CompleteMagic` functions. In this example I use a syntax for `.pbs` that is a `source.shell` derivative (saved in `<sublime-user-config>/Packages/User/pbs`):
```
[                                                                                                                                                  
        { "keys": ["tab"], "command": "tab_into_snippet", "context":
            [
                    { "key": "auto_complete_visible" },
                    { "key": "setting.auto_complete_commit_on_tab" },
                    { "key": "selector", "operator": "equal", "operand": "source.pb"s}
            ]
        },

        { "keys": ["tab"], "command": "commit_next_field", "context":
            [
                    { "key": "has_next_field", "operator": "equal", "operand": true },
                    { "key": "selector", "operator": "equal", "operand": "source.pbs"},
                    { "key": "text", "operator": "not_regex_contains", "operand": "endsnip"},
                    { "key": "selector", "operator": "equal", "operand": "source.pb"s}
            ]
        },

        { "keys": ["enter"], "command": "commit_completion", "context":
            [
                    { "key": "auto_complete_visible" },
                    { "key": "setting.auto_complete_commit_on_tab"}
                    { "key": "selector", "operator": "equal", "operand": "source.pb"s}
            ]
        },
        
        { "keys": ["ctrl+alt+i"], "command": "insert_file_name"
    		[
    			{ "key": "selector", "operator": "equal", "operand": "source.pbs"}
    		]
        },
]

```

