###########
# IMPORTS #
###########

import random
import math

#########################
# EXTRACTING COMPONENTS #
#########################

# Find connected components of a graph (stored as a dictionary) 
# Taken from stackoverflow --> returns roots (not needed for us) and components --> therefore: MODIFICATION to return only components was done

# takes dictionary with a graph (in our case it will be neighborhood subgraphs)
def getComponents(aNeigh):
    def findRoot(aNode,aRoot):
        while aNode != aRoot[aNode][0]:
            aNode = aRoot[aNode][0]
        return (aNode,aRoot[aNode][1])
    myRoot = {} 
    for myNode in aNeigh.keys():
        myRoot[myNode] = (myNode,0)  
    for myI in aNeigh: 
        for myJ in aNeigh[myI]: 
            (myRoot_myI,myDepthMyI) = findRoot(myI,myRoot) 
            (myRoot_myJ,myDepthMyJ) = findRoot(myJ,myRoot) 
            if myRoot_myI != myRoot_myJ: 
                myMin = myRoot_myI
                myMax = myRoot_myJ 
                if  myDepthMyI > myDepthMyJ: 
                    myMin = myRoot_myJ
                    myMax = myRoot_myI
                myRoot[myMax] = (myMax,max(myRoot[myMin][1]+1,myRoot[myMax][1]))
                myRoot[myMin] = (myRoot[myMax][0],-1) 
    myToRet = {}
    for myI in aNeigh: 
        if myRoot[myI][0] == myI:
            myToRet[myI] = []
    for myI in aNeigh: 
        myToRet[findRoot(myI,myRoot)[0]].append(myI)
    
    #modified
    #store components in a list
    components = list(myToRet.values())
    
    #returns connected components
    return components


# Extract neighborhood components of each person
## First step: find friends within the neighborhood for each person and store it as a dict (common_friends)
## Second step: find components within those subgraphs (common_friends) and return connected components
def extract_components(fnhc_dict, attributes):
    
    for attribute in attributes:

        #restart knows p
        knows_p = []

        for p in fnhc_dict:

            # #print("\n\n\n Current person entering the outer loop: %s\n" %p)
            knows_p = fnhc_dict[p][attribute]


            # #print("Friends (or calls/mails or whatever) of p are: %s\n" %knows_p)
            
            common_friends = {} #or common calls or whatever

            for i in knows_p: #loop over friends, calls or whatever

                # #print("For friend (or callTo or whatever) %s of %s\n" %(i,p))

                common_friends[i] = []

                for j in knows_p:

                    # #print("For every other friend %s of %s\n" %(j,p))

                    if j in fnhc_dict[i][attribute]: #check if we have 'friends' in common (wrt to my friends)
                        
                        # #print("%s is friend of %s" %(j,i))
                        common_friends[i].append(j)

                        # #print("Update of common_friends: %s" %common_friends[i])
            
            # #print("\n\nCommon friends", p,": ", common_friends)

            #find connected components of "common_friends"
            fnhc_dict[p]["components_%s" %attribute] = {}

            filterByKey = lambda keys: {x: common_friends[x] for x in keys}

            components = getComponents(common_friends)

            # #print("components", components)

            for i in range(len(components)):
                fnhc_dict[p]["components_%s" %attribute][i] = filterByKey(components[i])
            
            ##print("Subgraphs of neighborhood of %s are: " %p)
            #for i in fnhc_dict[p]["components_%s" %attribute]:
                ##print("* ", fnhc_dict[p]["components_%s" %attribute][i])
        
    return fnhc_dict


################################
# EFFICIENT FIND ALL DFS TREES #
################################

