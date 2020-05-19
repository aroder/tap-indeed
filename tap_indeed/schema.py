import os
import json
from singer import metadata
from tap_indeed.streams import STREAMS

# Reference:
# https://github.com/singer-io/getting-started/blob/master/docs/DISCOVERY_MODE.md#Metadata

def get_abs_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)

def get_schemas():
    schemas = {}
    field_metadata = {}

    for stream_name, stream_metadata in STREAMS.items():
        schema_path = get_abs_path('schemas/{}.json'.format(stream_name))
        with open(schema_path) as file:
            schema = json.load(file)
        schemas[stream_name] = schema
        mdata = metadata.new()

        # Documentation:
        # https://github.com/singer-io/getting-started/blob/master/docs/DISCOVERY_MODE.md#singer-python-helper-functions
        # Reference:
        # https://github.com/singer-io/singer-python/blob/master/singer/metadata.py#L25-L44
        # mdata = metadata.get_standard_metadata(
        mdata = get_standard_metadata(
            schema=schema,
            key_properties=stream_metadata.get('key_properties', None),
            valid_replication_keys=stream_metadata.get('replication_keys', None),
            replication_method=stream_metadata.get('replication_method', None),

        )

        for field in stream_metadata['default_selected_fields']:
            write(mdata, ('properties', field), 'selected', 'true')

        field_metadata[stream_name] = to_list(mdata)

    return schemas, field_metadata

def write(mdata, breadcrumb, k, val):
    if val is None:
        raise Exception()
    if breadcrumb in mdata:
        mdata.get(breadcrumb).update({k: val})
    else:
        mdata[breadcrumb] = {k: val}
    return mdata

def get_standard_metadata(schema=None, schema_name=None, key_properties=None,
                          valid_replication_keys=None, replication_method=None):
    mdata = {}

    if key_properties is not None:
        mdata = write(mdata, (), 'table-key-properties', key_properties)
    if replication_method:
        mdata = write(mdata, (), 'forced-replication-method', replication_method)
    if valid_replication_keys is not None:
        mdata = write(mdata, (), 'valid-replication-keys', valid_replication_keys)
    if schema:
        mdata = write(mdata, (), 'inclusion', 'available')

        if schema_name:
            mdata = write(mdata, (), 'schema-name', schema_name)
        for field_name in schema['properties'].keys():
            if key_properties and field_name in key_properties:
                mdata = write(mdata, ('properties', field_name), 'inclusion', 'automatic')
            else:
                mdata = write(mdata, ('properties', field_name), 'inclusion', 'available')

    return mdata
    # return to_list(mdata)

def to_list(compiled_metadata):
    return [{'breadcrumb': k, 'metadata': v} for k, v in compiled_metadata.items()]