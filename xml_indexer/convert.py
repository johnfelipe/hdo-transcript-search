#! /usr/bin/python
# coding=utf-8

"""
Script that converts Akoma Ntoso xml files from an xml/ directory
and converts them to json files compatible with hdo-transcript-search's API

API structure:
{
  presidents: [
    {
      name: "Hans J. Røsjorde",
      external_id: "HJR"
    }
  ],
  session: "2000-2001",
  transcript: "s010521.sgm",
  order: 40,
  external_id: "FKM",
  name: "Finn Kristian Marthinsen",
  party: "KrF",
  time: "2001-05-21T00:00:00+02:00",
  text: "Jeg har også lyst til å understreke, ettersom jeg ikke rakk det i mitt første innlegg, det som representanten Kristin Halvorsen pekte på som viktig. Det dreier seg nemlig om det forebyggende arbeidet, det arbeidet som vi ikke klarer å lese konkrete resultater ut av, men som er så verdifullt, som politiet gjør, og som vi ønsker at politiet skal fortsette å gjøre, ja utvide, slik at vi får et samspill mellom det offentlige og det private som kan føre til at vi kan få et tryggere samfunn i framtiden. Jeg har også lyst til å kommentere det justisministeren sa, at det er vanskelig å forstå at kompetansen svekkes om politimesteren sitter i Halden eller Sarpsborg, ettersom kompetansen er knyttet til folk. Ja, det har jeg ikke så veldig vanskelig med å forstå at justisministeren sier, men jeg kan da ikke begripe hvorfor Arbeiderpartiet trenger å komme med merknaden. Da må justisministeren gjøre henvendelsen til sine egne partifeller og spørre: Hvorfor trenger dere å si dette? Jeg vil også gjerne kommentere at man nokså lett har fart over spørsmålet om Aust-Agder og sammenslåingen til ett politidistrikt i Agderfylkene. Jeg vil gjerne gjøre det i tilknytning til representanten Rasmussens innlegg, hvor han bruker som argumentasjon for Arbeiderpartiets merknad om kommunene på sørsiden av Hardangerfjorden at dette kom så sent inn, og derfor måtte man legge inn en slik merknad. Vi i Kristelig Folkeparti er subsidiært enig i denne merknaden, men representantens bemerkninger kunne like gjerne gått på Aust-Agder. Men dette går man forsiktig over, sannsynligvis fordi man altså trengte flertall for sin innstilling i et samarbeid med Høyre. Det er akkurat det representanten Ranveig Frøiland også må forstå. Hun uttaler fra Stortingets talerstol at hun håper at Kristelig Folkeparti tenker seg om i forhold til Hordaland og Haugaland. Ja, vi har tenkt oss om. Det er derfor vi har en primærinnstilling. Men fordi flertallspartiene ikke klarer å bli enige seg imellom, trenger de andre til å hjelpe seg med løsningen. Da har vi sagt at vi har et sekundærstandpunkt i denne saken. Det ønsker Kristelig Folkeparti å framheve som noe som er vårt sekundære ståsted. Jeg håper, som det er sagt tidligere, at vi kan få et godt resultat til slutt. Vi vil samarbeide om det.",
  title: "Representant"
}

Before running, ensure that the following packages are installed (using pip or easy_install):
 - elasticsearch
 - lxml
"""
import json
from lxml import etree
from elasticsearch import Elasticsearch
from datetime import datetime
from time import mktime
import os
import sys

xml_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'xml')
xml_parsed_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'xml_parsed')
json_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'json')
json_indexed_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'json_indexed')
elastic = Elasticsearch()

ES_SETTINGS = {
    'index': {
        'analysis': {
            'analyzer': {
                'analyzer_standard': {
                    'tokenizer': "standard",
                    'filter': ["standard", "lowercase"]
                },
                'analyzer_shingle': {
                    'tokenizer': "standard",
                    'filter': ["standard", "lowercase", "filter_stop", "filter_shingle"]
                }
            },
            'filter': {
                'filter_shingle': {
                    'type': "shingle",
                    'max_shingle_size': 2,
                    'min_shingle_size': 2,
                    'output_unigrams': True
                },
                'filter_stop': {
                    'type': "stop",
                    'stopwords': "_spanish_"
                    # enable_position_increments: false
                }
            }
        }
    }
}

