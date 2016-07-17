# hdo-transcript-search

This project consists of two parts:

* `xml_indexer/` - Index XML transcripts (Akoma Ntoso format) in ElasticSearch
* `webapp/`  - web frontend to present / visualize the data

## Requirements

* elasticsearch
* node.js
* python

## xml_indexer

Index XML transcripts (requires a local elasticsearch):

* Install elasticsearch
  * <https://www.elastic.co/guide/en/elasticsearch/reference/current/_installation.html>
  * <https://www.elastic.co/guide/en/elasticsearch/reference/current/setup-service.html>
  
* cd /xml_indexer
* cp -R /path/to/xml_transcripts/* xml/
* python convert.py

## webapp

Start the webapp in dev mode:

* cd webapp
* npm install
* npm run dev
* open your browser at http://localhost:7575/
