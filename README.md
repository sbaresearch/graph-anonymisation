# Theoretical background

This repository includes the implementation described in the papers [Anonymisation of Heterogeneous Graphs with Multiple Edge types](https://link.springer.com/chapter/10.1007/978-3-031-12423-5_10) (presented at the [2022 DEXA conference in Vienna, Austria](https://www.dexa.org/)) and its extension in [ An Efficient Approach for Anonymising the Structure of Heterogeneous Graphs](https://ieeexplore.ieee.org/document/10020301) (presented at the [2022 IEEE Big Data conference in Osaka, Japan](http://bigdataieee.org/BigData2022/)).

# How to use it

1. Install the [requirements](https://gitlab.sba-research.org/machine-learning/graph-anonymisation/-/blob/3629069e6e9b84fedb52e603e3edb425ab6866fa/requirements.txt).
2. Generate a sample graph by running our [graph generator](https://gitlab.sba-research.org/machine-learning/graph-anonymisation/-/blob/d99eb80e735b5c6bce172501badf3c1ac78cf6f5/graph_generator/main.py). 

```bash
python graph_generator/main.py --attributes 'age' 'based_near' --hierarchies 'data/inputs/hierarchies/age.csv' 'data/inputs/hierarchies/austrian_cities.csv' --unidirectional_connections currentProject '[1, 2, 3]' Organization '[TU, UniWien]' --bidirectional_connections 'knows' '3' 'callTo' '3' --graph_name 'graph_generator_test' --n_people '10' --preamble 'www.examplepreamble.org/'

# Output in data/generated_graphs
```

* attributes: Name of the attributes to be generated
* hierarchies: Path to hierarchy files that are used for attribute generation
* unidirectional_connections: Name of the unidirectional connections to be created and their possible values
* bidirectional_connections: Name of the bidirectional connections to be generated and the maximum amount of connections between nodes (for each)
* graph_name: Name of graph that will be generated (a timestamp and the number of people will be added by default)
* n_people: Number of foaf:Person nodes to be generated
* preamble: Preamble for the URI of each node


Please, note that if some of the connections that you wish to generate do not belong to the FOAF namespace, they should be added as *custom* in [here (see examples)](https://gitlab.sba-research.org/machine-learning/graph-anonymisation/-/blob/d99eb80e735b5c6bce172501badf3c1ac78cf6f5/graph_generator/namespace.py).

*Or alternatively, import your own rdf graph in a txt file in data/generated_graphs (make sure it is in turtle format)*

3. Run the graph [k-rdf-anonymization algorithm](https://gitlab.sba-research.org/machine-learning/graph-anonymisation/-/blob/3629069e6e9b84fedb52e603e3edb425ab6866fa/graph_k_rdf_anonymizator/main.py).

```bash
python graph_k_rdf_anonymizator/main.py --graph_file 'data/generated_graphs/graph_generator_test_10_20220815210936.txt' --attributes 'age' 'based_near' --hierarchies 'data/inputs/hierarchies/age.csv' 'data/inputs/hierarchies/austrian_cities.csv' --unidirectional_connections 'currentProject' 'Organization' --bidirectional_connections 'knows' 'callTo' --k '2'

# Output in: data/anonymized_graphs
```

* graph_file: RDF graph to be anonymized (generated or imported)
* attributes: List of attribute connections to be anonymized
* hierarchies: List of hierarchies to be used for the attribute generalization
* unidirectional_connections: List of unidirectional connections to be anonymized
* bidirectional_connections: List of bidirectional connections to be anonymized 
* k: K-parameter for the anonymization

# Output in: data/anonymized_graphs


Note that there are some **additional arguments** that can be provided to the anonymization algorithm: 

```bash
-- sensitive_attributes has_disease -- merge_bidirectional_connectionls 'messageConnections: emails, letters' -- weights age, 0.5, based_near, 0.7... 
```

* sensitive_attributes: Sensitive attributes to be kept as they are originally
* merge_bidirectional_connectionls: Enter which bidirectional connections should be merged together because, for instance, they are semantically similar. This adds an extra-layer of security to the anonymization and simplifies the graph in terms of semantics.
* weights: Enter the weights of each of the connections for the dissimilarity computation algorithm. Weights are normalized afterwards. 


**Disclaimer:** this project was aimed at testing the new heterogeneous graph anonymization approach presented in [Anonymisation of Heterogeneous Graphs with Multiple Edge types](https://link.springer.com/chapter/10.1007/978-3-031-12423-5_10). However, it has not been tested for every possible RDF input graph and the user may have to adapt some functions to make it work with a customized input. 

# Cite the papers


Alamán Requena, G., Mayer, R., Ekelhart, A. (2022). "An Efficient Approach for Anonymising the Structure of Heterogeneous Graphs,". In: 2022 IEEE International Conference on Big Data (Big Data), Osaka, Japan, 2022, doi: 10.1109/BigData55660.2022.10020301. https://ieeexplore.ieee.org/document/10020301


```
@inproceedings{alaman_requena_efficient_2022,
		title = {An {Efficient} {Approach} for {Anonymising} the {Structure} of {Heterogeneous} {Graphs}},
		author = {Alamán Requena, Guillermo and Mayer, Rudolf and Ekelhart, Andreas},
		booktitle = {2022 {IEEE} {International} {Conference} on {Big} {Data} ({Big} {Data})},
		url = {https://ieeexplore.ieee.org/document/10020301/},
		doi = {10.1109/BigData55660.2022.10020301},
		publisher = {IEEE},
		address = {Osaka, Japan},
		month = dec,
		year = {2022},
	}
```

Alamán Requena, G., Mayer, R., Ekelhart, A. (2022). "Anonymisation of Heterogeneous Graphs with Multiple Edge Types". In: Database and Expert Systems Applications. DEXA 2022. Lecture Notes in Computer Science, vol 13426. Springer, Cham. https://doi.org/10.1007/978-3-031-12423-5_10

```
@inproceedings{alaman_requena_anonymisation_2022,
		title = {Anonymisation of {Heterogeneous} {Graphs} with {Multiple} {Edge} {Types}},
		author = {Alamán Requena, Guillermo and Mayer, Rudolf and Ekelhart, Andreas},
		booktitle = {Database and {Expert} {Systems} {Applications}},
		publisher = {Springer International Publishing},
		address = {Cham},
		series = {{DEXA}},
		doi = {10.1007/978-3-031-12423-5\_10},
		month = aug,
		year = {2022},
		abstract = {Anonymisation is a strategy often employed when sharing and exchanging data that contains personal and sensitive information, to avoid possible record identification or inference. Besides the actual attributes contained within a dataset, also certain other aspects might reveal information on the data subjects. One example of this is the structure within a graph, i.e. the connection between nodes. These might allow to re-identify a specific person, e.g. by knowledge of the number of connections for some individuals within the dataset.},
}
```


