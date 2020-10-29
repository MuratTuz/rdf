# This is a sample Python script.
import rdflib, pprint
from rdflib.plugins import sparql
from rdflib import URIRef, Graph
from rdflib import Namespace
from rdflib.namespace import XSD, RDF, RDFS
import gpxpy
import gpxpy.gpx
import requests
import xml.etree.ElementTree as ET
from SPARQLWrapper import SPARQLWrapper2
import SPARQLWrapper
# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

def get_osm_file(variance):
    response = requests.get(f'https://api.openstreetmap.org/api/0.6/map?bbox='
                            f'{variance[0]},{variance[1]},{variance[2]},{variance[3]}')
    with open('deneme.osm','w', encoding='utf-8') as file_osm:
         file_osm.write(response.text)

    file_rdf = open('gpx_osm_rdf.ttl', 'a', encoding='utf-8')
    data = ET.parse('deneme.osm')
    root = data.getroot()
    node_str = ''
    tag_str = ''
    for node in root.iter('node'):
        if node.attrib['visible'] == 'true': # check if the place is still accessible

            #print(node.attrib['lat'], node.attrib['lon'], node.attrib['id'])
            for tag in node.iter('tag'):
                # if node has tag then register it
                node_str = 'osm:node rdf:type osm:node; geo:lat "{}"^^xsd:float; ' \
                           'geo:lon "{}"^^xsd:float; osm:id "{}"^^xsd:int.\n' \
                           ''.format(node.attrib['lat'], node.attrib['lon'], node.attrib['id'])
                tag_str += 'osm:tag osm:id "{}"^^xsd:int; osm:key "{}"; osm:val "{}".\n' \
                           ''.format(node.attrib['id'], tag.attrib['k'], tag.attrib['v'])
                #print(tag.attrib['k'], tag.attrib['v'])
        file_rdf.write(node_str) ; file_rdf.write(tag_str)
        node_str = ''; tag_str = ''
    file_rdf.close()

def gpx_reader():
    # Parsing an existing file:
    # -------------------------

    gpx_file = open('4sDDFdd4cjA.gpx', 'r', encoding='utf-8')

    gpx = gpxpy.parse(gpx_file, version='1.1')


    '''for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                print('Point at ({0},{1}) -> {2}'.format(point.latitude, point.longitude, point.elevation))


    for waypoint in gpx.waypoints:
        print('waypoint {0} -> ({1},{2})'.format(waypoint.name, waypoint.latitude, waypoint.longitude))

    for route in gpx.routes:
        print('Route:')
        for point in route.points:
            print('Point at ({0},{1}) -> {2}'.format(point.latitude, point.longitude, point.elevation))'''

    # There are many more utility methods and functions:
    # You can manipulate/add/remove tracks, segments, points, waypoints and routes and
    # get the GPX XML file from the resulting object:

    #print('GPX:', gpx.to_xml())
    list_trackpoints = gpx.tracks[0].segments[0].points
    #print(type(list_trackpoints[0].latitude))
    #print(max(list_trackpoints.latitude, key=lambda x: list_trackpoints[x]))
    latitude_max = max(point.latitude for point in list_trackpoints)
    latitude_min = min(point.latitude for point in list_trackpoints)
    longitude_max = max(point.longitude for point in list_trackpoints)
    longitude_min = min(point.longitude for point in list_trackpoints)
    return (longitude_min,latitude_min,longitude_max,latitude_max)

    # Creating a new file:
    # --------------------

    '''gpx = gpxpy.gpx.GPX()

    # Create first track in our GPX:
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)

    # Create first segment in our GPX track:
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    # Create points:
    gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(2.1234, 5.1234, elevation=1234))
    gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(2.1235, 5.1235, elevation=1235))
    gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(2.1236, 5.1236, elevation=1236))

    # You can add routes and waypoints, too...

    print('Created GPX:', gpx.to_xml())'''

def rdf_reader(file):
    graph = rdflib.Graph()
    graph.load(file, format='xml')
    '''for s, p, o in graph:
        print(s)'''

def usage(name):
    # daha sonra yaz.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

def make_rdf():
    data = ET.parse('C:\\Users\\murat\\OneDrive\\Documents\\UniGE\\Master\\Semantic_Web\\GPX2RDF-20201003\\GPX_Tracks\\GPX_Tracks\\4sDDFdd4cjA.gpx')
    root = data.getroot()
    rdf_str ='{http://www.topografix.com/GPX/1/1}'
    file = open('gpx_osm_rdf.ttl','w', encoding='utf-8')
    file_str =''
    file_prefix ='@prefix xsd: <http://w3.org/2001/XMLSchema#>.\n' \
                 '@prefix rdf: <http://w3.org/1999/02/22-rdf-syntax-ns#>.\n' \
                 '@prefix rdfs: <http://w3.org/2000/01/rdf-schema#>.\n' \
                 '@prefix geo: <https://w3.org/wiki/GeoRDF#>.\n' \
                 '@prefix wikidata: <https://www.wikidata.org/wiki/>.\n' \
                 '@prefix dbpedia: <http://dbpedia.org/ontology/>.\n'    \
                 '@prefix osm: <http://openstreetmap.org/export/>.\n'   \
                 '@prefix : <http://topografix.com/GPX/1/1/>.\n\n\n'

    file.write(file_prefix)

    trk_name = root.find('{}trk//{}name'.format(rdf_str,rdf_str)).text
    file.write(':trk :name "{}".\n\n'.format(trk_name))

    for index, trkpt in enumerate(root.iter(tag='{}trkpt'.format(rdf_str))):
        #print(':{}'.format(trkpt.tag[len(rdf_str):]))
        file_str += ':{}'.format(trkpt.tag[len(rdf_str):])
        file_str += ' rdf:type {};'.format(':ptType')
        for k, element in enumerate(trkpt.attrib.items()):
            file_str += ' geo:{} "{}"^^xsd:float;'.format(element[0], element[1]) # lat lon
            #print(' :{} {};'.format(element[0], element[1]))
            #print(element.tag)
        #print(':id {}.'.format(index))
        file_str += ' :id "{}"^^xsd:int.\n'.format(index)
        file.write(file_str)
        file_str = ''
    file.close()

def get_query():

    g = rdflib.Graph()


    tp_rdf = Namespace('http://topografix.com/GPX/1/1/')
    g.bind(':',tp_rdf)
    g.bind('osm:', 'http://openstreetmap.org/export/')
    g.bind('xsd:', XSD)
    g.bind('geo:', 'https://w3.org/wiki/GeoRDF#')
    g.bind('rdf:', RDF)
    g.bind('rdfs:', RDFS)

    #g.parse('gpx_osm_rdf.ttl', format='ttl')
    #g.add((URIRef(tp_rdf.trkpt))
    query = '''    
    select distinct ?p
    where { osm:node rdf:type :ptType} '''
    g.query(query)
    #g = sparql.setQuery(query)
    for str in g:
        print(rdflib.term.Literal(str).value)
# Press the green button in the gutter to run the script.

def rdf_make():
    g = rdflib.Graph()

if __name__ == '__main__':

    variance = gpx_reader()
    make_rdf()
    get_osm_file(variance)
    #get_query()


