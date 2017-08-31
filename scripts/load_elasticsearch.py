import elasticsearch
import json
import click

from toolz import iterate, curry, take
from csv import DictReader
from elasticsearch.helpers import streaming_bulk

nuforc_report_index_name = 'nuforc'
nuforc_report_type_name = 'nuforc_report'

nuforc_report_index_body = {
    "mappings": {
        nuforc_report_type_name: {
            "properties": {
                "text": {
                    "type": "text"
                },
                "stats": {
                    "type": "text"
                },
                "date_time": {
                    "type": "date",
                    "format": "date_hour_minute_second"
                },
                "report_link": {
                    "type": "text"
                },
                "city": {
                    "type": "keyword"
                },
                "state": {
                    "type": "keyword"
                },
                "shape": {
                    "type": "keyword"
                },
                "duration": {
                    "type": "text"
                },
                "summary": {
                    "type": "text"
                },
                "posted": {
                    "type": "date",
                    "format": "date_hour_minute_second"
                }
            }
        }
    }
}

def nuforc_bulk_action(doc, doc_id):
    """ Binds a document / id to an action for use with the _bulk endpoint.
    """
    return {
        "_op_type": "index",
        "_index": nuforc_report_index_name,
        "_type": nuforc_report_type_name,
        "_id": doc_id,
        "_source": doc
    }

@click.command()
@click.argument("report_file", type=click.File('r'))
def main(report_file):
    """ Creates an Elasticsearch index for the NUFORC reports and loads the
        processed CSV file into it.
    """
    client = elasticsearch.Elasticsearch()
    index_client = elasticsearch.client.IndicesClient(client)

    # Drop the index if it exists; it will be replaced. This is the most efficient
    # way to delete the data from an index according to ES documentation.
    if index_client.exists(nuforc_report_index_name):
        index_client.delete(nuforc_report_index_name)

    # Create the index with the appropriate mapping.
    index_client.create(nuforc_report_index_name, nuforc_report_index_body)

    reports = DictReader(report_file)

    # Zip the reports with an id generator, embedding them in the actions.
    report_actions = map(nuforc_bulk_action, reports, iterate(lambda x: x+1, 0))

    # Stream the reports into the ES database.
    for ok,resp in elasticsearch.helpers.streaming_bulk(client, report_actions):
        if not ok:
            print(resp)

if __name__ == "__main__":
    main()