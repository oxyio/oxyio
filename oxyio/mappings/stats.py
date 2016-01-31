# oxy.io
# File: oxyio/mappings/stats.js
# Desc: stats mappings

object_stat_mapping = {
    'object_stat': {
        'dynamic': False,
        '_all': {
            'enabled': False
        },
        'properties': {
            'object_id': {
                'type': 'integer'
            },
            'object_module': {
                'type': 'string',
                'index': 'not_analyzed'
            },
            'object_type': {
                'type': 'string',
                'index': 'not_analyzed'
            },
            'datetime': {
                'type': 'date',
                'format': 'dateOptionalTime'
            },
            'type': {
                'type': 'string',
                'index': 'not_analyzed'
            },
            'key': {
                'type': 'string',
                'index': 'not_analyzed'
            },
            'detail': {
                'type': 'string',
                'index': 'not_analyzed'
            },
            'value': {
                'type': 'integer'
            }
        }
    }
}
