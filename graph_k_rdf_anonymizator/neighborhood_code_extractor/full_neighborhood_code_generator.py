#Libraries
from rdflib import URIRef, RDF
from rdflib.namespace import ClosedNamespace
from namespace import *

def fnhcGenerator(g, args, dict_merge_bidirectional, dict_weigths):

    '''
        Function that takes a graph as an input and returns the FNHC of every person stored in a dictionary.
        The URI of each person is the key to get the Fnhc of that person.
        For bidrectional connections,  the ones with same semantic connection are merged, but not encoded yet. 
    '''

    #empty dict where all FNHC of each person will be stored
    FNHC_dict = {}

    # Store information from one-hop-neighborhood of each person in a dict
    for person in g.subjects(RDF.type, FOAF.Person):

        #start a dict for the neighborhood code of each person
        FNHC_dict[person] = {}

        #start count for the degree of the rdf graph
        degree = 0 #every connection (either attributes, projects or friends) will increase degree by 1

        #loop over the attributes to extract neighborhood codes --> always check if this connection type exists
        if args.attributes != None:
            for attribute in args.attributes:
                for entry in g.objects(person, getattr(FOAF, attribute)):
                    FNHC_dict[person][attribute] = entry.toPython() #trying to solve and encoding problem when importing data 
                    degree = degree + 1

        #loop over unidirectional connections to extract neighborhood codes --> always check if this connection type exists 
        if args.unidirectional_connections != None:
            for uni_con in args.unidirectional_connections:
                uni_con_list = []
                for entry in g.objects(person, getattr(FOAF, uni_con)):
                    uni_con_list.append(entry.toPython())
                    degree = degree + 1
                FNHC_dict[person][uni_con] = sorted(uni_con_list)

        #loop over bidirectional connections and extract them (raw) --> always check if this connection type exists
        if args.bidirectional_connections != None:
            for bi_con in args.bidirectional_connections:
                bi_con_list = []
                for entry in g.objects(person, getattr(FOAF, bi_con)): #entries expected to be URI's :)
                    bi_con_list.append(entry)
                    degree = degree + 1
                FNHC_dict[person][bi_con] = bi_con_list

        #ADD DEGREE to the dict
        FNHC_dict[person]["degree"] = degree

        #add also sensitive attributes
        if args.senstive_attributes != None:
            for sens in args.senstive_attributes:
                    for entry in g.objects(person, getattr(FOAF, sens)):
                        FNHC_dict[person][sens] = entry.toPython().encode("latin1").decode("utf8") #trying to solve and encoding problem when importing data 

        #perform the transformation of bidirectional objects that are supposed to be merged
        for new_connection_type in dict_merge_bidirectional:
            new_connection_type_entries = []
            for type in dict_merge_bidirectional[new_connection_type]:
                for entry in FNHC_dict[person][type]:
                    new_connection_type_entries.append(entry)
                #delete type for this person (not needed anymore)
                del FNHC_dict[person][type]

            #add new type and its connections for this person
            FNHC_dict[person][new_connection_type] = list(dict.fromkeys(new_connection_type_entries)) #no duplicates

    #update the bidirectional_connections list
    for new_connection_type in dict_merge_bidirectional:
        args.bidirectional_connections.append(new_connection_type) #append new types
        mean_weight = 0
        count = 0
        for type in dict_merge_bidirectional[new_connection_type]:
            args.bidirectional_connections.remove(type) #remove old types
            #also weigths need to be updated
            mean_weight = mean_weight + dict_weigths[type]
            count = count + 1
            del dict_weigths[type]
        #compute weight of the new connection
        mean_weight = mean_weight/count
        dict_weigths[new_connection_type] = mean_weight

    #and finally return the dictionary and the updated unidirectional connections
    return FNHC_dict, args.bidirectional_connections



