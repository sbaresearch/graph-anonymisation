##################################
# INDIVIDUAL SIMILARITY MEASURES #
##################################

import copy

############################
# SIMILARITY OF ATTRIBUTES #
############################

#takes fnhc of two vectors u and v and computes *attribute* similarity between them
def sim_attributes(fnhc_u, fnhc_v, hierarchy, attribute):

    #number of levels
    n_levels = len(hierarchy.columns)

    #initially distance = 0 
    distance = 0

    #attribute node u
    attribute_u = fnhc_u[attribute]

    #attribute node v
    attribute_v = fnhc_v[attribute]
    
    #if attribute is the same, 0 distance --> sim_attribute = 0
    if  attribute_u == attribute_v:
        sim_attribute = distance
        #print("Same attribute!!: ", attribute_u, "equals ", attribute_v)
    
    #if attributes are different
    else:

        #print("attribute_u: ", attribute_u)
        #print("attribute_v: ", attribute_v)

        #define int_u and int_v differently --> meaning they belong to different level 0 interval
        int_u = ""
        int_v = "/"

        #define starting level for the hierarchies
        level = 0

        while int_u != int_v:

            #print("current level: ", level)

            #increase distance
            distance = distance + 1

            #set ints as next level in hierarchy
            int_u = hierarchy.loc[attribute_u][level]
            int_v = hierarchy.loc[attribute_v][level]

            #print("int_u: ", int_u)
            #print("int_v: " , int_v)
            

            #update level
            level = level + 1
        
        sim_attribute = distance / n_levels

        #print("distance: ", distance)
        #print("level", level)
        #print("similarity: ", sim_attribute)

    return sim_attribute


#######################################
# SIMILARITY OF PROJECTS (STRUCTURES) #
#######################################

#takes fnhc of two vectors u and v and computes project similarity between them
def sim_unidirectional_connections(fnhc_u, fnhc_v, unidirectional_connection):

    uni_u = set(fnhc_u[unidirectional_connection])
    uni_v = set(fnhc_v[unidirectional_connection])

    #oppossite of intersection --> set_differences
    #number of projects to be deleted so two nodes have the same projects in common (as described in the paper)
    sim_project = len(uni_u^uni_v)
    
    return sim_project


#######################################
# SIMILARITY OF PROJECTS (STRUCTURES) #
#######################################

####################
# Helper functions #
####################

#checks wheter two substrings match or not, if not --> first conflicting edges returned
def match_all(substring_v, substring_w):
    #for every edge in the smallest substring
    for edge_index in range(min(len(substring_v),len(substring_w))):
        #if edges do not match, return false and continue
        if substring_v[edge_index][:2] != substring_w[edge_index][:2]:
            return substring_v[edge_index], substring_w[edge_index] #function stops here
        #else, continue and return True in the end
        else:
            continue
    return True

#function to determine whether and edge is forward or backward
def is_forward(edge):
    if edge[0] > edge[1]:
        return False
    if edge[0] < edge[1]:
        return True

#takes to edges and returns whether edge_v < edge_w (linear order in the paper)
def linear_order(edge_v, edge_w):
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

