# oxy.io
# File: oxyio/tasks/index.py
# Desc: a task that batch indexes stats buffered in a Redis queue

import json
from datetime import date

from elasticsearch import helpers as es_helpers

from oxyio import settings
from oxyio.log import logger
from oxyio.app import redis_client, es_client
from oxyio.mappings.stats import object_stat_mapping

from .base import Task


class IndexStats(Task):
    NAME = 'core/index_stats'

    es_index = None

    def __init__(self):
        self.doc_buffer = []

    def start(self):
        '''
        Read stats from the Redis queue and append to internal buffer.
        '''

        while True:
            es_doc = redis_client.brpop(settings.REDIS_INDEX_QUEUE, 5)

            if es_doc:
                _, es_doc = es_doc
                es_doc = json.loads(es_doc)
                self.doc_buffer.append(es_doc)

            if len(self.doc_buffer) >= settings.ES_INDEX_BATCH:
                self.index()

    def stop(self):
        # Make sure we index anything left over
        self.index()

    def index(self):
        '''
        Actually indexes the current doc buffer in ES.
        '''

        logger.debug('Indexing {0} stats -> ES...'.format(len(self.doc_buffer)))

        # Make ES docs
        docs = [{
            '_index': self.get_index(),
            '_type': 'object_stat',
            '_source': es_source
        } for es_source in self.doc_buffer]

        n_inserted, errors = es_helpers.bulk(es_client, docs)

        logger.info('Indexed {0} stats -> ES'.format(n_inserted))

        for error in errors:
            logger.error('Error inserting ES doc: {0}'.format(error))

        # Reset the buffer
        self.doc_buffer = []

    def get_index(self):
        '''
        Returns the current (daily) index, after ensuring it exists.
        '''

        # Get the index name
        today = date.today().strftime('%Y%m%d')
        index_name = '{0}_{1}'.format(settings.ES_STATS_INDEX, today)

        # Does our cached index check match
        if self.es_index == index_name:
            return index_name

        # Check the index exists
        if not es_client.indices.exists(index=index_name):
            # Create index, put mappings
            es_client.indices.create(index=index_name)
            es_client.indices.put_mapping(
                index=index_name,
                doc_type='object_stat',
                body=object_stat_mapping
            )

            # Update the alias
            es_client.indices.put_alias(
                name=settings.ES_STATS_INDEX,
                index='{0}_*'.format(settings.ES_STATS_INDEX),
            )

        # Cache & return
        self.es_index = index_name
        return index_name
