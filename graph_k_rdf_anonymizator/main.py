# Library imports
import argparse
from datetime import datetime
from helpers import *
from neighborhood_code_extractor.full_neighborhood_code_generator import *
from neighborhood_code_extractor.encoding_bidirectional_connections import *
from similarity_computation_and_generalization.kRdfAnonymizationAlgorithm import *

#############
# Argparser #
#############

ap = argparse.ArgumentParser()
ap.add_argument("--graph_file", type=str,
                help="Enter path to RDF graph file in ttl format.", required=True)
ap.add_argument("--senstive_attributes", nargs="+",
                help="Enter senstive attributes to be kept.", required=False, default=None)
ap.add_argument("--attributes", nargs="+",
                help="Enter name of the attributes to be generalized.", required=False, default=None)
ap.add_argument("--hierarchies", nargs="+",
                help="Enter the hierarchies to be used to generalize attributes. There should be exactly as many hierarchies as attributes.",
                 required=False)
ap.add_argument("--unidirectional_connections", nargs="+",
                help="Enter the name of the unidirectional connections that should be generalized.",
                 required=False, default=None)
ap.add_argument("--bidirectional_connections", nargs="+",
                help="Enter the name of the bidirectional connections that should be generalized.",
                 required=False, default=None)
ap.add_argument("--merge_bidirectional_connections",
     nargs="+",
     required=False,
     help="""Enter which bidirectional connections should be merged together. Formatting: 'messageConnections: emails, letters'
        """)
ap.add_argument("--k", type=int, help="Size of k for anonymization", required=True)
ap.add_argument("--weights", nargs="+",
                help="Enter the weigths of each of the connections for the anonymization. Example: 'age', 0.5, 'based_near', 0.7...", required=False)
args = ap.parse_args()

# Validate Arguments
validate_args = validate_args(args)
if validate_args == True:
    print("Arguments provided have been validated.")

#################
# Preprocessing #
#################

print("\nStarting preprocessing of parameters...")

# Bidirectional connections with same semantic meaning are allowed to be merged. If the argument, this info is processed here and be stored in a dictionary.
print("\nPreprocessing Bidirectional Connections")
if args.merge_bidirectional_connections:
    dict_merge_bidirectional = process_merge_bidirectional_arg(args.merge_bidirectional_connections)
    print("Bidirectional connections with same semantic meaning to be merged (key,value): %s" %dict_merge_bidirectional)
else:
    dict_merge_bidirectional = {}
    print("No bidirectional connections to be merged.")
print("Preprocessing bidirectional connections finished.")

#Weigths - a dictionary will all the information about the weights of each attribute/connection needs to be created (if provided, else default is 1 for allº)
print("\nPreprocessing Weights")
dict_weigths, all_properties = process_weights_arg(args)
print("Preprocessing weights finished.")


#########################
# Load Target RDF Graph #
#########################

g = Graph()
g.parse(args.graph_file, format="ttl", encoding = "utf-8")


##############################
# Call the anonymization job #
##############################

if __name__ == "__main__":

    start_time = datetime.now()

    # 1. Full neighborhood code computation
    print("\nComputing Full Neighborhood Code (FNHC)...")
    fnhc_dict, args.bidirectional_connections = fnhcGenerator(g, args, dict_merge_bidirectional, dict_weigths)
    print("\nEncode bidirectional connections")
    fnhc_dict = compute_fnhc_bidirectional(fnhc_dict, args.bidirectional_connections)
    print("\nFNHC computed.")
    print("Total time to compute FNHC: ", datetime.now() - start_time)

    # load hierarchies & save in a dictionary
    print("\nLoading hierarchies for generalization of the attributes...")
    hierarchies = {}
    count = 0
    if args.attributes != None:
        for attribute in args.attributes:
            hierarchies[attribute] = attribute_reader(args.hierarchies[count])
            count = count+1
    print("Hierarchies loaded.")

    #convert dicitonary with all properties to two lists
    #make a list of all the attributes to be generalized (order_list)
    #and use a list of weigths (weights)
    order_list = all_properties.copy()
    weights = []
    #append weigths using the specified order
    for conn in order_list:
        weights.append(dict_weigths[conn])

    print("\nCall main function to anonymize the graph (containing 2. Similarity computation and 3. Generalization)...")
    g_anonymized = k_RDF_Anonymity(fnhc_dict, args.k, args.attributes, args.unidirectional_connections, args.bidirectional_connections, weights, hierarchies, args.senstive_attributes)
    print("Anonymization finished.")

    # show results & #save graph
    print("\nSaving anonymized graph...")
    output_file_name = args.graph_file.replace("data/generated_graphs/", "").replace(".txt","")
    g_anonymized.serialize(format="ttl", destination = "data/anonymized_graphs/%s.txt" %output_file_name)
    print("Anonymized graph saved.")

    #terminate script
    print("\nShutting down...")

    #########################################################################################################