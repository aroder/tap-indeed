import csv

import singer

from tap_indeed.client.indeed import IndeedClient
from tap_indeed.streams import STREAMS
from tap_indeed.transform import transform_record

LOGGER = singer.get_logger()


def do_sync(config, state, catalog):
    selected_streams = [
        stream.stream for stream in catalog.get_selected_streams(state)]
    if not selected_streams or len(selected_streams) == 0:
        LOGGER.warning(
            f'No streams were selected for streaming; selected_streams was None')
    LOGGER.info(
        f'Will sync {len(selected_streams)} streams: {", ".join(selected_streams)}')

    for stream_name, stream_config in STREAMS.items():
        if stream_name in selected_streams:
            LOGGER.info(f'START syncing stream: {stream_name}')
            update_currently_syncing(state, stream_name)
            total_records = sync_stream(config, catalog, state, stream_name)
            update_currently_syncing(state, None)
            LOGGER.info(
                f'FINISHED syncing stream: {stream_name}, total_records: {total_records}')


def sync_stream(config, catalog, state, stream_name):
    time_extracted = singer.utils.now()
    total_records = 0
    write_schema(catalog, stream_name)

    selected_fields = get_selected_fields(catalog, stream_name)
    LOGGER.info(f'Stream: {stream_name}, selected_fields: {selected_fields}')

    if (stream_name == 'data_from_file'):
        counter = 0
        with open('./sample_data.csv') as f:
            reader = csv.reader(f, delimiter=',')
            headers = next(reader)
            records = []
            for row in reader:
                record = {headers[idx]: field for idx, field in enumerate(row)}
                records.append(transform_record(stream_name, record))
            record_count = process_record_batch(catalog, state, stream_name, records, time_extracted)
        LOGGER.info(
            f'Stream {stream_name} batch processed {record_count} records')
        total_records = total_records + record_count

    elif stream_name == 'openings_counts':
        client = IndeedClient(locations=config['locations'], queries=config['queries'])
        with singer.metrics.record_counter(stream_name) as counter:
            for record in client.extract():
                process_record(catalog, state, stream_name, record, time_extracted)
                counter.increment()
            total_records = counter.value
        
    else:
        raise Error('not yet implemented')

    if total_records == 0:
        LOGGER.warning(f'NO NEW DATA FOR {stream_name}')
    return total_records


def process_record_batch(catalog, state, stream_name, records, time_extracted):
    stream = catalog.get_stream(stream_name)
    schema = stream.schema.to_dict()
    stream_metadata = singer.metadata.to_map(stream.metadata)

    with singer.metrics.record_counter(stream_name) as counter:
        for rec in records:
            with singer.Transformer() as transformer:
                try:
                    transformed_record = transformer.transform(
                        rec, schema, stream_metadata)
                except Exception as err:
                    LOGGER.error(f'Transformer error: {err}, stream: {stream}')
                    LOGGER.error(f'record: {record}')

                write_record(stream_name, transformed_record, time_extracted)
                counter.increment()
        return counter.value

def process_record(catalog, state, stream_name, record, time_extracted):
    stream = catalog.get_stream(stream_name)
    schema = stream.schema.to_dict()
    stream_metadata = singer.metadata.to_map(stream.metadata)
    with singer.Transformer() as transformer:
        try:
            transformed_record = transformer.transform(
                record, schema, stream_metadata)
            write_record(stream_name, transformed_record, time_extracted)
        except Exception as err:
            LOGGER.error(f'Transformer error: {err}, stream: {stream}')
            LOGGER.error(f'record: {record}')



def write_record(stream_name, record, time_extracted):
    try:
        singer.messages.write_record(
            stream_name=stream_name,
            record=record,
            time_extracted=time_extracted
        )
    except OSError as err:
        LOGGER.error(f'OSError writing record for stream {stream_name}')
        LOGGER.error(f'record: {record}')

# Currently syncing sets the stream currently being delivered in the state.
# If the integration is interrupted, this state property is used to identify
#  the starting point to continue from.
# Reference: https://github.com/singer-io/singer-python/blob/master/singer/bookmarks.py#L41-L46


def update_currently_syncing(state, stream_name):
    if (stream_name is None) and ('currently_syncing' in state):
        del state['currently_syncing']
    else:
        singer.set_currently_syncing(state, stream_name)
    singer.write_state(state)


def write_schema(catalog, stream_name):
    stream = catalog.get_stream(stream_name)
    schema = stream.schema.to_dict()
    try:
        singer.write_schema(stream_name, schema, stream.key_properties)
    except OSError as err:
        LOGGER.error('OS Error writing schema for: {}'.format(stream_name))
        raise err


# List selected fields from stream catalog
def get_selected_fields(catalog, stream_name):
    stream = catalog.get_stream(stream_name)
    mdata = singer.metadata.to_map(stream.metadata)
    mdata_list = singer.metadata.to_list(mdata)
    selected_fields = []
    for entry in mdata_list:
        field = None
        try:
            field = entry['breadcrumb'][1]
            if entry.get('metadata', {}).get('selected', False):
                selected_fields.append(field)
        except IndexError:
            pass
    return selected_fields


def write_bookmark(state, stream, value):
    if 'bookmarks' not in state:
        state['bookmarks'] = {}
    state['bookmarks'][stream] = value
    LOGGER.info('Write state for stream: {}, value: {}'.format(stream, value))
    singer.write_state(state)