#function to find_all_DFS paths from a connected component of a graph from a starting node
#inputs
## connected component (graph)
## source node from where to start (src)
## earliest backward edge found so far (earliest_backward)
def find_all_DFS_backwards_stop(graph, src, earliest_backward):
        
    ##print("\nAnd source node is: ", src, "\n")
        
    #dictionary where all possible DFS paths should be stored
    paths_dict = {}
    codes_dict = {}

    #start first path with src as starting node
    paths_dict[0] = [src]
    codes_dict[0] = [[0,1,None,src]]
        
    #position (to be used later to change the source node, check for parent, etc.)
    i = -1
    
    #backward found overall
    backwards_found_overall = False
    
    #list to store unblcoked paths once a backward is found
    unblocked_paths = []
    
    #reference path for the while loop
    #Until reference path is not as long as the length of the graph, the while loop keeps going
    a = 0
    
    #count iterations
    #used later to check if there are no earlier backward edges in a given path than the current earliest
    count = 0
    
    #     ##print("Current Graph (should be the same as the component): ", graph)
    
    #while the length of the paths is smaller than the length of the reference path
    #why? because we have to find paths of the size of the component
    while len(paths_dict[a])<len(graph):
        
        #if there are no earlier backward edges than the current earliest backward edge - then return an empty path
        if (count > earliest_backward) & (backwards_found_overall == False):
            ##print("There are no earlier backward edges than the current earlies backward edge: ", earliest_backward)
            return {}, {}, earliest_backward
        
        #else, continue with the iteration
        else:
            
            #new dict where the splited paths will be stored (i.e. new routes found from previous code/path)
            new_paths_loop = {}
            new_codes_loop = {}

            #to index the new paths found
            key_count = 0
            
            #to be used even if backwards_found_overall are modified during the iteration
            temporal_backwards_found_overall = backwards_found_overall
            #same for unblocked_paths
            temporal_unblocked_paths = unblocked_paths.copy()

            #for every path that we already have
            for path in paths_dict:
                
                ##print("\nPath %s entering the loop: %s" %(path, paths_dict[path]))
                ##print("Current paths in temporal unblocked", temporal_unblocked_paths)
                ##print("Current temporal backwards found overall", temporal_backwards_found_overall)
                
                #create a new dictionary for this path
                new_paths_loop[path] = {}
                new_codes_loop[path] = {}
                
                #if this path is in unblocked paths (or backward found is False and therefore temporal doesn't exist yet)
                if (path in temporal_unblocked_paths) | (temporal_backwards_found_overall == False):

                    #restart position for slicing 
                    i = - 1

                    #while the dictionary of the new path is still empty (it cannot be empty --> there must be at least
                    # one path for each)
                    while len(new_paths_loop[path]) == 0:

                        #loop over the neighbors of the last node found (determined by i)
                        for neighbor in graph[paths_dict[path][i]]:
                            #store parent of current neighbor
                            parent = paths_dict[path][i]
                            #if not visited yet --> add it to the path and increase the key_count (see below)
                            if neighbor not in paths_dict[path]:
                                ##print("New path found! How many? %s" %key_count)
                                new_paths_loop[path][key_count] = paths_dict[path] + [neighbor]
                                new_codes_loop[path][key_count] = codes_dict[path] + [[new_paths_loop[path][key_count].index(parent)+1,
                                                                                      new_paths_loop[path][key_count].index(neighbor)+1,
                                                                                      parent, neighbor]]

                                #add backward edges on the fly
                                #store a variable to check if there are backward edges found in this round yet 
                                backwards_found_this_round = False
                                
                                #if the length of the path is larger than 2 (if not, it imposible to find backward edges)
                                if len(new_paths_loop[path][key_count]) > 2:
                                    # for every node in the previous two positions (because previous is parent)
                                    for node in new_paths_loop[path][key_count][:-2]:
                                        #if this node is connected to the new node added to the path and it is not the parent
                                        #then, add backward edge                                     
                                        if (node in graph[neighbor]) & (node != parent): # Maybe shouldn't be parent by def (TO CHECK)
                                            new_codes_loop[path][key_count] = new_codes_loop[path][key_count] + [[new_paths_loop[path][key_count].index(neighbor)+1,
                                                                                                                   new_paths_loop[path][key_count].index(node)+1,
                                                                                                                   neighbor,
                                                                                                                   node]]
                    
                                            #turn backward edge found this round to true (because we are inside the if)
                                            backwards_found_this_round = True
                                            
                                            #global conditions for a good behavior of the overall algorithm
                                    
                                            #if it is the first backward edge found ever (in all iterations over this src)
                                            if backwards_found_overall == False:
                                                #Turn backwards overall to true and set this node as the reference node
                                                backwards_found_overall = True
            
                                                #switch reference path
                                                a = key_count
                                                
                                                #if the iteration where the earliest backward was found is lower or equal
                                                #than current earliest backward among ALL src(s), then update this value
                                                if count <= earliest_backward:
                                                    #update value
                                                    earliest_backward = count
                                                    #and should also eliminate all previous backward (TODO)
                                            
                                            #if temporal is false, and we found a backward (even if overall is True)
                                            if temporal_backwards_found_overall == False:
                                                #we have to append it to the unblocked (candidate paths)
                                                unblocked_paths.append(key_count)


                                #for the next neighbor, we need to update the key count 
                                #(i.e., new entry in the dict of this path)
                                key_count += 1

                        #if None of the neighbors has been added, go to the previous node and repeat the process
                        # (by definition of DFS recursion)
                        i = i - 1
                
                #if current path needs to be discarded
                else:
                    ##print("Discard this path!")
                    new_paths_loop[path][key_count] = []
                    new_codes_loop[path][key_count] = [[]]
                    key_count += 1

            #store dict with the new paths
            paths_dict = new_paths_loop
            codes_dict = new_codes_loop

            #to have same structure as before
            restore_vistied = {}
            restore_codes = {}
            
            #recover structure and indexes
            restore_indexes = []
            ##print("\nRestoring indexes...")
            
            
            ##print("Loop over the copy of paths dict indexes: ", paths_dict.copy().keys())
            for i in paths_dict.copy():
                ##print("Current parent key: ", i)
                if (len(temporal_unblocked_paths) != 0) & (i not in temporal_unblocked_paths):
                    del paths_dict[i]
                    ##print("Paths from this parent deleted because not in temporal unblocked paths.")
                    continue
                
                else:
                    ##print("Current parent key in unblocked paths: ", i in temporal_unblocked_paths)
                    ##print("For every new path of this parent:" , paths_dict[i].keys())
                    for j in paths_dict[i]:
                        ##print("j: ", j)
                        if i in temporal_unblocked_paths:
                            ##print("This condition should be always!!")
                            restore_indexes.append(j)
                            a = j #restore also reference (if not, out of index error)
                        restore_vistied[j] = paths_dict[i][j]
                        
            if len(restore_indexes) != 0:
                unblocked_paths = restore_indexes.copy()
        

            for i in codes_dict:
                for j in codes_dict[i]:
                    restore_codes[j] = codes_dict[i][j]

            paths_dict = restore_vistied
            codes_dict = restore_codes
            


        ##print("Source node: ", src[-15:])
        ##print("Keys of the dict", paths_dict.keys())
        #increase_count (for the next iteration to be compared with earliest backward)
        count += 1
    
    
    #     ##print("\nCode(s) returned: ")
    #     for i in codes_dict:
    #         ##print("\nCode %s is and starts from %s: " %(i, src[-15:]))
    #         for j in codes_dict[i]:
    #             ##print("[%s,%s]" %(j[0], j[1]))
    
    #return the dictionary with the paths
    return paths_dict, codes_dict, earliest_backward

