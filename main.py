#! /usr/bin/env python

import sys, io

try:
    from glob import glob
    from rdflib.plugins import sparql
    from rdflib import URIRef, Graph, Literal
    from rdflib import Namespace
    from rdflib.namespace import XSD, RDF, RDFS, OWL, FOAF
except ImportError:
    print
    'Please install rdflib'
    sys.exit(1)
try:
    import gpxpy.gpx
except ImportError:
    print
    'Please install gpxpy'
    sys.exit(1)
try:
    import requests
except ImportError:
    print
    'Please install requests'
    sys.exit(1)
try:
    import xml.etree.ElementTree as ET
except ImportError:
    print
    'Please install xml'
    sys.exit(1)
try:
    from SPARQLWrapper import SPARQLWrapper, JSON
except ImportError:
    print
    'Please install SPARQLWrapper'
    sys.exit(1)

gpxFileName = 'GPX_Tracks/4sDDFdd4cjA.gpx'  # file with track points
rdfFileName = 'gpx_osm_rdf.ttl'  # rdf file containing track points and interesting venues

osmFileName = 'deneme.osm'  # temporary file from openstreetmap


def createHtmlFile(variance, mapName, points, venues):
    with open('website_%s.html'%mapName, 'w') as f:
        f.write('<!DOCTYPE html>\n')
        f.write('<html>\n')
        f.write('    <head>\n')
        f.write('        <title>OpenStreetmap with RDF</title>\n')
        f.write(
            '        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" integrity="sha512-xodZBNTC5n17Xt2atTPuE1HxjVMSvLVW9ocqUKLsCC5CXdbqCmblAshOMAS6/keqq/sMZMZ19scR4PsZChSR7A==" crossorigin=""/>\n')
        f.write(
            '        <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js" integrity="sha512-XQoYMqMTK8LvdxXYG3nZ448hOEQiglfqkJs1NOQV44cWnUrBc8PkAOcXy20w0vlaXaVUearIOBhiXZ5V3ynxwA==" crossorigin=""></script>\n')
        f.write('    </head>\n')
        f.write('    <body>\n')
        f.write('        <div id="mapid" style="width: 800px; height: 600px;"></div>\n')
        f.write('        <script>\n')
        # build the map
        f.write('            var mymap = L.map("mapid").setView([%.6f, %.6f], 13);\n' % (
        (variance[3] + variance[1]) / 2,
        (variance[2] + variance[0]) / 2))  # last number is zoom, could be adapted more accurately from overall map size
        # add the markers
        for point in points:
            f.write('            var circle = L.circle([%.6f, %.6f], {\n' % (point.latitude, point.longitude))
            f.write('                color: \'black\',\n')
            f.write('                fillColor: \'#f03\',\n')
            f.write('                fillOpacity: 0.5,\n')
            f.write('                radius: 50\n')
            f.write('            }).addTo(mymap);\n')
        for point, title, description in venues:
            f.write('            var marker = L.marker([%.6f, %.6f]).addTo(mymap);\n' % (point[0], point[1]))
            f.write('            marker.bindPopup("<b>%s</b><br>%s").openPopup();\n' % (title, description))
        f.write(
            '\n            L.tileLayer("https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw", {\n')
        f.write('            maxZoom: 18,\n')
        f.write(
            '            attribution: \'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery <a href="https://www.mapbox.com/">Mapbox</a>\',\n')
        f.write('            id: \'mapbox/streets-v11\',\n')
        f.write('            tileSize: 512,\n')
        f.write('            zoomOffset: -1\n')
        f.write('            }).addTo(mymap);\n')
        #
        f.write('        </script>\n')
        # f.write('        <iframe width="800" height="600" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="https://www.openstreetmap.org/export/embed.html?bbox=%.6f%%2C%.6f%%2C%.6f%%2C%.6f&amp;layer=mapnik" style="border: 1px solid black"></iframe><br/>\n'%(variance[0],variance[1],variance[2],variance[3]))
        # f.write('        <small><a href="https://www.openstreetmap.org/#map=13/%.6f/%.6f">View larger map</a></small>\n'%((variance[3]+variance[1])/2,(variance[2]+variance[0])/2)) # first number is zoom, could be adapted more accurately from overall map size
        f.write('    </body>\n')
        f.write('</html>\n')
    f.close()