#update a path given an edge to delete
#return either the updated path 
#or the splited path 
#return also updated "to_delete" list
def update_path(path, del_edge, to_delete):

    #identify the index of the edge to delete in the path 
    del_edge_index = path.index(del_edge)

    #As a simplification, always remove backward edges that are inmediately after the current disconnected node
    while is_forward(path[del_edge_index+1]) == False:
        to_delete.append(path[del_edge_index+1])
        # print("delete backward edge inmediately after deleted edge: ", path[del_edge_index+1])
        path.remove(path[del_edge_index+1])

        #stop prior to index error
        if len(path) == del_edge_index+1:
            path.remove(del_edge)
            to_delete.append(del_edge)
            return to_delete, path, []

    #FIRST CONDITION (ONLY  UPDATE)
    # if delete edge is the last edge in a subpath, then we delete it and just update
    # the following forward and backward edges accordignly

    # if the next forward edge after the deleted doesn't start from the last discovered node
    # then the edge to delete is the last edge in his subpath
    # no need to split the string in this case --> ACTUALLY THERE IS A STANDALONE NODE THAT NEEDS TO BE SPLIT
    if del_edge[1] != path[del_edge_index+1][0]:
        #print("No need to split the string")
        #print("Next forward: ", path[del_edge_index+1])

        #for every edge starting from the next edge after the deleted edge
        for edge in path[del_edge_index+1:]:
            #print(edge)
            #for every node (numerically encoded) in the edge that is currently being analyzed
            for node in edge[:2]:
                #if the number is greater than the last node of the edge to be deleted, then just substract 1
                if node > del_edge[1]:
                    edge[edge.index(node)] = node - 1
                #else, it is a node that was already in the string, so leave it like that

        #remove edge to delete from the path
        path.remove(del_edge)
        to_delete.append(del_edge)

        #STANDALONE NODE (SHOULD WORK)
        split2 = [[0,1,None,del_edge[3]]]
        split1 = path.copy()


    # SECOND CONDITION (SPLIT AND UPDATE)
    # it is not the last node of a subpath, thus we need to split the string
    # split only the subpath starting from that node and update everything else
    # that means taking into account both forward and backward edges of that subpath
    
    #if the next forward edge after the edge to delete continues from the discovered node in the to_delete
    elif del_edge[1] == path[del_edge_index+1][0]:
        #print("Next forward: " ,path[del_edge_index+1])

        #first part of the path stays the same (until the deleted edge)
        split1 = path[:del_edge_index]
        #everything else needs to be checked
        split2 = []
        #append edge to to_delete
        to_delete.append(del_edge)

        #variable used later 
        all_there = False

        #for every edge in the other side (i.e. those edges that need to be checked)
        for edge in path[del_edge_index+1:]:
            #print("\n current edge", edge)

            #if it is a forward edge
            if is_forward(edge)==True:
                #if we are already in the point in which all edges need to go to split1 
                # (i.e. whole subpath has been explored already)
                if all_there == True:

                    #get previous forward
                    for prev in split1[::-1]:
                        if is_forward(prev):
                            prev_forward = prev[1]
                            break

                    #if the edge starts with 1 or from any other discovered edge in split 1
                    if (edge[0]==1) | (edge[0] in [i[1] for i in split1]):
                        #edge[0] stays the same (logical) and edge[1] takes the next number available from split1
                        edge = [edge[0], prev_forward+1, edge[2], edge[3]]
                    #if none of those conditions are met, 
                    else:
                        #then the next edge follows the previous one for sure
                        edge = [prev_forward, prev_forward+1, edge[2], edge[3]]
                    #print("Append forward in all there", edge)
                    #append the edge to split 1
                    split1.append(edge)
                #if all_there is not Ture yet, and the edge to be added starts from a number
                #greater or equal than the last node of the deleted edge
                elif edge[0] >= del_edge[1]:
                    max_for_split2 = edge[1]
                    # reset for numbering so that we start from the last node of the deleted edge
                    edge = [edge[0]-(del_edge[1]-1), edge[1]-(del_edge[1]-1), edge[2], edge[3]]
                    #append to split2
                    split2.append(edge)
                # once you found a forward edge that should go to the other side,
                # every other forward should go there too, thus all_there == True
                # the rest is the same as in above
                elif edge[0] < del_edge[1]:

                    #get previous forward
                    for prev in split1[::-1]:
                        if is_forward(prev):
                            prev_forward = prev[1]
                            break

                    edge = [edge[0], prev_forward+1, edge[2], edge[3]]
                    split1.append(edge)
                    all_there = True
                
            #if you find a backward edge, there are 3 cases:
            #from in to in (i.e. from split2 to split 2) --> update accordingly
            #from out to out (i.e. from split1 to split1) --> update accordingly
            #other --> any other case --> then delete edge
            elif is_forward(edge) == False:
                #from in to in
                if (edge[1] >= del_edge[1]) & (edge[0]-(del_edge[1]-1) in [i[1] for i in split2]):
                    #print("in to in ", edge)
                    edge = [edge[0]-(del_edge[1]-1), edge[1]-(del_edge[1]-1), edge[2], edge[3]]
                    split2.append(edge)
                #from out to out
                elif (edge[0]-(del_edge[1]-1) not in [i[1] for i in split2]) & ((edge[1] < del_edge[1]) | (edge[1] > max_for_split2)):
                    
                    #for every edge (in reverse direction of split1)
                    for i in split1[::-1]:
                        #find  the last forward split
                        if is_forward(i) == True:
                            #store it
                            max_for_split1 = i[1]
                            break
                        
                    #print("out to out", edge)
                    #if the target node is in split 1
                    if edge[1] in [a[1] for a in split1]:
                        #from maximum forward (it is right for sure), to original
                        edge = [max_for_split1, edge[1], edge[2], edge[3]]
                    else:
                        #if not from max forward also, but to original minus difference
                        difference = edge[1] - edge[0]
                        edge = [max_for_split1, max_for_split1+difference, edge[2], edge[3]]
                    #print("append backward split1", edge)
                    split1.append(edge)
                else:	
                    #print("delete edge", edge)
                    to_delete.append(edge)
        
        #add [0,1,None,"A"] 'edge' to split 2

        if len(split2) > 0:
            split2.insert(0, [0,1,None,split2[0][2]])

        #clean path
        path.clear()


    return to_delete, split1, split2

