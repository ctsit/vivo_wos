"""

Using a VIVO Journal URI as input, find related
publications and match each against the Web of Science
LAMR Web Service to obtain Web of Science links and additional identifiers.

"""
import logging
import json
import sys

from rdflib import URIRef, Namespace

import amr
import models
from utils import get_uri

# use caching if available
try:
    import requests_cache
    requests_cache.install_cache('/tmp/vivo', backend='sqlite', allowable_methods=('GET', 'POST'))
except ImportError:
    pass

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.basicConfig(level=logging.INFO)

VIVO = Namespace('http://vivoweb.org/ontology/core#')
BIBO = Namespace('http://purl.org/ontology/bibo/')


def get_pub_ids(puri):
    puri = puri.rstrip()
    logging.info("Processing publication uri: " + puri)
    uri = URIRef(puri)
    g = get_uri(puri)
    try:
        doi = g.value(subject=uri, predicate=BIBO.doi).toPython()
    except AttributeError:
        doi = None
    try:
        pmid = g.value(subject=uri, predicate=BIBO.pmid).toPython()
    except AttributeError:
        pmid = None
    logging.info("Pub URI: {} Pub DOI: {} PubMedID: {}".format(puri, doi, pmid))
    return dict(id=puri, doi=doi, pmid=pmid)


def get_pubs_in_journal(vuri):
    logging.info("Processing journal uri: " + vuri)
    g = get_uri(vuri)
    #issn = g.value(subject=URIRef(vuri), predicate=BIBO.issn)
    #logging.info("ISSN: " + issn)
    for pub in g.objects(subject=URIRef(vuri), predicate=VIVO.publicationVenueFor):
        yield get_pub_ids(pub)


def get_wos_links(journal_uri):
    """
    Run the Journal URI through the process and
    output an RDFLib graph with statements for
    linking to the Web of Science.
    """
    pubs = get_pubs_in_journal(uri)
    matched = amr.check_batch(pubs)
    g = models.to_rdf(matched)
    return g

if __name__ == '__main__':
    uri = sys.argv[1]

    g = get_wos_links(uri)
    print g.serialize(format="turtle")

    #pubs = get_pubs_in_journal(uri)
    #found = [p for p in pubs]
    #print json.dumps(found, indent=2)
