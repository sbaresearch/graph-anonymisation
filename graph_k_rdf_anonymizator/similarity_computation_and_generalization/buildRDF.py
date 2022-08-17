from rdflib import Literal, Graph, RDF
from rdflib.term import URIRef
from namespace import *

def build_rdf(fnhc_dict, attributes, unidirectional_connections, bidirectional_connections, senstive_attributes):

    anonymized_graph = Graph()
    
    #anonymize names
    names_dict = {}
    count = 0 
    preamble = "#/"

    for p in fnhc_dict:
        count = count + 1
        names_dict[p] = URIRef("%s_ID_%s" %(preamble, count))
    
    
    #print("Names Dictionary", names_dict)

    #generate graph
    for p in fnhc_dict:
        
        #substitute names by IDs (remove identifiable attributes)
        p_new = names_dict[p]

        #create the foaf:person
        anonymized_graph.add((p_new, RDF.type, FOAF.Person))
        
        #add sensitive attributes
        if senstive_attributes != None:
            for senstive_attribute in senstive_attributes:
                anonymized_graph.add((p_new, getattr(FOAF, senstive_attribute), Literal(fnhc_dict[p][senstive_attribute])))
                #bind foaf

        #add attributes
        if attributes != None:
            for attribute in attributes:
                anonymized_graph.add((p_new, getattr(FOAF, attribute), Literal(fnhc_dict[p][attribute])))
                #bind foaf
    
        #add unidirectional connections
        if unidirectional_connections != None:
            for unidirectional_connection in unidirectional_connections:
                for entry in fnhc_dict[p][unidirectional_connection]:
                    anonymized_graph.add((p_new, getattr(FOAF, unidirectional_connection),
                        Literal("%s" %entry)))


        #add bidirectional connections
        if bidirectional_connections != None:
            for bidirectional_connection in bidirectional_connections:
                for bidi in fnhc_dict[p][bidirectional_connection]:
                    bidi = names_dict[bidi]
                    anonymized_graph.add((
                        p_new,
                        getattr(FOAF, bidirectional_connection),
                        Literal("%s" %bidi)
                        ))

    anonymized_graph.bind("foaf", FOAF)    
    return anonymized_graph

