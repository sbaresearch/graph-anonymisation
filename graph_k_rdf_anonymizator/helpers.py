from rdflib import Graph
import pandas as pd

"""
    Some helper functions for graph anonymization main script
"""

#INPUT VALIDATION
def validate_args(args):

    """Raises several errors if input is incorrect

    Raises:
        ValueError: if attributes do not match hierarchies
        ValueError: raises errors if not all weights provided (No weights is fine --> turns to default)
    """

    print("\nValidating arguments...")

    # attributes not matching hierarchies
    if len(args.attributes) != len(args.hierarchies):
        raise ValueError(
            "Length of attributes to generalize and lenght of hierarchies do not match.")

    # weights not matching numbers of connections
    if args.weights:
        if len(args.weights)/2 != len(args.attributes + args.unidirectional_connections + args.bidirectional_connections):
            raise ValueError("Weights not matching numbers of connections.")
    
    return True

#PROCESSING
def process_merge_bidirectional_arg(list_merge_bidirectional):
    """
        Bidirectional connections with same semantic meaning are allowed to be merged. 
        If the argument, this info is processed here and be stored in a dictionary.

        Example from input entered in argument:  "message connections: knows, callTo" 
        to structured information storage {'MessageConnections': ['knows', 'call To']}    
    """
    dict_merge_bidirectional = {}
    for l in list_merge_bidirectional:
        l = l.replace(" ", "")
        key = l.split(':')[0]
        values = l.split(':')[1].split(',')
        dict_merge_bidirectional[key] = values

    return dict_merge_bidirectional

def process_weights_arg(args):
    
    """
        Converts weights arg to a structured dictionary (if provided)
        Else, it assigns default values
    """

    #create a list of properties in order
    all_properties = []
    #check if they are None because it could happen that some of the connections is not in the network (i.e. knop2D export3)
    if args.attributes != None: 
        all_properties += args.attributes

    if args.unidirectional_connections != None: 
        all_properties += args.unidirectional_connections

    if args.bidirectional_connections != None: 
        all_properties += args.bidirectional_connections

    #customized
    if args.weights:
        list_weights = args.weights
        dict_weigths = {}

        for i in range(0, len(list_weights), 2):
            dict_weigths[list_weights[i]] = float(list_weights[i+1])

    #default
    else:
        #create dictionary with weights and set default (1)	- as described in the paper - to review so that it makes sense with similarity
        dict_weigths = {}

        for p in all_properties:
            dict_weigths[p] = 1
    
    return dict_weigths, all_properties

#LOAD DATA
#Read hierarchies
def attribute_reader(filename):
    df = pd.read_csv(filename, sep=";", header=None)
    column_names = ["level_%s" %i for i in range(len(df.columns))]
    df.columns = column_names
    df = df.astype(str)
    df = df.set_index("level_0")
    return df 


