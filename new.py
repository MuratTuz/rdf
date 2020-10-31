import rdflib
import gpxpy
import gpxpy.gpx
import os.path
from rdflib import Namespace, URIRef, Graph, Literal
from rdflib.namespace import RDF, FOAF, OWL, RDFS, XSD

# define graph
g = rdflib.Graph()
Myrdf = rdflib.Namespace("define your URI here ,  and example: htpp....../Murat")
g.bind("Myrdf", Myrdf)
g.bind("rdf", rdflib.RDF)
g.bind("rdfs", rdflib.RDFS)
g.bind("foaf", rdflib.FOAF)
g.bind("owl", rdflib.OWL)
g.bind("xsd", rdflib.XSD)
Geographic = rdflib.Namespace("https://www.w3.org/2003/01/geo/wgs84_pos#")
g.bind("Geographic", Geographic)

g.add((rdflib.URIRef(Myrdf.Track), rdflib.RDF.type, rdflib.OWL.Thing))
g.add((rdflib.URIRef(Myrdf.Trklink), rdflib.RDF.type, rdflib.FOAF.Document))
g.add((rdflib.URIRef(Myrdf.Segement), rdflib.RDF.type, rdflib.RDF.List))

gpx_file = open('UAQjXL9WRKY.gpx', 'r')
gpx_basename = os.path.basename(gpx_file.name)

gpx_basename = os.path.splitext(gpx_basename)[0]

print(gpx_basename)

for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            # Add point to RDF
            g.add((URIRef(Myrdf.Trackpoint), RDF.type, Myrdf.Trkpoint))
            g.add((URIRef(Myrdf.Segement), Myrdf.hasTrkpoint,
                   URIRef(Myrdf.Trackpoint)))
            g.add((URIRef(Myrdf.Trackpoint), Geographic.longitude,
                   Literal(point.longitude, datatype=XSD.float)))
            g.add((URIRef(Myrdf.Trackpoint), Geographic.latitude,
                   Literal(point.latitude, datatype=XSD.float)))
            g.add((URIRef(Myrdf.Trackpoint), Geographic.altitude,
                   Literal(point.elevation, datatype=XSD.integer)))
            g.add((URIRef(Myrdf.Trackpoint), XSD.date,
                   Literal(point.time, datatype=XSD.datetime)))

g.serialize(gpx_basename + ".ttl", format="ttl")