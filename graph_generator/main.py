#Library imports
import argparse
from helpers import *
from namespace import *

#argument parser
ap = argparse.ArgumentParser()
ap.add_argument("--attributes", nargs="+",
				help="Enter name of the attributes to be generated.", required=False)
ap.add_argument("--hierarchies", nargs="+",
				help="Enter the path to the hierarchies to be used to generate attributes. There should be exactly as many hierarchies as attributes.", required=False)
ap.add_argument("--unidirectional_connections", nargs="+",
				help="Enter the name of the unidirectional connections that should be generated and a list of possible values.", required=False)
ap.add_argument("--bidirectional_connections", nargs="+",
				help="Enter the name of the bidirectional connections that should be generated and the maximum amount of random connections to be generated between the nodes.", required=False)
ap.add_argument("--n_people", required=True, help="Enter number of people (nodes) that it is wished to have in the generated graph", type=int)
ap.add_argument("--preamble", required=True, help="Enter a customized preamble for the URIs", type=str)
ap.add_argument("--graph_name", required=True, help="Enter a customized named to be used as a preamble of your generated graph name", type=str)
args = ap.parse_args()

# define a list of random first and last names to be used for random name generation
first_names = read_txt_file("data/inputs/names/first_names.txt")
last_names = read_txt_file("data/inputs/names/last_names.txt")

#load attributes from argparser
attributes_dict = {}
count = 0
for attribute in args.attributes:
    attributes_dict[attribute] = hierarchy_reader(args.hierarchies[count])
    count = count + 1

#load unidirectional_connections
unidirectional_connections_dict = {}
for i in range(0, len(args.unidirectional_connections),2):
    unidirectional_connections_dict[args.unidirectional_connections[i]] = args.unidirectional_connections[i+1].strip('][').split(', ')

#load bidirectional_connections
bidirectional_connections_dict = {}
for i in range(0, len(args.bidirectional_connections),2):
    bidirectional_connections_dict[args.bidirectional_connections[i]] = args.bidirectional_connections[i+1]

#call the generate_rdf job
if __name__ == "__main__":
    generate_rdf(
        attributes_dict,
        unidirectional_connections_dict,
        bidirectional_connections_dict,
        args.preamble,
        int(args.n_people),
        args.graph_name, 
        first_names,
        last_names)