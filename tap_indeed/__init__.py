#!/usr/bin/env python3
import os
import json
import singer
from singer import utils, metadata
from singer.catalog import Catalog, CatalogEntry
from singer.schema import Schema

from tap_indeed.discover import do_discover
from tap_indeed.sync import do_sync


# REQUIRED_CONFIG_KEYS = ["start_date", "username", "password"]
REQUIRED_CONFIG_KEYS = []
LOGGER = singer.get_logger()


@utils.handle_top_exception(LOGGER)
def main():
    args = utils.parse_args(REQUIRED_CONFIG_KEYS)

    if args.discover:
        catalog = do_discover()
    else:  # Otherwise run in sync mode
        do_sync(args.config, args.state, args.catalog)


if __name__ == "__main__":
    main()