ES_MAPPINGS = {
    'speech': {
        'properties': {
            'time': {
                'type':   'date',
                'format': 'date_time_no_millis'
            },
            'text': {
                'type': 'string',
                'analyzer': 'analyzer_standard',
                'fields': {
                    'shingles': { 'type': "string", 'analyzer': "analyzer_shingle"}
                }
            },
            'name':  { 'type': 'string', 'index': 'not_analyzed' },
            'party': { 'type': 'string', 'index': 'not_analyzed' },
            'presidents':  {
                'properties': {
                    'name':        { 'type': 'string', 'index': 'not_analyzed' },
                    'external_id': { 'type': 'string', 'index': 'not_analyzed' }
                }
            },
            'title':       { 'type': 'string',  'index': 'not_analyzed' },
            'external_id': { 'type': 'string',  'index': 'not_analyzed' },
            'transcript':  { 'type': 'string',  'index': 'not_analyzed' },
            'session':     { 'type': 'string',  'index': 'not_analyzed' },
            'order':       { 'type': 'integer', 'index': 'not_analyzed' }
        }
    }
}


def convert_xml_to_json():
    xml_files = os.listdir(xml_path)

    for file_name in xml_files:
        parse_xml(file_name)
        os.rename(os.path.join(xml_path, file_name), os.path.join(xml_parsed_path, file_name))


def parse_xml(file_name):
    print 'Convirtiendo XML a JSON ' + file_name
    xml = etree.parse(os.path.join(xml_path, file_name))
    doc_title = xml.xpath('//preface/docTitle')[0].text
    speeches = xml.xpath('//speech')
    questions = xml.xpath('//questions')

    for idx in range(len(speeches)):
        speech = speeches[idx]
        speaker_name = speech.xpath('.//from')[0].text
        speaker_id = speech.xpath('.//@by')[0]
        time = speech.xpath('.//@startTime')[0]
        text = speech.xpath('.//p')[0].text

        save_json(session=doc_title,
                  transcript=file_name,
                  order=idx + 1,
                  speaker_id=speaker_id,
                  speaker_name=speaker_name,
                  time=time,
                  text=text,
                  speech_type='s')

    for idx in range(len(questions)):
        question = questions[idx]
        speaker_name = question.xpath('.//from')[0].text
        speaker_id = question.xpath('.//@by')[0]
        time = question.xpath('//@startTime')[idx]
        narratives = question.xpath('.//narrative')
        question_list = question.xpath('.//question')

        text = '\n'.join(map(lambda n: n.text.strip(), narratives)) + '\n' + \
               '\n'.join(map(lambda q: q.text.strip(), question_list))

        save_json(session=doc_title,
                  transcript=file_name,
                  order=idx + 1,
                  speaker_id=speaker_id,
                  speaker_name=speaker_name,
                  time=time,
                  text=text,
                  speech_type='q')

def save_json(session, transcript, order, speaker_id, speaker_name, time, text, speech_type):
    speech = {
        'presidents': [],
        'session': session,
        'transcript': os.path.splitext(os.path.basename(transcript))[0],
        'order': order,
        'external_id': speaker_id,
        'name': speaker_name,
        'party': None,
        'time': time + '-05:00',
        'text': text,
        'title': "Representante"
    }

    if speaker_name.lower() != 'otros':
        file_name_json = 'json/' + os.path.splitext(os.path.basename(transcript))[0] + '-' + speech_type + str(order) + '.json'
        print 'Guardar JSON ' + file_name_json
        output = open(file_name_json, 'w')
        output.write(json.dumps(speech))

def index_json_on_elasticsearch():
    json_files = os.listdir(json_path)
    index_name = "hdo-transcripts"
    doc_type = "speech"

    for file_name in json_files:
        print 'Índice de la elasticsearch: ' + file_name
        contents = open(os.path.join(json_path, file_name)).read()
        json_loads = json.loads(contents)
        elastic.index(index=index_name, doc_type=doc_type, body=json_loads)
        os.rename(os.path.join(json_path, file_name), os.path.join(json_indexed_path, file_name))


def create_all_paths():
    for path in [json_path, json_indexed_path, xml_path, xml_parsed_path]:
        if not os.path.exists(path):
            os.mkdir(path)


if __name__ == '__main__':

    RECREATE = 'recreate' in sys.argv

    if RECREATE:
        print "Deleting elasticsearch indices"
        elastic.indices.delete(index="hdo-transcripts", ignore=[400, 404])
        elastic.indices.create(index="hdo-transcripts", body={ 'settings': ES_SETTINGS, 'mappings': ES_MAPPINGS })

    create_all_paths()
    convert_xml_to_json()
    index_json_on_elasticsearch()