def get_osm_file(variance, gpxFile, rdfFile):
    #

    # This function get osm file form api.openstreetmap

    # and adds nodes to the existed file which has been produced before using with gpx

    # @parameter 'variance' is the value of lat and lon max and min

    #

    response = requests.get('https://api.openstreetmap.org/api/0.6/map?bbox=%.6f,%.6f,%.6f,%.6f' % (
    variance[0], variance[1], variance[2], variance[3]))
    with io.open(osmFileName, 'w', encoding='utf8') as f:
        f.write(response.text)
    f.close()

    data = ET.parse(osmFileName)

    root = data.getroot()

    venues = []

    with io.open(rdfFile, 'a', encoding='utf8') as f:

        for node in root.iter('node'):

            if node.attrib['visible'] == 'true':  # check if the place is still accessible

                f.write((
                                    ':api osm:node _:a. _:a rdf:type rdf:seq; geo:lat "%s"^^xsd:float; geo:lon "%s"^^xsd:float; osm:id "%s"^^xsd:int.\n' % (
                            node.attrib['lat'], node.attrib['lon'], node.attrib['id'])).encode('utf-8').decode('utf8'))

                for tag in node.iter('tag'):

                    f.write((u''.join(('_:a osm:tag _:t. _:t osm:key "%s"; osm:val "%s".\n' % (
                    tag.attrib['k'], tag.attrib['v']))).encode('utf-8')).decode('utf8'))
                    if tag.attrib['k'] == 'name': venues.append(((float(node.attrib['lat']), float(node.attrib['lon'])),
                                                                 tag.attrib['v'].encode('utf-8'),
                                                                 "TODO: get from dbpedia"))

    f.close()
    return venues


def gpx_reader(gpxFile):
    # Parsing an existing file of gpx:

    # this function is being used just for getting latitude and longitude (max and min)

    gpx_file = open(gpxFile, 'r')

    gpx = gpxpy.parse(gpx_file, version='1.1')



    list_trackpoints = gpx.tracks[0].segments[0].points

    return list_trackpoints

    # print(type(list_trackpoints[0].latitude))

    # print(max(list_trackpoints.latitude, key=lambda x: list_trackpoints[x]))



def make_rdf(gpxFile, rdfFile):
    #

    # This function makes the rdf triple (a simple version) writing in file

    #

    data = ET.parse(gpxFile)

    root = data.getroot()

    rdf_str = '{http://www.topografix.com/GPX/1/1}'

    file = open(rdfFile, 'w')

    file_str = ''

    file_prefix = '@prefix xsd: <http://w3.org/2001/XMLSchema#>.\n' + '@prefix rdf: <http://w3.org/1999/02/22-rdf-syntax-ns#>.\n' + '@prefix rdfs: <http://w3.org/2000/01/rdf-schema#>.\n' + '@prefix geo: <https://w3.org/wiki/GeoRDF#>.\n' + '@prefix wikidata: <https://www.wikidata.org/wiki/>.\n' + '@prefix dbpedia: <http://dbpedia.org/ontology/>.\n' + '@prefix osm: <http://openstreetmap.org/export/>.\n' + '@prefix api: <https://api.openstreetmap.org/api/0.6/map?bbox=#>.\n' + '@prefix : <http://topografix.com/GPX/1/1/>.\n\n\n'

    file.write(file_prefix)

    trk_name = root.find('{}trk//{}name'.format(rdf_str, rdf_str)).text

    file.write(':trk :name "{}".\n\n'.format(trk_name))

    for index, trkpt in enumerate(root.iter(tag='{}trkpt'.format(rdf_str))):

        # print(':{}'.format(trkpt.tag[len(rdf_str):]))

        file_str += ':{}'.format(trkpt.tag[len(rdf_str):])

        file_str += ' rdf:type {};'.format(':ptType')

        for k, element in enumerate(trkpt.attrib.items()):
            file_str += ' geo:{} "{}"^^xsd:float;'.format(element[0], element[1])  # lat lon

            # print(' :{} {};'.format(element[0], element[1]))

            # print(element.tag)

        # print(':id {}.'.format(index))

        file_str += ' :id "{}"^^xsd:int.\n'.format(index)

        file.write(file_str)

        file_str = ''

    file.close()