# performs update when unmatched edges (i.e. remove edge and update accordingly)
def remove_and_update(current_path, edge, to_delete):

    #if it is a backward edge --> also just delete from the current substring
    if is_forward(edge) == False:
        # print("Backward")
        current_path.remove(edge)
        to_delete.append(edge)
        #needed
        split1 = []
        split2 = []


    #if it is a forward edge
    if is_forward(edge) == True:
        #if it is the last edge of the component --> just delete edge from current substring
        if current_path.index(edge) == (len(current_path)-1):
            # print("last element")
            # print(current_path, to_delete)
            current_path.remove(edge)
            to_delete.append(edge)
            # print(current_path, "to delete", to_delete)

            #needed
            split1 = []
            split2 = []

        # if it is forward but not the last one
        elif current_path.index(edge) != (len(current_path)-1):
            # print("forward but not last")

            #update current path (substring)
            #this function deletes the edge that has to be deleted, updates the code accordingly
            #and splits if necessary
            to_delete, split1, split2 = update_path(current_path, edge, to_delete)

        else:
            raise ValueError("Something failed")

    #return all of this and then use some logic later to determine how to update
    return current_path, split1, split2, to_delete

def reorder_code(code):
    
    # print("Code: ", code)

    #variable to store the new code
    new_code = []

    #variable for the features
    features_code = []

    #used later
    count = 0

    #extract features
    for path in code:
        # print("Current path: ", path)
        
        #id_path --> avoids uniqueness
        id_path = count
        count = count +1

        #n_edges
        n_edges = len(path)
        # print("Number of edges ", n_edges)

        #n_vertices
        if is_forward(path[-1]) == True:
            n_vertices = path[-1][1]
        else:
            n_vertices = path[-1][0]
        
        # print("Number of vertices: ", n_vertices)

        #earliest backward
        for edge in path:
            #if it is backward edge
            if is_forward(edge) == False:
                first_backward = path.index(edge)
                break
            else:
                #this helps to avoid exactly the same encoding later
                first_backward = 1000000

        # print("First backward: ", first_backward)

        features_code.append([n_vertices, n_edges, first_backward, id_path])

    sorted_list_of_features = sorted(features_code)
    # print("sorted list of features", sorted_list_of_features)


    for i in sorted_list_of_features:
        index = features_code.index(i)
        #if the index is the same as before, then increase by 1 
        #(it means that two paths have same structure exactly)

        new_code.append(code[index])
        # print(index)
        # print(code[index])
        
        #just in case some paths have same features exactly
        #we store this variable
        prev_index = index 


    # print(new_code)

    return new_code

def update_large(code, matched, non_matched, to_delete):
    
    #store list of nodes in matched
    if is_forward(matched[-1]) == True:
        nodes_matched = [*range(matched[-1][1]+1)]
    else:
        nodes_matched = [*range(matched[-1][0]+1)]

    # print("Matched: ", matched)
    # print("Nodes_matched: ", nodes_matched)
    # print("Non_matched: ", non_matched)

    new_paths = {}
    count = 0

    # loop over the unmatched edges
    for edge in non_matched:
        #if backward
        if is_forward(edge) == False:
            #if pointing to nodes in nodes_matched
            if (edge[1] in nodes_matched) == True:
                #delete
                to_delete.append(edge)
                
            #else
            #update accordignly (it points to his own path for sure)
            else:
                difference = edge[1] - edge[0]
                #find last_forward edge in path 
                for u in new_paths[count][::-1]:
                    if is_forward(u) == True:
                        last_forward_edge = u[1]
                        break
                edge = [last_forward_edge, last_forward_edge+difference, edge[2], edge[3]]
                new_paths[count].append(edge)
        #if forward 
        elif is_forward(edge) == True:
            #if starting from nodes in nodes_matched --> start a new path (and delete connection to matched)
            if (edge[0] in nodes_matched) == True:
                #delete connection to matched
                to_delete.append(edge)
                #start new node 0
                new_edge = [0, 1, None, edge[3]]
                #count for new path in dict
                count = count +1
                #reference edge for the updates
                starting_edge_path = edge[1]-1
                #save new node 0
                new_paths[count] = [new_edge]

            #else continue in the previous path
            else:
                edge = [edge[0]-starting_edge_path, edge[1]-starting_edge_path, edge[2],edge[3]]
                new_paths[count].append(edge) 

    #update code accordignly
    for p in new_paths:
        code.append(new_paths[p])
    
    code = reorder_code(code)

    # print("New paths", new_paths)
    # print("Updated code", code)

    return code

