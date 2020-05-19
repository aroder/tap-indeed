# properties:
#   key_properties: the fields that uniquely identify a record

STREAMS = {
    # temporary, using for testing
    'data_from_file': {
        'key_properties': ['query', 'location'],
        'replication_method': 'FULL_TABLE',
        'default_selected_fields': []
    },
    # a list of openings by location for each query/search term
    'openings_counts': {
        'key_properties': ['measured_date', 'query', 'location'], # singer property, indicates which fields are they key
        'replication_method': 'FULL_TABLE', # singer property
        'default_selected_fields': ['openings_count', '__sdc_extracted_at', '__sdc_sequence'] # we use this to populate the singer metadata property selected-by-default. We could repeat the key properties above, but it is unnecessary

    }
}