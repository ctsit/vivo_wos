"""

Sample script to take a CSV of journals with
uri,issn columns as input and look those journals
up via AMR to add links to the JCR.

"""
import os
import csv
import logging
import json
import sys

import amr
import models
import utils

import xml.etree.ElementTree as ET

USER = os.environ['LAMR_USER']
PASSWORD = os.environ['LAMR_PASSWORD']

request_template = u"""<?xml version="1.0" encoding="UTF-8" ?>
<request xmlns="http://www.isinet.com/xrpc41" src="app.id=InternalVIVODemo">
  <fn name="LinksAMR.retrieve">
    <list>
      <!-- authentication -->
      <map>
        <val name="username">{user}</val>
        <val name="password">{password}</val>
      </map>
      <!-- what to to return -->
       <map>
        <list name="JCR">
          <val>impactGraphURL</val>
        </list>
      </map>
       <!-- LOOKUP DATA -->
       {items}
    </list>
  </fn>
</request>
"""

def prep_amr(items):
    """
    <map name="cite_1">
        <val name="{id_type}">{value}</val>
    </map>
    """
    map_items = ET.Element("map")
    for uri, issn in items:
        if (uri is None) or (issn is None):
            continue
        this_item = ET.Element("map", name=uri)
        de = ET.Element("val", name="issn")
        de.text = issn
        this_item.append(de)
        map_items.append(this_item)
    
    request_items = ET.tostring(map_items)
    xml = request_template.format(user=USER, password=PASSWORD, items=request_items)
    return xml

def to_rdf(found):
    g = Graph()
    for uri in found:
        jcr = item['impactGraphURL']
        uri = URIRef(uri)
        # Add web links
        link_vcard_uri, lg = add_vcard_weblink(uri, link)
        g += lg
        g.add((uri, OBO['ARG_2000028'], link_vcard_uri))


def do_batch(batch):
    # Returns a dict uri - jcr link
    xml = prep_amr(batch)
    rsp = amr.get(xml)
    found = amr.read(rsp)
    return found


def process_items(jrnls):
    found = {}
    for batch in utils.grouper(jrnls, 25, fillvalue=(None,None)):
        b = do_batch(batch)
        found.update(b)
    return found


if __name__ == '__main__':
    journal_file = sys.argv[1]

    to_check = []

    with open(journal_file) as inputfile:
        for n, row in enumerate(csv.DictReader(inputfile)):
            if row['issn'] == "":
                print>>sys.stderr, "No ISSN for", row['uri']
                continue
            to_check.append((row['uri'], row['issn']))
            if n > 50:
                break

    # Send off to AMR
    found = process_items(to_check)
    # Map to VIVO RDF
    g = models.journal_link_rdf(found)
    # Print as turtle
    print g.serialize(format="turtle")
