# -*- coding: utf-8 -*-
"""
Convert found data to RDF.
"""
import os
from rdflib import URIRef, Namespace, Graph, Literal, RDF, RDFS

D = Namespace(os.environ['DATA_NAMESPACE'])
VIVO = Namespace('http://vivoweb.org/ontology/core#')
BIBO = Namespace('http://purl.org/ontology/bibo/')
OBO = Namespace('http://purl.obolibrary.org/obo/')
VCARD = Namespace('http://www.w3.org/2006/vcard/ns#')
UFL = Namespace('http://vivo.ufl.edu/ontology/vivo-ufl/')


WOS_LINK_TEXT = u"Web of Science™"


def add_vcard_weblink(pub_uri, link):
    """
    Build statements for weblinks in VIVO.
    :return: rdflib.Graph
    """
    local_id = pub_uri.split('/')[-1]
    g = Graph()

    # vcard individual for pub
    vci_uri = D['vcard-individual-pub-' + local_id]
    g.add((vci_uri, RDF.type, VCARD.Individual))

    # vcard URL
    vcu_uri = D['vcard-url-pub-' + local_id]
    g.add((vcu_uri, RDF.type, UFL.TRCatalogLink))
    g.add((vcu_uri, RDFS.label, Literal(WOS_LINK_TEXT)))
    g.add((vcu_uri, VCARD.url, Literal(link)))
    # Relate vcard individual to url
    g.add((vci_uri, VCARD.hasURL, vcu_uri))
    return vci_uri, g


def to_rdf(found):
    """
    Process the AMR response into RDF.
    """
    g = Graph()
    for url in found:
        ut = found[url].get('ut')
        uri = URIRef(url)
        link = found[url].get('sourceURL')
        if ut is not None:
            g.add((uri, UFL.wosId, Literal(ut)))
            # Add web links
            link_vcard_uri, lg = add_vcard_weblink(uri, link)
            g += lg
            g.add((uri, OBO['ARG_2000028'], link_vcard_uri))
    return g
