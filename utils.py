"""
Utilities.
"""

import logging
from itertools import izip_longest
import time

import requests
from rdflib import Graph

# cache delay length
DELAY_LENGTH = .3
# user agent
USER_AGENT = 'https://github.com/ctsit/vivo_wos/'


def get_uri(url, delay=False):
    """
    Return a RDFLib graph from a VIVO HTTP url.
    Will use requests_cache if available.
    """
    logging.info("Requesting: {}".format(url))
    g = Graph()
    try:
        rsp = requests.get(
            url,
            headers={'Accept': 'application/rdf+xml', 'User-Agent': USER_AGENT},
            verify=False
        )
    except Exception, e:
        logging.warning("Failed to parse " + url)
        return g
    try:
        cached_rsp = rsp.from_cache
    except AttributeError:
        cached_rsp = False

    if (delay is True) and (cached_rsp is True):
        logging.debug("-- crawl delay --")
        time.sleep(DELAY_LENGTH)
    try:
        g.parse(data=rsp.content)
    except Exception, e:
        logging.error("Error loading graph {}".format(url))
        return
    return g


def grouper(iterable, n, fillvalue=None):
    """
    Group iterable into n sized chunks.
    See: http://stackoverflow.com/a/312644/758157
    """
    args = [iter(iterable)] * n
    return izip_longest(*args, fillvalue=fillvalue)