def get_letters(edge):
    
    letters = []

    for i in edge[2:]:
        letters.append(i)

    return letters

##########################
# Similarity computation #
##########################

def sim_bidirectional_connections(v, w, complete_similarity=False):
    
    #make a copy of orginal codes so that they can be sent to original again later
    code_v = v
    code_w = w

    # print("\nOrginal codes: \nv: ",code_v,"\n w: ", code_w)


    #lists to stored already matched edges
    matched_v = []
    matched_w = []

    #list to store edges to delete (similarity will be the lenght of this list)
    to_delete = []

    # print("\nComputing similarity between codes:\n v:", code_v, " \nand w: ", code_w, "...")
    # print("\nStarting loop over the different substrings...")

    while ((len(code_v) > 0) & (len(code_w) > 0)):

        deleted_until_now = copy.deepcopy(to_delete)

        #select the biggest substring among the fnh codes (remember that they are sorted. Thus, take last one)
        current_v = code_v[-1]
        current_w =  code_w[-1]

        # print("\nLargest strings from each of the codes are: ")
        # print("current v", current_v)
        # print("current w", current_w)


        ##############
        # BOTH EDGES #
        ##############

        #if both substrings are composed of vertices and edges  (i.e. they are not single vertices)
        if (len(current_v) > 1) & (len(current_w) > 1):

            #BOTH SAME SIZE
            if len(current_v) == len(current_w):
                # THE FIRST CASE
                #if all their edges match in structure
                if match_all(current_v,current_w) == True:
                    #append to matched substrings
                    matched_v.append(current_v)
                    matched_w.append(current_w)
                    #delete this substrings from all substrings
                    code_v.remove(current_v)
                    code_w.remove(current_w)
                    #no need to sort this time, since we just deleted whole substrings

                    
                # THE SECOND CASE a)
                #if there exist two edges that don't match
                else:
                    #store conflicting edges
                    edge_v, edge_w = match_all(current_v,current_w)
                    #print("Conflicting edges", edge_v,edge_w)

                    #if edge_v < edge_w --> remove edge_V and update the substrings accordingly
                    if linear_order(edge_v,edge_w):
                        code_v.remove(current_v)
                        current_v, split1, split2, to_delete = remove_and_update(current_v,edge_v,to_delete)
                        if (len(split2) == 0) & (len(split1) == 0):
                            code_v.append(current_v)
                        elif (len(split2) == 0) & (len(split1) >= 1):
                            code_v.append(split1)
                        elif len(split2) >=1:
                            code_v.append(split1)
                            code_v.append(split2)
                            
                        # print(split1)
                        # print(split2)
                        # print("To delete", to_delete)
                        # print("\v:", code_v)

                        #reorder the code
                        code_v = reorder_code(code_v)
                        # print("\v:", code_v)

                    #if edge_w, edge_v, remove edge w and update substrings accordingly
                    elif linear_order(edge_w,edge_v):
                        code_w.remove(current_w)
                        current_w, split1, split2, to_delete = remove_and_update(current_w,edge_w,to_delete)
                        if (len(split2) == 0) & (len(split1) == 0):
                            code_w.append(current_w)
                        elif (len(split2) == 0) & (len(split1) >= 1):
                            code_w.append(split1)
                        elif len(split2) >=1:
                            code_w.append(split1)
                            code_w.append(split2)
                        
                        # print(split1)
                        # print(split2)
                        # print("To delete", to_delete)
                        # print("\nw:", code_w)

                        #reorder code
                        code_w = reorder_code(code_w)
                        # print("\nw:", code_w)

                    else:
                        # print("Conflicting edges:", edge_v, edge_w)
                        raise ValueError("Conflicting edges match. Therefore they should not conflict.")

            
            #THE SECOND CASE b)
            ##one substring is larger than the other one
            elif len(current_v) != len(current_w):

                #try to match all edges from small substring
                #perform matching 
            
                #if they do --> split larger substring and append the rest to "matched"
                if match_all(current_v,current_w)==True:
                    if len(current_v) < len(current_w):
                        matched_v.append(current_v)
                        code_v.remove(current_v)
                        matched_w.append(current_w[:len(current_v)])

                        #separate the splits to enter the function
                        matched_s = current_w[:len(current_v)]
                        non_matched_s = current_w[len(current_v):]

                        # print("current w", current_w)
                        # print("code w:" , code_w)
                        #remove current_w from code (we will enter the updated code)
                        code_w.remove(current_w)

                        #update the other part of the string of current w
                        code_w = update_large(code_w, matched_s, non_matched_s, to_delete)
                        # print("w", code_w)
                        # print("matched v", matched_v)
                        # print("matched w", matched_w)
                        
                    else:
                        matched_w.append(current_w)
                        code_w.remove(current_w)
                        matched_v.append(current_v[:len(current_w)])
                        #update the other part of the string of current v

                        #separate the splits to enter the function
                        matched_s = current_v[:len(current_w)]
                        non_matched_s = current_v[len(current_w):]

                        #remove from code_v the current v
                        code_v.remove(current_v)

                        #update the other part of the string of current v
                        code_v = update_large(code_v, matched_s, non_matched_s, to_delete)
                        # print("v", code_v)


                #if they don't --> remove one edge in the same way as in second case a)
                else:
                    edge_v, edge_w = match_all(current_v,current_w)
                    # print("Conflicting edges", edge_v,edge_w)
                    #if edge_v < edge_w --> remove edge_V and update the substrings accordingly
                    if linear_order(edge_v,edge_w):
                        code_v.remove(current_v)
                        current_v, split1, split2, to_delete = remove_and_update(current_v,edge_v,to_delete)
                        if (len(split2) == 0) & (len(split1) == 0):
                            code_v.append(current_v)
                        elif (len(split2) == 0) & (len(split1) >= 1):
                            code_v.append(split1)
                        elif len(split2) >=1:
                            code_v.append(split1)
                            code_v.append(split2)
                            
                        # print(split1)
                        # print(split2)
                        # print("To delete", to_delete)
                        # print("\v:", code_v)

                        #reorder the code
                        reorder_code(code_v)
                        # print("\v:", code_v)

                    #if edge_w, edge_v, remove edge w and update substrings accordingly
                    elif linear_order(edge_w,edge_v):
                        code_w.remove(current_w)
                        current_w, split1, split2, to_delete = remove_and_update(current_w,edge_w,to_delete)
                        if (len(split2) == 0) & (len(split1) == 0):
                            code_w.append(current_w)
                        elif (len(split2) == 0) & (len(split1) >= 1):
                            code_w.append(split1)
                        elif len(split2) >=1:
                            code_w.append(split1)
                            code_w.append(split2)
                        
                        # print(split1)
                        # print(split2)
                        # print("To delete", to_delete)
                        # print("\nw:", code_w)

                        #reorder code
                        code_w = reorder_code(code_w)
                        # print("\nw:", code_w)

                    else:
                        # print("Conflicting edges:", edge_v, edge_w)
                        raise ValueError("Conflicting edges match. Therefore they should not conflict.")


        #if one edge, one vertex

        #one vertex v and edges in w
        elif ((len(current_v) == 1) & (len(current_w) > 1)) | ((len(current_w) == 1) & (len(current_v) > 1)):

            #The way I have the data, I can apply same as before
                    #if they do --> split larger substring and append the rest to "matched"
            if match_all(current_v,current_w)==True:
                if len(current_v) < len(current_w):
                    matched_v.append(current_v)
                    code_v.remove(current_v)
                    matched_w.append(current_w[:len(current_v)])

                    #separate the splits to enter the function
                    matched_s = current_w[:len(current_v)]
                    non_matched_s = current_w[len(current_v):]

                    # print("current w", current_w)
                    # print("code w:" , code_w)
                    #remove current_w from code (we will enter the updated code)
                    code_w.remove(current_w)

                    #update the other part of the string of current w
                    code_w = update_large(code_w, matched_s, non_matched_s, to_delete)
                    # print("w", code_w)
                    # print(matched_v)
                    # print(matched_w)
                    
                else:
                    matched_w.append(current_w)
                    code_w.remove(current_w)
                    matched_v.append(current_v[:len(current_w)])
                    #update the other part of the string of current v

                    #separate the splits to enter the function
                    matched_s = current_v[:len(current_w)]
                    non_matched_s = current_v[len(current_w):]

                    #remove from code_v the current v
                    code_v.remove(current_v)

                    #update the other part of the string of current v
                    code_v = update_large(code_v, matched_s, non_matched_s, to_delete)
                    # print("v", code_v)

        #THIRD CASE
        #both substrings are composed of a vertex
        elif (len(current_v) == 1) & (len(current_w) == 1):
            # print("Match vertices together")

            #match and remove from current code
            matched_v.append(current_v)
            matched_w.append(current_w)
            code_v.remove(current_v)
            code_w.remove(current_w)

        #raise error if not fiting in any of the cases
        else:
            raise ValueError("These two edges: %s and %s, do not fit in any of the cases." %(current_v,current_w))	

        # print("\nAfter this round, we update everything: ")
        # print("To delete", to_delete)
        # print("matched v", matched_v)
        # print("matched w", matched_w)
        # print("code v", code_v)
        # print("length code v", len(code_v))
        # print("code w", code_w)
        # print("length code w", len(code_w))

        if complete_similarity == True:
            #IF IT AFFECTS THE OTHER NODE, ALSO UPDATE IT
            first_set = set(map(tuple, to_delete))
            second_set = set(map(tuple, deleted_until_now))
            deleted_this_round = list(first_set.symmetric_difference(second_set))
            for del_edge in deleted_this_round:
                #set proper type if needed
                if type(del_edge) != type([]):
                    del_edge = list(del_edge)
                else:
                    pass
                #for every code in the graph
                for code in [code_v, code_w]:
                    #for every substring in each code
                    for substring in code:
                        #for every edge in those substrings
                        for edge in substring:
                            #if the deleted edge is in that code, remove it from the code and update accordingly
                            if (edge[2] == del_edge[2]) & (edge[3] == del_edge[3]):
                                # print("EDGE", edge)
                                # print("CODE", code)
                                code.remove(substring)
                                # print("CODE", code)
                                # print("SUBSTRING", substring)
                                substring, split1, split2, empty = remove_and_update(substring,edge,[])
                                #if further edges are removed during the update, add them to the list of deleted this round
                                for candidate in empty:
                                    if sorted(get_letters(candidate)) != sorted(get_letters(del_edge)):	
                                        deleted_this_round.append(candidate)
                                        # print("HEEERE")
                                    else:
                                        pass
                                # print(deleted_this_round)
                                #SAME AS BEFORE
                                if (len(split2) == 0) & (len(split1) == 0):
                                    code.append(substring)
                                elif (len(split2) == 0) & (len(split1) >= 1):
                                    code.append(split1)
                                elif len(split2) >=1:
                                    code.append(split1)
                                    code.append(split2)
                                # print("SUBSTRING", substring)
                                # print("CODE", code)
                                # print("SPLIT1", split1)
                                # print("SPLIT2", split2)
                                # print("EMPTY", empty)

    #send remaining edges to to_delete (remove also connections of those nodes to main node)
    if len(code_v) == 0: 
        for c in code_w:
            for edge in c:
                to_delete.append(edge)
                if (edge[0] != 0) & (is_forward(edge) == True):
                    to_delete.append([0,1,None,edge[1]])

    elif len(code_w) == 0:
        for c in code_v:
            for edge in c:
                to_delete.append(edge)
                if (edge[0] != 0) & (is_forward(edge) == True):
                    to_delete.append([0,1,None,edge[3]])


    #similarity is the number of edges to be deleted so that both neighborhoods are isomorphic to one another
    sim_knows = len(to_delete)

    # print("\n\nSimilarity between v and w is: ", sim_knows)
    # print("Edges to delete are: ", to_delete)
    # print("Matched codes:")
    # print("V: ", matched_v)
    # print("W: ", matched_w)

    return sim_knows
    
################################################################################################################################################
################################################################################################################################################
################################################################################################################################################


####################
# TOTAL SIMILARITY #
####################

def similarityComputation(weights, similarities):

    similarity = 0
    count = 0

    for w in weights:

        similarity = similarity + float(w)*similarities[count]
        count = count + 1

    return similarity