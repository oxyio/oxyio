# oxy.io
# File: oxyio/util/stats.py
# Desc: the stats system

import json
from datetime import datetime

from elasticquery import ElasticQuery, Query, Aggregate

from oxyio import settings
from oxyio.app import redis_client, es_client

STAT_TYPE_TO_AGG = {
    'total': Aggregate.sum,
    'fixed': Aggregate.avg
}


def get_stat_keys(type_=None, queries=None):
    '''
    Get unique stat keys.
    '''

    if queries is None:
        queries = []

    # Type filter?
    if type_:
        queries.append(Query.term('type', type_))

    # Build our query
    q = ElasticQuery(
        es=es_client,
        index=settings.ES_STATS_INDEX,
        doc_type='object_stat'
    )

    # Attach queries
    q.query(Query.bool(must=queries))

    # Attach a terms aggregate
    q.aggregate(Aggregate.terms('key_terms', 'key'))

    # Get the results
    results = q.get()

    return [
        bucket['key']
        for bucket in results['aggregations']['key_terms']['buckets']
    ]


def get_stats(
    type_=None, keys=None, details=None, queries=None,
    stat_type='total', interval='1m', since='now-24h', to='now'
):
    '''
    Get stats from ES.
    '''

    if queries is None:
        queries = []

    # Always apply date range
    queries.append(Query.range('datetime', gte=since, lt=to))

    # Type filter?
    if type_:
        queries.append(Query.term('type', type_))

    # Top level date histogram aggregate
    top_aggregate = aggregate = Aggregate.date_histogram('dates', 'datetime', interval)

    # Build kwarg filters & aggregates
    for key, values in (
        ('key', keys),
        ('detail', details)
    ):
        # Handle term or terms queries
        if values:
            # If we're a list, we want to aggregate to split the data up between list
            # keys. Similarly True means we want all list keys.
            if isinstance(values, list) or values is True:
                query = Query.terms

                # Aggregate
                agg = Aggregate.terms('{0}_terms'.format(key), key)
                if aggregate:
                    aggregate.aggregate(agg)

                aggregate = agg

            else:
                query = Query.term

            # Filter if not getting all
            if values is not True:
                queries.append(query(key, values))

    # Attach the stat aggregate
    stat_agg = STAT_TYPE_TO_AGG.get(stat_type)
    stat_agg = stat_agg('value', 'value')

    # Nest aggregate
    if aggregate:
        aggregate.aggregate(stat_agg)

    # Assign nested stat agg as latest
    aggregate = stat_agg

    # Build our query
    q = ElasticQuery(
        es=es_client,
        index=settings.ES_STATS_INDEX,
        doc_type='object_stat'
    )

    # Attach queries
    q.query(Query.bool(must=queries))

    # Add the original top level date histogram
    q.aggregate(top_aggregate)

    # Get results
    results = q.get()
    dates = []

    def parse_bucket(bucket):
        out = {}

        for field in ('key', 'detail'):
            terms_field = '{0}_terms'.format(field)

            if terms_field in bucket:
                out.update(parse_buckets(bucket[terms_field]['buckets']))
                out['key'] = bucket['key']
                break

        else:
            out = {
                'key': bucket['key'],
                'value': bucket['value']['value']
            }

        return out

    def parse_buckets(buckets):
        buckets = [parse_bucket(bucket) for bucket in buckets]

        return {
            bucket.pop('key'): bucket['value'] if 'value' in bucket else bucket
            for bucket in buckets
        }

    # Parse the results into appropriately nested list of dicts
    for bucket in results['aggregations']['dates']['buckets']:
        stats = {}

        stats['stats'] = parse_bucket(bucket)
        stats['stats'].pop('key')

        stats.update({
            'datetime': bucket['key_as_string']
        })

        dates.append(stats)

    return dates


def _object_function_wrapper(obj, handler, **kwargs):
    queries = kwargs.pop('queries', [])

    queries.extend([
        Query.term('object_module', obj.MODULE),
        Query.term('object_type', obj.OBJECT),
        Query.term('object_id', obj.id)
    ])

    return handler(queries=queries, **kwargs)


def get_object_stat_keys(obj, **kwargs):
    return _object_function_wrapper(obj, get_stat_keys, **kwargs)


def get_object_stats(obj, **kwargs):
    return _object_function_wrapper(obj, get_stats, **kwargs)


def index_object_stats(obj, stats, time=None):
    '''
    Push stats to the Redis index queue.
    '''

    iso_now = datetime.utcnow().replace(microsecond=0).isoformat()

    for stat in stats:
        stat.update({
            'object_type': obj.OBJECT,
            'object_module': obj.MODULE,
            'object_id': obj.id,
            'datetime': iso_now
        })

        # Push onto the queue
        redis_client.lpush(
            settings.REDIS_INDEX_QUEUE,
            json.dumps(stat)
        )
