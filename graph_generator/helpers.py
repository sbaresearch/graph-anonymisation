#Library imports
import pandas as pd
import random
import csv
from rdflib import Literal, Graph, RDF
from namespace import *
import datetime

"""
    Helper functions to be used in the main.py file
    - hierarchy_reader: reads a hierarchy file to be used for attribute generalization
    - generate_full_name: generates a list of random full names
    - read_txt_file: reads a text file and returns a list of comma-separated elements
    - generate_rdf: generates an RDF graph with FOAF vocabulary specification which fits the expected input of the implemented graph anonymization algorithm
"""

# reads a hierarchy file file dataset and renames columns
# the expected format of the hierarchy file is the same as when exporting a hierarchy file from ARX anonymization tool
# example: data\hierarchies\age.csv
def hierarchy_reader(filename: str):
    df = pd.read_csv(filename, sep=";", header=None) #note the separator when exporting file from ARX
    column_names = ["level_%s" %i for i in range(len(df.columns))] #provide customized column names
    df.columns = column_names
    df = df.astype(str)
    return df 

#gets a list of first names, a list of last names and a number of people and generates a list of random full names
def generate_full_name(first_names,last_names, n):
    names = []
    for i in range(n):
        names.append("".join(random.choice(first_names)+"_"+random.choice(last_names)))
    return names

#reads a text file and returns a list of comma-separated elements
def read_txt_file(filename):
    with open(filename, newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
        #flatten list of lists
        data = [item for sublist in data for item in sublist]
    return data

#generates an RDF graph with FOAF vocabulary specification which fits the expected input of the implemented graph anonymization algorithm
def generate_rdf(
    attributes_dict: dict,
    unidirectional_connections_dict: dict,
    bidirectional_connections_dict: dict,
    preamble: str,
    n_people: int,
    graph_name: str,
    first_names: list,
    last_names: list):
    
    #PREPROCESSING
    #random seed initialization for reproducibility in subsequent runs
    random.seed(11)
    #empty graph element where whole RDF graph will be stored
    g = Graph()
    #generate random names for the people (nodes)
    full_names = generate_full_name(n=n_people,
                                    first_names=first_names,
                                    last_names=last_names)

    #each person should have a URI associated with a subject, object and predicate
    #full names are used for this purpose
    #URIs are stored in a list
    URIs = [URIRef("%s/%s_%s" %(preamble, full_names[i], i)) for i in range(n_people)]
    
    
    #GRAPH GENERATION
    #loop over the number of nodes to be created
    for i in range(n_people):
        #create a FOAF.Person Object and FOAF.name attribute for each node
        URI = URIs[i]
        g.add((URI, RDF.type, FOAF.Person))
        g.add((URI,FOAF.name, Literal(full_names[i])))
        
        #generate the attributes using the hierarchies
        #level 0 indicates the raw value of a hierarchy attribute (every allowed value is iin that column)
        for att in attributes_dict:
            g.add((URI, getattr(FOAF, att), Literal(random.choice(attributes_dict[att]["level_0"]))))
        
        #generate unidirectional connections
        #a person can work as maximum in ALL possible values of the respective unidirectional connection
        for uni in unidirectional_connections_dict:
            uni_connections = random.sample(unidirectional_connections_dict[uni], random.randint(1, len(unidirectional_connections_dict[uni])))
            for u in uni_connections:
                g.add((URI, getattr(FOAF, uni), Literal("%s" %u)))

        #generate bidirectional connections
        for bi in bidirectional_connections_dict:
            bidi_connections = random.sample(URIs[:i] + URIs[i+1:], random.randint(1, int(bidirectional_connections_dict[bi])))
            for b in bidi_connections:
                g.add((URI, getattr(FOAF,bi), b))

    #bind namespace to a prefix
    g.bind("foaf", FOAF)
    
    #Friends have been assigned randomly, however this has been done only in one direction
    #It is a condition that if x knows y, y should also know x (bidirectional logic)
    #Ensure that this condition is met
    for bi in bidirectional_connections_dict:
        #for every person x amd every friend of person x
        for person_x in g.subjects(RDF.type, FOAF.Person):
            for bidi in g.objects(person_x, getattr(FOAF, bi)):
                #for every other person y
                for person_y in g.subjects(RDF.type, FOAF.Person):
                    if person_x == person_y:
                        pass
                    #if friend of person x is person y, then add the person to the list of friends of person y (if not already there)
                    if bidi == person_y:
                        if person_x in [f for f in g.objects(person_y, getattr(FOAF, bi))]:
                            pass
                        else:
                            g.add((person_y, getattr(FOAF, bi), person_x))
                    else:
                        pass
    
    #save the graph to data/generated_graphs/
    #storage logic is the following: <graph_name>_<number_of_people_in_the_graph>_<generation_timestamp>.txt
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    destination_file = f"data/generated_graphs/{graph_name}_{n_people}_{timestamp}.txt"
    g.serialize(format="ttl", destination = destination_file)
    

    print("Job finished successfully. Exiting...")
    print(f"Graph destination path: {destination_file}")
    print(f"Number of people: {n_people}")
    print(f"Attributes: {attributes_dict.keys()}")
    print(f"Unidirectional connections: {unidirectional_connections_dict}")
    print(f"Bidirectional connections: {bidirectional_connections_dict}")
    print(f"Preamble: {preamble}")
    print("Shutting down...")

    #return the generated graph
    return g