def query_make():
    #

    # Sparql query but not working yet

    #

    # sparql = SPARQLWrapper('http://dbpedia.org/sparql')

    # sparql.setQuery('''

    # PREFIX dbo: <http://dbpedia.org/ontology/>

    # PREFIX file: <https://github.com/MuratTuz/rdf/blob/main/>

    # select ?node

    # where { file:osm:node

    #     ''')

    # from SPARQLWrapper import SPARQLWrapper, JSON

    sparql = SPARQLWrapper("http://dbpedia.org/sparql")

    queryTourism = """ 
        PREFIX dbp: <http://dbpedia.org/resource/classes#>.
        PREFIX file: <https://github.com/MuratTuz/rdf/blob/main#gpx_osm_rdf.ttl>.
        PREFIX dbo: <http://dbpedia.org/ontology/>

        SELECT DISTINCT ?place

        WHERE {file:tags osm:key ?place.
        filter(?place=dbp:tourism)}"""

    print('---------------------------')
    print('id %s' % id)
    sparql.setQuery(queryTourism)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    print('---------------------------')
    for result in results["results"]["bindings"]:
        print(result["place"]["value"])

    print('---------------------------')

    # for tag in tagNames:
    #     print('---------------------------')
    #     print('Tag %s'%tag)
    #     sparql.setQuery("""
    #         PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    #         SELECT ?label
    #         WHERE { <http://dbpedia.org/resource/%s> rdfs:label ?label }
    #     """%tag)
    #     sparql.setReturnFormat(JSON)
    #     results = sparql.query().convert()

    #     print('---------------------------')
    #     for result in results["results"]["bindings"]:
    #         print(result["label"]["value"])

    #     print('---------------------------')

def createAllFiles(gpxFiles):
    #
    # This function creates all html files
    #
    for gpx_file in gpxFiles:
        list_trackpoints = gpx_reader(gpx_file)

        # calculate part of map to be shown
        latitude_max = max(point.latitude for point in list_trackpoints)
        latitude_min = min(point.latitude for point in list_trackpoints)
        longitude_max = max(point.longitude for point in list_trackpoints)
        longitude_min = min(point.longitude for point in list_trackpoints)
        variance = (longitude_min, latitude_min, longitude_max, latitude_max)

        make_rdf(gpx_file, rdfFileName)

        # TODO: the venue description is filled by a default value inside get_osm_file()
        # however, it should be filled with info from dbpedia retrieved via SPARQLWrapper?!
        venues = get_osm_file(variance, gpxFileName, rdfFileName)
        # query_make()

        createHtmlFile(variance, gpxFileName.replace('.gpx', ''), list_trackpoints, venues)


if __name__ == '__main__':
    # retrieve track points from gxpFile
    files = glob('*.gpx')
    list_trackpoints = gpx_reader(gpxFileName)

    # calculate part of map to be shown
    latitude_max = max(point.latitude for point in list_trackpoints)
    latitude_min = min(point.latitude for point in list_trackpoints)
    longitude_max = max(point.longitude for point in list_trackpoints)
    longitude_min = min(point.longitude for point in list_trackpoints)
    variance = (longitude_min, latitude_min, longitude_max, latitude_max)

    make_rdf(gpxFileName, rdfFileName)

    # TODO: the venue description is filled by a default value inside get_osm_file()
    # however, it should be filled with info from dbpedia retrieved via SPARQLWrapper?!
    venues = get_osm_file(variance, gpxFileName, rdfFileName)
    query_make()

    createHtmlFile(variance, gpxFileName.replace('.gpx', ''), list_trackpoints, venues)
