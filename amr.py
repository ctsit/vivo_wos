"""
Client for sending requests to AMR:
http://ipscience-help.thomsonreuters.com/LAMRService/WebServicesOverviewGroup/overview.html
"""

import logging
import os

import xml.etree.ElementTree as ET

import requests

import utils

USER = os.environ['LAMR_USER']
PASSWORD = os.environ['LAMR_PASSWORD']

ns = {'isi': 'http://www.isinet.com/xrpc41'}


ET.register_namespace("isi", "http://www.isinet.com/xrpc41")

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
         <list name="WOS">
           <val>timesCited</val>
           <val>ut</val>
           <val>doi</val>
           <val>pmid</val>
           <val>sourceURL</val>
           <val>citingArticlesURL</val>
           <val>relatedRecordsURL</val>
         </list>
       </map>
       <!-- LOOKUP DATA -->
       {items}
    </list>
  </fn>
</request>
"""


def read(raw):
    """
    Read the AMR response into a dictionary.
    """
    raw = ET.fromstring(raw)
    cites = raw.findall('isi:fn/isi:map/isi:map', ns)
    out = {}
    for cite in raw.findall('isi:fn/isi:map/isi:map', ns):
        cite_key = cite.attrib['name']
        meta = {}
        for val in cite.findall('isi:map/isi:val', ns):
            meta[val.attrib['name']] = val.text
            out[cite_key] = meta
    return out


def get(xml):
    """
    POST the given XML to AMR.
    """
    logging.debug("Posting to AMR:\n" + xml)
    rsp = requests.post(
        'https://ws.isiknowledge.com/cps/xrpc',
        data=xml,
        headers={'Content Type': "application/xml"},
        verify=False
    )
    try:
        logging.debug("Cached response: " + str(rsp.from_cache))
    except AttributeError:
        pass
    return rsp.text

def prep_amr(items):
    """
    <map name="cite_1">
        <val name="{id_type}">{value}</val>
    </map>
    """
    map_items = ET.Element("map")
    for pub in items:
        if pub is None:
            continue
        this_item = ET.Element("map", name=pub['id'])
        for k,v in pub.items():
            if v is None:
                continue
            de = ET.Element("val", name=k)
            de.text = v
            this_item.append(de)
        map_items.append(this_item)
    
    request_items = ET.tostring(map_items)
    xml = request_template.format(user=USER, password=PASSWORD, items=request_items)
    return xml


def check_batch(items, number=25):
    """
    Takes a list of items and sends to AMR.
    Pass in number as the number of items to send to AMR at once.
    The web service restricts this to at most 50.
    """
    d = {}
    for batch in utils.grouper(items, number):
        lamr_msg = prep_amr(batch)
        logging.debug("Prepared AMR message: \n" + lamr_msg)
        found = get(lamr_msg)
        meta = read(found)
        d.update(meta)

    return d