#import functions for similarity computation
from similarity_computation_and_generalization.similarityComputation import *
from similarity_computation_and_generalization.generalization import *
from similarity_computation_and_generalization.buildRDF import *

def k_RDF_Anonymity(fnhc_dict: dict, k: int, attributes: list, unidirectional_connections: list, bidirectional_connections: list, weigths: list, hierarchies: dict, sensitive_attributes: list):
     
     #compute a list of people to be anonymized
     people = [p for p in fnhc_dict]

     #as long as there are already enough people to be anonymized in two
     #different groups of size k
     while len(people) >= 2*k:

         ##print("\n\n\n An iteration begins...")

         #select the node representing the person with biggest one-hop-
         #neighborhood (i.e. highest degree)

         #define maximum initially to 0
         maximum = 0 
         #over all people in the graph
         for i in people:
             # check whether the degree is larger than current maximum
            if fnhc_dict[i]["degree"] > maximum:
                    # if yes --> set degree to maximum
                    maximum = fnhc_dict[i]["degree"]
                    #assign temporaly this URI (person) as target
                    target = i
        
         ##print("\nThe current node in the graph with highest degree is: %s with a total degree of %s" %(target, maximum))

         #remove target from the people's list (wonn't be used anymore)
         people.remove(target)
         
         #start and empty similarity dict
         sim_dict = {}

         #compute similarity between current target and the other person
         for u in people:
             #list to save similarity of each type of connection
             sim_list_u = []
             
             #similarity attributes
             if attributes != None:
                for attribute in attributes:
                    ##print("target", fnhc_dict[target][attribute])
                    ##print("u", fnhc_dict[u][attribute])

                    if (attribute in fnhc_dict[target].keys()) & (attribute in fnhc_dict[u].keys()):
                        sim = sim_attributes(fnhc_dict[target], fnhc_dict[u], hierarchies[attribute], attribute)

                    else:
                        sim = 1
                    sim_list_u.append(sim)
                    ##print("sim", sim, "\n")

             #similarity unidirectional connections
             if unidirectional_connections != None:
                for unidirectional_connection in unidirectional_connections:
                    ##print("target", fnhc_dict[target][unidirectional_connection])
                    ##print("u", fnhc_dict[u][unidirectional_connection])
                    if (unidirectional_connection in fnhc_dict[target].keys()) & (unidirectional_connection in fnhc_dict[u].keys()):
                        sim = sim_unidirectional_connections(fnhc_dict[target], fnhc_dict[u], unidirectional_connection)
                    elif unidirectional_connection in fnhc_dict[target].keys():
                        sim = len(fnhc_dict[target][unidirectional_connection])
                    elif unidirectional_connection in fnhc_dict[u].keys():
                        sim = len(fnhc_dict[u][unidirectional_connection])
                    else:
                        sim = 0                
                    sim_list_u.append(sim)
                    ##print("sim", sim, "\n")

             #similarity bidirectional_connections
             if bidirectional_connections !=None:
                for bidirectional_connection in bidirectional_connections:
                    ##print("target", fnhc_dict[target][bidirectional_connection])
                    ##print("u", fnhc_dict[u][bidirectional_connection])

                    if (len(fnhc_dict[target][bidirectional_connection])>0) & (len(fnhc_dict[u][bidirectional_connection])>0):
                        #code --> i.e. minimum code attached to the bidirectional connection that enters the loop
                        code = "full_code_%s" %bidirectional_connection
                        copy_target = copy.deepcopy(fnhc_dict[target][code])
                        copy_u = copy.deepcopy(fnhc_dict[u][code])
                        sim = sim_bidirectional_connections(copy_target, copy_u, complete_similarity=False) #complete similarity was discarded during meetings (it refers to the possibility of updating edge every single time)


                    elif (len(fnhc_dict[target][bidirectional_connection])>0):
                        sim = len(fnhc_dict[target][bidirectional_connection])

                    elif (len(fnhc_dict[u][bidirectional_connection])>0):
                        sim = len(fnhc_dict[u][bidirectional_connection])
                    else:
                        sim = 0                

                    
                    sim_list_u.append(sim)
                    ##print("sim", sim, "\n")
                
                    #print(u, sim_list_u)

             #store similarities in the dictionary
             sim_dict[u] = similarityComputation(weigths, sim_list_u)
        

         #list where most similar verticies to target will be stored
         best_fitting_vertices = []


        #  for i in sim_dict:
        #      #print(i, ": ", sim_dict[i])

         #make a list with the k-1 most similar vertices with respect to target
         for i in range(k-1):
            #get current minimum value from similarity dict
            u = min(sim_dict, key=sim_dict.get)
            #store that person as best fitting vertex
            best_fitting_vertices.append(u)
            #delete that person from the dictionary
            del sim_dict[u]
                 
         #define the neighborhood
         neighborhood = best_fitting_vertices.copy()
         neighborhood.append(target)

        #  #print("NEIGHBORHOOD", neighborhood)

        #  exit()

        #  #print("\nAfter computing similarities with every other node, the neighborhood of %s is %s" %(target, best_fitting_vertices))
         # apply graph modification algorithm to target and most similar nodes
         # graph_modification(best_fitting_vertices,target)

        #  #print("Before: ")
        #  for p in neighborhood:
        #      #print("Person: ", p, "\nAttributes:", fnhc_dict[p], "\n\n")
         
         #Generalization of attributes, unidirectional_connections and bidirectional_connections
         if attributes != None:
            for attribute in attributes:
                fnhc_dict = generalize_attribute(neighborhood, fnhc_dict, hierarchies[attribute], attribute)
         if unidirectional_connections != None:
            for unidirectional_connection in unidirectional_connections:
                fnhc_dict = generalize_unidirectional_connection(neighborhood,fnhc_dict,unidirectional_connection)

         if bidirectional_connections != None:
            for bidirectional_connection in bidirectional_connections:
                fnhc_dict = generalize_biderctional_connections(neighborhood, fnhc_dict, people, bidirectional_connection)
         
        #  #print("After: ")
        #  for p in neighborhood:
        #      #print("Person: ", p, "\nAttributes:", fnhc_dict[p], "\n\n")
         

         #remove best fitting vertices from people too (they are already in one neighborhood)
         for vertex in best_fitting_vertices:
            people.remove(vertex)
    
     # graph modification for remaining EOIs (outside the loop)
     # their size is already lower than 2*(k-1) --> i.e two groups of size k cannot
     # be separated.
     #Generalization of attributes, unidirectional_connections and bidirectional_connections
     if attributes != None:
        for attribute in attributes:
            fnhc_dict = generalize_attribute(people, fnhc_dict, hierarchies[attribute], attribute)
    
     if unidirectional_connections != None:
        for unidirectional_connection in unidirectional_connections:
            fnhc_dict = generalize_unidirectional_connection(people,fnhc_dict,unidirectional_connection)

     if bidirectional_connections != None: 
        for bidirectional_connection in bidirectional_connections:
            fnhc_dict = generalize_biderctional_connections(people, fnhc_dict, people, bidirectional_connection)

        #  show anonymized dict         
        #  for p in fnhc_dict:
        #      #print("\n\n\n", p)
        #      for a in fnhc_dict[p]:
        #          #print(a, ": ", fnhc_dict[p][a])

     # TRANSOFRM DICT TO A GRAPH
     g_anonymized = build_rdf(fnhc_dict, attributes, unidirectional_connections, bidirectional_connections, sensitive_attributes)
     #  #print(g_anonymized.serialize(format="ttl"))
     return  g_anonymized
