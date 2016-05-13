# vivo_wos
Collaboration for adding Web of Science link to VIVO publications

## `fetch_ids`

This script will take a VIVO URI for a journal as input, find the publications related to that journal, and attempt to match
those to the Web of Science™ using the [Links Article Match Retrieval](http://ipscience-help.thomsonreuters.com/LAMRService/WebServicesOverviewGroup/overview.html) web service.

For example:

`$ python fetch_ids.py http://vivo.ufl.edu/individual/n5180047362`

## Settings and credentials
The VIVO data namespace and the credentials for the AMR Web service are configured as environment variables. Copy `.env-sample` to
a file, e.g. `.env`, and adjust them to meet your system. Then type `source .env`.

## Code layout

* `amr.py` - client to the [Links Article Match Retrieval](http://ipscience-help.thomsonreuters.com/LAMRService/WebServicesOverviewGroup/overview.html) service for the Web of Science.

* `models.py` - mappings of AMR response data to RDF for adding links to publication records.

* `utils.py` - utilities for fetching linked data from VIVO.

The mapping 

## Authors
Ted Lawless, Nicholas Rejack, Chris Barnes, Kevin Hanson