#function that loops over source nodes of a component and finds all paths in the component
# inputs
## component 
def find_all_paths_in_component(component):
    
    #dictionary to store all paths
    all_paths = {}
    all_codes = {}
    
    #list to store the paths
    all_paths_new = {}
    all_codes_new = {}
    
    # position_earliest_backward = 0
    earliest_backward = math.inf
    
    
    #run the function in the loop (as described)
    for i in component:
        
        ##print("\n Starting with component %s" %component)
        
        prev_earliest_backward = earliest_backward
        prev_paths_keys = list(all_paths.keys())
        #call main function
        all_paths[i], all_codes[i], earliest_backward = find_all_DFS_backwards_stop(component, i, earliest_backward)
        #remove all previous node if an earliest backward is found
        if prev_earliest_backward != earliest_backward:
            for j in prev_paths_keys:
                all_paths[j] = {}
                all_codes[j] = {}
    
    #transform structure for an easier candidate choosing later on
    count = 0 
    for p in all_paths:
        if len(all_paths[p]) > 0:
            for i in all_paths[p]:
                all_paths_new[count] = all_paths[p][i]
                all_codes_new[count] = all_codes[p][i]
                count += 1

    return all_paths_new, all_codes_new, earliest_backward


#helper
#function to determine whether and edge is forward or backward
def is_forward(edge):
    if edge[0] > edge[1]:
        return False
    if edge[0] < edge[1]:
        return True

