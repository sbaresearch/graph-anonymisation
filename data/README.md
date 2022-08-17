# Data Folder

This folder contains all inputs, support files and outputs for the graph anonymization algorithm.


## Inputs

- Hierarchies: contains csv files used by the  graph generator for random generation of attributes (i.e., age) and by the graph anonymization algorithm (to generalize those attributes).
- Names: contains a subset of first and last names used by the graph generator to randomly create names for the FOAF.Person nodes. 

## Generated graphs

Contains txt files with the RDF generated graphs by the graph_generator. The naming convention is <name_of_graph>_<n_people>_<timestamp>.txt

## Anonymized graph

Contains txt files with the anonymized graphs. The naming convention is the same as for the generated graphs: <name_of_graph>_<n_people>_<timestamp>.txt