vport_expressions = {
   "secure scaleout": {
      'regex': '^secure',
      'json': {
          'scaleout-bucket-count': 128
      }
   }
}

virtual_server_expressions = {
   "described": {
        'regex': '^desc',
        'json': {
            'description': 'Described from the name'
            }
        }
}

service_group_expressions = {
  "mon1": {
    'regex': '^mon',
    'json': {
      "health-check": "mon1"
    }
  }
}

member_expressions = {
  "connections42": {
    'regex': '^connlimit',
    'json': {
        "conn-limit": 4200
    }
  }
}

monitor_expressions = {
    "monitor": {
        "regex": "^tagged",
        "json": {
            "user-tag": 42
        }
    }
}