#helper
#takes to edges and returns whether edge_v < edge_w (linear order in the paper)
def linear_order(edge_v, edge_w):

    #IF SAME STRUCTURE
    if ((edge_v[0] == edge_w[0]) & (edge_v[1] == edge_w[1])):
        return "SameStructure"
    
    #edge_v < edge_w if one of the following conditions holds: 
    #variables for first condition
    both_forward = is_forward(edge_v) & is_forward(edge_w)
    secondv_lower_secondw = edge_v[1]<edge_w[1]
    firstv_larger_firstw = edge_v[0]>edge_w[0]
    if (edge_v[1] == edge_w[1]): 
        secondv_secondw = True
    else:
        secondv_secondw = False

    #FIRST CONDITION: both forward
    if both_forward & (secondv_lower_secondw | (firstv_larger_firstw & secondv_secondw)):
        return True
    
    
    #SECOND CONDITION: backward - forward (CHANGED WRT TO PAPER)
    if (is_forward(edge_v)==False) & is_forward(edge_w) & (edge_v[0] < edge_w[1]): #in paper:  (edge_v[1] < edge_w[0])
        return True
    

    #THIRD CONDITION: forward - backward (CHANGED WRT TO PAPER)
    if is_forward(edge_v) & (is_forward(edge_w)==False) & (edge_w[0]>=edge_v[1]): #in paper: (edge_v[1]<=edge_v[0])
        return True

    #variables for third condition
    first_v_lower_first_w = edge_v[0] < edge_w[0]
    if edge_v[0] == edge_w[0]:
        first_v_first_w = True
    else:
        first_v_first_w = False
    
    #FOURTH CONDITION: both backward
    if (is_forward(edge_v)==False) & (is_forward(edge_w)==False) & (first_v_lower_first_w | (first_v_first_w & secondv_lower_secondw)):
        return True

    #else edge_u < edge_v is False
    else:
        return False


#choose candidate coodes from all codes (according to rules defined in the paper)
def choose_candidate_code(all_codes, earliest_backward):
    
    #if there is a backward edge among the candidates
    if earliest_backward != math.inf:
        position = earliest_backward + 3 #3 because of the way earliest backward is computed
        
        #if the paths are shorter than 4 edges, then return one randomly, because they are identical
        #or if the backward edge is in the last position
        if (len(all_codes[0]) <= 4) | (position == len(all_codes[0])):
            return all_codes[random.choice(list(all_codes.keys()))], earliest_backward
        
    #if not, start from 2nd position (because position 0 and 1 are always 0,1 and 1,2)
    else:
        position = 2
    
        #if the paths are shorter than 3 edges, then return one randomly, because they are identical
        if len(all_codes[0]) <= 3:
            return all_codes[random.choice(list(all_codes.keys()))], earliest_backward
    
    #at the beginning just take a random path as best
    best_path = 0
    
    
    #while there is more than 1 candidate path
    while len(all_codes) > 1: 
        #list to store those paths that have the same structure as the current best
        keys_equal_to_best = []
        #for every path in our dictionary
        for path in all_codes.copy():
    #             ##print("Path: ", path)
    #             ##print("New iteration: ", all_codes[path][position], "and best path: ", all_codes[best_path][position])
            #if they have the same structure 
    #             if all_codes[path][0][3][-10:] == "r_Brown_32":
                ##print("Position: %s" %position)
                ##print("Path: %s" %path)
                ##print("All codes len: %s" %len(all_codes))
                ##print("All_codes: ", all_codes)
                ##print("Best path", best_path)
        #             ##print("All codes: %s" %all_codes)
            if linear_order(all_codes[path][position], all_codes[best_path][position]) == "SameStructure":
    #                 ##print("Same edges' structure. Continue.\n")
                    #append the path to same structure as best path
                    keys_equal_to_best.append(path)
                    #continue to next iteration (necessary?)
                    continue
                # if linear order is True, the current path is better than the old best path
            elif (linear_order(all_codes[path][position], all_codes[best_path][position]) == True):
                    # There is a new winner, thus best_path has to be updated
    #                 ##print("\nNew winner!")
    #                 ##print("The fight was: ", all_codes[path][position], " vs ", all_codes[best_path][position])
    #                 ##print("Update best path:", path)
                best_path = path
    #                 ##print("Now the best path is: ", all_codes[best_path])
    #                 ##print("And also delete all previous paths")
                #delete all the keys so far in the list "keys_equal_to_best" (because there is a new winner) - (2)
                #and also delete all codes from the dictionary of that list (1)
                for prev in keys_equal_to_best: #(1)
                    del all_codes[prev]
                keys_equal_to_best = [] #(2)

            #if the linear order is false, then delete the path because it lost agains current best
            else:
    #                 ##print("Delete path because he lost against best path.\n")
                del all_codes[path]
                continue #(necessary?)
        
        
        #condition to break the while loop
        #when the position (i.e., edge that we are checking) reaches the length of the path, then break the while loop
        #why? because even if there are more than 1 path in all_codes, we already have our candidates (we cannot check further)
        if position == (len(all_codes[best_path])-1):
    #             ##print("All codes so far: ")
    #             for i in all_codes:
    #                 ##print(all_codes[i])
            
    #             ##print("Keyys", keys_equal_to_best)
    #             ##print("Best", all_codes[best_path])
            
            #randomly return one of the best paths (as described in the paper)
            return all_codes[random.choice(list(all_codes.keys()))], earliest_backward
        
        else:
            position += 1
    #             ##print(len(all_codes))
    
    #if we are out of the while loop because there is only a candidate left, 
    #then return the code of the "best path"
    return all_codes[best_path], earliest_backward
    
