import json
import sys
import os

import singer
from singer.catalog import Catalog, CatalogEntry, Schema

from tap_indeed.schema import get_schemas, STREAMS

LOGGER = singer.get_logger()

def do_discover():
    LOGGER.info('Starting discover')
    catalog = discover()
    catalog.dump()
    LOGGER.info('Finished discover')

def discover():
    schemas, field_metadata = get_schemas()
    catalog = Catalog([])

    for stream_name, schema_dict in schemas.items():
        schema = Schema.from_dict(schema_dict)
        mdata = field_metadata[stream_name]

        catalog.streams.append(CatalogEntry(
            stream=stream_name,
            tap_stream_id=stream_name,
            key_properties=STREAMS[stream_name]['key_properties'],
            schema=schema,
            metadata=mdata
        ))

    return catalog


# def discover():
#     raw_schemas = load_schemas()
#     streams = []
#     for stream_id, schema in raw_schemas.items():
#         # TODO: populate any metadata and stream's key properties here..
#         stream_metadata = []
#         key_properties = []
#         streams.append(
#             CatalogEntry(
#                 tap_stream_id=stream_id,
#                 stream=stream_id,
#                 schema=schema,
#                 key_properties=key_properties,
#                 metadata=stream_metadata,
#                 replication_key=None,
#                 is_view=None,
#                 database=None,
#                 table=None,
#                 row_count=None,
#                 stream_alias=None,
#                 replication_method=None,
#             )
#         )
#     return Catalog(streams)