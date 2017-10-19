import json

settings_json = json.dumps([
    {'type': 'options',
     'title': 'Start Sequence',
     'desc':'Choose the type of start sequence',
     'options': ['5, 4, 1, Go', '6, 3, 1, Go', '6, 3, Go', '3, 2, 1, Go','1, Go'],
     'section': 'Race settings',
     'key': 'sequence'
    },
    {'type': 'numeric',
     'title': 'Number of starts',
     'desc': 'Number of back to back starts in sequence (max 4)',
     'section': 'Race settings',
     'key': 'nstarts'
     },
    {'type': 'numeric',
     'title': 'Time between starts (minutes)',
     'desc': 'Time between starts in minutes',
     'section': 'Race settings',
     'key' : 'interval'
     },
    {'type': 'bool',
     'title': 'Add extra minute before first start',
     'desc': 'e.g. After postponement down?',
     'section' : 'Race settings',
     'key' : 'add_minute'},
    {'type': 'options',
     'title': 'General Recall Option',
     'desc':'Choose behaviour for general recalls if multiple starts',
     'options': ['Move start to end', 'Reset Current and later starts'],
     'section': 'Race settings',
     'key': 'recall'
    }
    ])