# So basically, loop over components to find paths and select a candidate for each component. Aditionally, extract features to be used later.
def find_candidate_path_in_components(components):
    
    paths = {}
    codes = {}
    features = []
    #to be able to order the features properly
    id = 0 

    for component in components:
                
        paths[component], codes[component], earliest_backward = find_all_paths_in_component(components[component])
        codes[component], earliest_backward = choose_candidate_code(codes[component], earliest_backward)
        #if last element is a backward edge
        if is_forward(codes[component][-1]) == False:
            #then the number of vertices is the same as the last discovered vertex in the code (i.e. 1st position)
            n_vertices = codes[component][-1][0]
        #the second element (obvious)
        else:
            n_vertices = codes[component][-1][1]
        #number of edges of the chosen candidate
        n_edges = len(codes[component])
        features.append([n_vertices, n_edges, earliest_backward, id])
        id += 1
            
    return codes, features


#Concatenate the selected paths for each components (using features extracted). 
def concatenate_candidates(components_codes, components_features):
    
    #to store full_neighborhood_code of a node
    full_code = []
    
    #sort the features as indicated in the paper
    sorted_list_features = sorted(components_features)
    
    #loop over sorted features, store index and append the codes in that order
    for i in sorted_list_features:
        index = components_features.index(i)
        full_code.append(components_codes[index])
        
    
    return full_code

#full function to extract codes
def compute_fnhc_bidirectional_generalization(fnhc_dict, person, bidirectionals):
    
    # #print("Bidirectionals are: ", bidirectionals)
    
    #extract components
    # #print("\nExtracting components...")
    fnhc_dict = extract_components(fnhc_dict, bidirectionals)
    
    #loop over all bidirectional connections that are there
    for bidi in bidirectionals:
        #loop over every person in the graph
        for p in fnhc_dict:

            if p != person:
                continue
    
            pp =  p[-25:]
            index = pp.find("#") +2
            # #print("\nFocusing on: %s " %pp[index:])
            # #print("Number of knows connections of this person: ", len(fnhc_dict[p]["knows"]))
            # #print("Number of components of this person: ", len(fnhc_dict[p]["components_%s" %bidi]))

            #calculate candidate paths
            fnhc_dict[p]["component_codes_%s" %bidi], fnhc_dict[p]["component_codes_features_%s" %bidi]  = find_candidate_path_in_components(fnhc_dict[p]["components_%s" %bidi])

            # #print("Component codes: ", fnhc_dict[p]["component_codes_%s" %bidi], "\n")
            
            #concatenate those paths and return full code
            fnhc_dict[p]["full_code_%s" %bidi] = concatenate_candidates(fnhc_dict[p]["component_codes_%s" %bidi], fnhc_dict[p]["component_codes_features_%s" %bidi])

            
            del fnhc_dict[p]["component_codes_%s" %bidi]
            del fnhc_dict[p]["component_codes_features_%s" %bidi]
            del fnhc_dict[p]["components_%s" %bidi]
            
    return fnhc_dict