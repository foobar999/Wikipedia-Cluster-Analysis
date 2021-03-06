import argparse
import sys
import json
import pprint
import xmltodict
from datetime import date, timedelta
from collections import OrderedDict


def generate_xmldump_base_object():
    base_xml = '<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.8/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.mediawiki.org/xml/export-0.8/ http://www.mediawiki.org/xml/export-0.8.xsd" version="0.8" xml:lang="en">\
    <siteinfo>\
        <sitename>Wikipedia</sitename>\
        <base>http://en.wikipedia.org/wiki/Main_Page</base>\
        <generator>MediaWiki 1.22wmf2</generator>\
        <case>first-letter</case>\
        <namespaces>\
            <namespace key="0" case="first-letter" />\
            <namespace key="1" case="first-letter">Talk</namespace>\
        </namespaces>\
        </siteinfo>\
    </mediawiki>'
    return xmltodict.parse(base_xml)

    
def create_authorids_mapping_from_authornames(simple_collection):    
    authornames = set(rev['user'] for doc in simple_collection.values() for rev in doc['revisions'])
    authornames = sorted(list(authornames))
    return {name: id+1 for id,name in enumerate(authornames)}
    
    
def create_revisions_pages_from_simple_collection(simple_collection, authorname_ids, start_date=date(2002,1,1), time_delta=timedelta(days=1)):
    '''
    erzeugt aus der einfachen Kollektionsrepräsentation simple_collection ein Kollektionsobjekt, 
    das mit xmltodict als XML-Datei gespeichert werden kann 
    das gespeicherte Objekt verhält sich wie ein "richtiger" MediaWiki-Dump
    aufeinanderfolgende Revisionen desselben Dokumentes erhalten aufeinanderfolgende Zeitstempel: die erste Revision erhält den Zeitstempel
    start_date, die 2. Revision den Zeitstempel start_date+1*time_delta usw.
    '''
    pages = []
    for docid,(doctitle,doc) in enumerate(simple_collection.items()):
        page = OrderedDict()
        page['title'] = doctitle
        if 'namespace' in doc:
            page['ns'] = doc['namespace']
        page['id'] = docid + 1
        page['revision'] = []
        for i,rev in enumerate(doc['revisions']):
            current_revision = OrderedDict()
            current_revision['id'] = i+1
            current_revision['timestamp'] = (start_date+i*time_delta).strftime('%Y-%m-%dT%H:%M:%SZ')
            current_revision['contributor'] = OrderedDict()
            current_revision['contributor']['username'] = rev['user']
            current_revision['contributor']['id'] = authorname_ids[rev['user']]
            current_revision['comment'] = "*"        
            current_revision['text'] = OrderedDict()
            current_revision['text']['@xml:space'] = "preserve"
            current_revision['text']['#text'] = rev['content']
            page['revision'].append(current_revision)
        pages.append(page)
    return pages
    

def create_articles_pages_from_simple_collection(simple_collection, authorname_ids, start_date=date(2002,1,1), time_delta=timedelta(days=1)):
    articles_pages = create_revisions_pages_from_simple_collection(simple_collection, authorname_ids, start_date, time_delta)
    for page in articles_pages:
        page['revision'] = [page['revision'][-1]]   # entferne je Dokument alle Revisionen außer der aktuellsten
    return articles_pages
        
        
def save_object_to_xml(obj, xml_path):
    with open(xml_path, 'w', newline='', encoding='utf-8') as xml_file:
        xmltodict.unparse(obj, pretty=True, output=xml_file, indent='  ', full_document=False)    
    
        

def main():
    parser = argparse.ArgumentParser(description='converts a simple JSON-collection of document revisions of contributors to MediaWiki-like XML dump files', epilog='Example: ./{} collection.json collection-pages-articles.xml collection-pages-meta-history.xml.'.format(sys.argv[0]))
    parser.add_argument("icollection", type=argparse.FileType('r'), help='path to input JSON-collection')
    parser.add_argument("oarticlesdump", type=argparse.FileType('w'), help='path to output XML articles dump file')
    parser.add_argument("orevisionsdump", type=argparse.FileType('w'), help='path to output XML revisions dump file')
    args = parser.parse_args()
    input_collection_path = args.icollection.name
    output_articles_path = args.oarticlesdump.name 
    output_revisions_path = args.orevisionsdump.name 
    print('converting simple JSON collection "{}"'.format(input_collection_path))
    print('to XML articles dump "{}"'.format(output_articles_path))
    print('and XML revisions dump "{}"'.format(output_revisions_path))
    with open(input_collection_path, 'r', newline='', encoding='utf-8') as input_collection_file:
        simple_collection = json.load(input_collection_file, strict=False)   
    
    authorname_ids = create_authorids_mapping_from_authornames(simple_collection)
    print('authorname->authorid mapping: {}'.format(authorname_ids))
    
    print('generating XML articles dump file')
    collection_articles = generate_xmldump_base_object()
    articles_pages = create_articles_pages_from_simple_collection(simple_collection, authorname_ids)
    collection_articles['mediawiki']['page'] = articles_pages 
    save_object_to_xml(collection_articles, output_articles_path)  
    
    print('generating XML revisions dump file')
    collection_revisions = generate_xmldump_base_object()
    revisions_pages = create_revisions_pages_from_simple_collection(simple_collection, authorname_ids)
    collection_revisions['mediawiki']['page'] = revisions_pages    
    save_object_to_xml(collection_revisions, output_revisions_path)
    
    
    
if __name__ == '__main__':
    main()
    

    
    
    