# properties:
#   key_properties: the fields that uniquely identify a record

STREAMS = {
    # temporary, using for testing
    'data_from_file': {
        'key_properties': ['query', 'location'],
        'replication_method': 'FULL_TABLE'
    },
    # a list of openings by location for each query/search term
    'openings_counts': {
        'key_properties': ['query', 'location'],
        'replication_method': 'FULL_TABLE'
    }
}