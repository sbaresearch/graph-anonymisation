# Theoretical background

This repository includes the implementation described in the paper [Anonymisation of Heterogeneous Graphs with Multiple Edge types](https://link.springer.com/chapter/10.1007/978-3-031-12423-5_10). The paper was presented on 22nd of August of 2022 at [DEXA conference in Vienna](https://www.dexa.org/). 

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

# Cite this paper 

Alamán Requena, G., Mayer, R., Ekelhart, A. (2022). Anonymisation of Heterogeneous Graphs with Multiple Edge Types. In: Strauss, C., Cuzzocrea, A., Kotsis, G., Tjoa, A.M., Khalil, I. (eds) Database and Expert Systems Applications. DEXA 2022. Lecture Notes in Computer Science, vol 13426. Springer, Cham. https://doi.org/10.1007/978-3-031-12423-5_10

```
 @InProceedings{10.1007/978-3-031-12423-5_10,
    author="Alam{\'a}n Requena, Guillermo
    and Mayer, Rudolf
    and Ekelhart, Andreas",
    editor="Strauss, Christine
    and Cuzzocrea, Alfredo
    and Kotsis, Gabriele
    and Tjoa, A. Min
    and Khalil, Ismail",
    title="Anonymisation of Heterogeneous Graphs with Multiple Edge Types",
    booktitle="Database and Expert Systems Applications",
    year="2022",
    publisher="Springer International Publishing",
    address="Cham",
    pages="130--135",
    abstract="Anonymisation is a strategy often employed when sharing and exchanging data that contains personal and sensitive information, to avoid possible record identification or inference. Besides the actual attributes contained within a dataset, also certain other aspects might reveal information on the data subjects. One example of this is the structure within a graph, i.e. the connection between nodes. These might allow to re-identify a specific person, e.g. by knowledge of the number of connections for some individuals within the dataset.",
    isbn="978-3-031-12423-5"
}
```

# References

1. Campan, A., Truta, T.M.: Data and structural k-anonymity in social networks.
In: Bonchi, F., Ferrari, E., Jiang, W., Malin, B. (eds.) PInKDD 2008. LNCS, vol.
5456, pp. 33–54. Springer, Heidelberg (2009). https://doi.org/10.1007/978-3-642-
01718-6 4
2. Feder, T., Nabar, S.U., Terzi, E.: Anonymizing graphs, October 2008.
arXiv:0810.5578
3. Heitmann, B., Hermsen, F., Decker, S.: k - RDF-Neighbourhood anonymity: combining
structural and attribute-based anonymisation for linked data. In: Workshop
on Society, Privacy and the Semantic Web - Policy and Technology (PrivOn),
Vienna, Austria (2017). http://ceur-ws.org/Vol-1951/PrivOn2017 paper 3.pdf
4. Hu, Z., Dong, Y., Wang, K., Sun, Y.: Heterogeneous graph transformer. In: The
Web Conference 2020, pp. 2704–2710, WWW. ACM, Taipei, Taiwan, April 2020.
https://doi.org/10.1145/3366423.3380027
5. H¨ubscher, G., et al.: Graph-based managing and mining of processes and data in
the domain of intellectual property. Inf. Syst. 106, 101844 (2022). https://doi.org/
10.1016/j.is.2021.101844
6. Ji, S., Mittal, P., Beyah, R.: Graph data anonymization, de-anonymization attacks,
and de-anonymizability quantification: a survey. IEEE Commun. Surv. Tutorials
19(2), 1305–1326 (2017). https://doi.org/10.1109/COMST.2016.2633620
7. Liu, K., Terzi, E.: Towards identity anonymization on graphs. In: ACM SIGMOD
International Conference on Management of Data, p. 93, SIGMOD. ACM Press,
Vancouver, Canada (2008). https://doi.org/10.1145/1376616.1376629
8. Mohapatra, D., Patra, M.R.: Anonymization of attributed social graph using
anatomy based clustering. Multimedia Tools Appl. 78(18), 25455–25486 (2019).
https://doi.org/10.1007/s11042-019-07745-4
9. Zheleva, E., Getoor, L.: Preserving the privacy of sensitive relationships in graph
data. In: Bonchi, F., Ferrari, E., Malin, B., Saygin, Y. (eds.) PInKDD 2007. LNCS,
vol. 4890, pp. 153–171. Springer, Heidelberg (2008). https://doi.org/10.1007/978-
3-540-78478-4 9
10. Zhou, B., Pei, J.: Preserving privacy in social networks against neighborhood
attacks. In: International Conference on Data Engineering, pp. 506–515, ICDE.
IEEE, Cancun, Mexico, April 2008. https://doi.org/10.1109/ICDE.2008.4497459
