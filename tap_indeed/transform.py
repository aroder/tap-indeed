def transform_record(stream_name, record):
    if stream_name == 'data_from_file':
        r = record
        r['openings_count'] = int(record['openings_count'])
    else:
        r = record
    return r