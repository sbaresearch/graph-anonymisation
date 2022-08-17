##############
# ATTRIBUTES #
##############

import copy
from re import X
from similarity_computation_and_generalization.similarityComputation import *
from similarity_computation_and_generalization.generalizationSupportBidirectional import * 

#same as similarity computation but returns only distance between  attributes of two nodes
def distance_computation(fnhc_u, fnhc_v, hierarchy, attribute):

	#initially distance = 0 
	distance = 0

	#attribute node u
	attribute_u = fnhc_u[attribute]

	#attribute node v
	attribute_v = fnhc_v[attribute]
	
	#if attribute is the same, skip --> distance = 0
	if  attribute_u == attribute_v:
		pass

	#if attributes are different
	else:

		#define int_u and int_v differently --> meaning they belong to different level 0 interval
		int_u = ""
		int_v = "/"

		#define starting level for the hierarchies
		level = 0

		while int_u != int_v:

			#increase distance
			distance = distance + 1

			#set ints as next level in hierarchy
			int_u = hierarchy.loc[attribute_u][level]
			int_v = hierarchy.loc[attribute_v][level]

			#update level
			level = level + 1

	return distance

#function to generalize a neighborhood
#the idea is to use maximum distance between two nodes to generalize the whole neighborhood 
# (maximum distance will always be the first common vertex for all vertices in the attribute)
def generalize_attribute(neighborhood, fnhc_dict, hierarchy, attribute):
	
	###print("\n\nCALLL FUNCTION")

	#start a current maximum distance in 0
	maximum = 0
	
	###print(len(neighborhood))

	#for every node but the target
	for i in range(len(neighborhood)-1):
		#target
		target = neighborhood[-1]
		#every other node i
		node_u = neighborhood[i]
		#distance between target and node i
		distance = distance_computation(fnhc_dict[target], fnhc_dict[node_u], hierarchy, attribute)
		###print("distance: ", distance)
		#if distance between i and target is greater than current maximum
		if distance > maximum:
			#update the maximum
			maximum = distance
			###print("maximum: ", maximum)



	#for every node in best_fitting_vertices and target
	for j in neighborhood:
		attribute_j = fnhc_dict[j][attribute]
		#update the value of attribute attribute for those vertices
		fnhc_dict[j][attribute] = hierarchy.loc[attribute_j][maximum-1]
		###print(fnhc_dict[j][attribute])

	return fnhc_dict


#########################
# PROJECTS (STRUCTURES) #
#########################

def generalize_unidirectional_connection(neighborhood, fnhc_dict, unidirectional_connection):
	
	#gen_projects list (start only with 1 node)
	target = neighborhood[-1]
	gen_projects = set(fnhc_dict[target][unidirectional_connection])

	#for every node but the target
	for i in range(len(neighborhood)-1):

		#every other node i
		node_u = neighborhood[i]
		projects_u = set(fnhc_dict[node_u][unidirectional_connection])

		gen_projects = gen_projects&projects_u
	

	#for all vertices in the neighborhood
	for j in neighborhood:
		#update projects
		fnhc_dict[j][unidirectional_connection] = list(gen_projects)

	return fnhc_dict


#####################################
# KNOWS (BIDIRECTIONAL CONNECTIONS) #
#####################################

###########################################################
# Helper (same as similarity but returning to_delete too) #
###########################################################

def sim_bidirectional_gen(v, w, source_v, source_w, complete_similarity=False):
	
	#make a copy of orginal codes so that they can be sent to original again later
	code_v = v
	code_w = w

	for path in code_v:
		path[0][2] = source_v
	
	for path in code_w:
		path[0][2] = source_w

	# ##print("\nOrginal codes: \nv: ",code_v,"\n w: ", code_w)

	#lists to stored already matched edges
	matched_v = []
	matched_w = []

	#list to store edges to delete (similarity will be the lenght of this list)
	to_delete = []

	# ##print("\nComputing similarity between codes:\n v:", code_v, " \nand w: ", code_w, "...")
	# ##print("\nStarting loop over the different substrings...")

	while ((len(code_v) > 0) & (len(code_w) > 0)):

		deleted_until_now = copy.deepcopy(to_delete)

		#select the biggest substring among the fnh codes (remember that they are sorted. Thus, take last one)
		current_v = code_v[-1]
		current_w =  code_w[-1]

		# ##print("\nLargest strings from each of the codes are: ")
		# ##print("current v", current_v)
		# ##print("current w", current_w)


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
					###print("Conflicting edges", edge_v,edge_w)

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
							
						# ##print(split1)
						# ##print(split2)
						# ##print("To delete", to_delete)
						# ##print("\v:", code_v)

						#reorder the code
						code_v = reorder_code(code_v)
						# ##print("\v:", code_v)

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
						
						# ##print(split1)
						# ##print(split2)
						# ##print("To delete", to_delete)
						# ##print("\nw:", code_w)

						#reorder code
						code_w = reorder_code(code_w)
						# ##print("\nw:", code_w)

					else:
						# ##print("Conflicting edges:", edge_v, edge_w)
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

						# ##print("current w", current_w)
						# ##print("code w:" , code_w)
						#remove current_w from code (we will enter the updated code)
						code_w.remove(current_w)

						#update the other part of the string of current w
						code_w = update_large(code_w, matched_s, non_matched_s, to_delete)
						# ##print("w", code_w)
						# ##print("matched v", matched_v)
						# ##print("matched w", matched_w)
						
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
						# ##print("v", code_v)


				#if they don't --> remove one edge in the same way as in second case a)
				else:
					edge_v, edge_w = match_all(current_v,current_w)
					# ##print("Conflicting edges", edge_v,edge_w)
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
							
						# ##print(split1)
						# ##print(split2)
						# ##print("To delete", to_delete)
						# ##print("\v:", code_v)

						#reorder the code
						reorder_code(code_v)
						# ##print("\v:", code_v)

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
						
						# ##print(split1)
						# ##print(split2)
						# ##print("To delete", to_delete)
						# ##print("\nw:", code_w)

						#reorder code
						code_w = reorder_code(code_w)
						# ##print("\nw:", code_w)

					else:
						# ##print("Conflicting edges:", edge_v, edge_w)
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

					# ##print("current w", current_w)
					# ##print("code w:" , code_w)
					#remove current_w from code (we will enter the updated code)
					code_w.remove(current_w)

					#update the other part of the string of current w
					code_w = update_large(code_w, matched_s, non_matched_s, to_delete)
					# ##print("w", code_w)
					# ##print(matched_v)
					# ##print(matched_w)
					
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
					# ##print("v", code_v)

		#THIRD CASE
		#both substrings are composed of a vertex
		elif (len(current_v) == 1) & (len(current_w) == 1):
			# ##print("Match vertices together")

			#match and remove from current code
			matched_v.append(current_v)
			matched_w.append(current_w)
			code_v.remove(current_v)
			code_w.remove(current_w)

		#raise error if not fiting in any of the cases
		else:
			raise ValueError("These two edges: %s and %s, do not fit in any of the cases." %(current_v,current_w))	

		# #print("\nAfter this round, we update everything: ")
		# #print("To delete", to_delete)
		# #print("matched v", matched_v)
		# #print("matched w", matched_w)
		# #print("code v", code_v)
		# #print("length code v", len(code_v))
		# #print("code w", code_w)
		# #print("length code w", len(code_w))

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
								##print("EDGE", edge)
								##print("CODE", code)
								code.remove(substring)
								##print("CODE", code)
								##print("SUBSTRING", substring)
								substring, split1, split2, empty = remove_and_update(substring,edge,[])
								#if further edges are removed during the update, add them to the list of deleted this round
								for candidate in empty:
									if sorted(get_letters(candidate)) != sorted(get_letters(del_edge)):	
										deleted_this_round.append(candidate)
										##print("HEEERE")
									else:
										pass
								##print(deleted_this_round)
								#SAME AS BEFORE
								if (len(split2) == 0) & (len(split1) == 0):
									code.append(substring)
								elif (len(split2) == 0) & (len(split1) >= 1):
									code.append(split1)
								elif len(split2) >=1:
									code.append(split1)
									code.append(split2)
								##print("SUBSTRING", substring)
								##print("CODE", code)
								##print("SPLIT1", split1)
								##print("SPLIT2", split2)
								##print("EMPTY", empty)
	

	#send remaining edges to to_delete (remove also connections of those nodes to main node)
	if len(code_v) == 0: 
		for c in code_w:
			for edge in c:
				#saver for node edges (can happen in second pass)
				if edge[2] == None:
					edge[2] = source_w
				to_delete.append(edge)
				if (edge[0] != 0) & (is_forward(edge) == True):
					to_delete.append([0,1, source_w, edge[3]]) #this naming happens only here, they need to be deleted later :)

	elif len(code_w) == 0:
		for c in code_v:
			for edge in c:
				#saver
				if edge[2] == None:
					edge[2] = source_w
				to_delete.append(edge)
				if (edge[0] != 0) & (is_forward(edge) == True):
					to_delete.append([0,1, source_v,edge[3]])


	# ##print("GENERALIZATION\n\nSimilarity between v and w is: ", sim_knows)
	# ##print("Edges to delete are: ", to_delete)
	# ##print("Matched codes:")
	# ##print("V: ", matched_v)
	# ##print("Matched w: ", matched_w)

	return to_delete, matched_v, matched_w
 
##################
# Generalization #
##################

def generalize_biderctional_connections(neighborhood, fnhc, people, bidi_connection):

	#print("Neighborhood before everything")
	# for n in neighborhood:
		#print(fnhc[n]["full_code_"], "\n")

	target = neighborhood[-1]
	current_match = fnhc[target]["full_code_%s" %bidi_connection]
	delete_in_neighborhood = []

	for neighbhor in neighborhood[:-1]:

		#save edges to delete and current match
		to_delete, current_match, fnhc[neighbhor]["full_code_%s" %bidi_connection] = sim_bidirectional_gen(current_match, fnhc[neighbhor]["full_code_%s" %bidi_connection], target, neighbhor, False)


		for x in to_delete:
			delete_in_neighborhood.append(x)

		#update the current match to the most recent one
		current_match = reorder_code(current_match)
		#also update the fnhc code of the neighbor by only taking what is matched (everything else deleted)
		#this code will be used for the second pass
		fnhc[neighbhor]["full_code_%s" %bidi_connection] = reorder_code(fnhc[neighbhor]["full_code_%s" %bidi_connection])

		to_delete = []


		
	# ##print("\nDELETE NEIGHBORHOOD" , delete_in_neighborhood)
	# ##print("\nCURRENT MATCH", current_match)

	#we don't need to go ove target and neither over the last code (already with the same structure as target)
	for neighbhor in neighborhood[:-2]:
		#everything else is the same as before
			to_delete, current_match, fnhc[neighbhor]["full_code_%s" %bidi_connection] = sim_bidirectional_gen(current_match, fnhc[neighbhor]["full_code_%s" %bidi_connection], target, neighbhor, False)
			
			for x in to_delete:
				delete_in_neighborhood.append(x)
			
			current_match = reorder_code(current_match)
			fnhc[neighbhor]["full_code_%s" %bidi_connection] = reorder_code(fnhc[neighbhor]["full_code_%s" %bidi_connection])


	#print("\nNeighborhood codes after pure anonymization (without actually removing edges yet):")
	# for n in neighborhood[:-1]:
		#print(fnhc[n]["full_code"], "\n")
	#print(current_match)

	#print("\nIn order to actually perform that 'pure' anonymization, we needed to delete the following edges", delete_in_neighborhood)
	# ##print(fnhc)


	#print("\nFor that purpose the 'knows' connections of the whole dataset are updated. When doing so, the k-property may be broken 'additional edges deleted'.")
	#do a copy of people and remove anonymized
	#this way we have a list of non_anonymized vertices
	#DO IT ONLY IF LENGHT PEOPLE > 0 (i.e. not in the last anonymization step)
	if len(people) > 0:
		# #print("WHOOOOHWOWHOWHWO")
		non_anonymized = copy.deepcopy(people)
		for n in neighborhood[:-1]:
			non_anonymized.remove(n)

		codes_to_recompute = []

		for d in delete_in_neighborhood:

			#identify the deleted edges also in other full_codes
			for p in non_anonymized:
				if p in codes_to_recompute:
					pass
				else:
					#if some person is within the deleted edges, the node of this person needs to be updated
					if d[2] == p:
						if d[3] in fnhc[p][bidi_connection]:
							codes_to_recompute.append(p)
							pass
					elif d[3] == p:
						if d[2] in fnhc[p][bidi_connection]:
							codes_to_recompute.append(p)
							pass
					#or if the deleted edge is in some form in my code (less likely)
					for path in fnhc[p]["full_code_%s" %bidi_connection]:
						for edge in path:
							if ((edge[2] == d[2]) & (edge[3] == d[3])) | ((edge[2] == d[3]) & (edge[3] == d[2])):
								codes_to_recompute.append(p)
								pass
					else:
						pass

			# update knows for every deleted edge & update degree
			if d[3] in fnhc[d[2]][bidi_connection]:
				fnhc[d[2]][bidi_connection].remove(d[3])
				fnhc[d[2]]["degree"] = fnhc[d[2]]["degree"] - 1
				fnhc[d[3]][bidi_connection].remove(d[2])
				fnhc[d[3]]["degree"] = fnhc[d[3]]["degree"] - 1

		#print("COOOOOOOODEEESS",codes_to_recompute)

		for rec in codes_to_recompute:
			#print("\nWHO: ", rec)
			#print("Full social code before", fnhc[rec]["full_code"])
			#recompute codes
			fnhc = compute_fnhc_bidirectional_generalization(fnhc, rec, [bidi_connection])
			#print("full social code after", fnhc[rec]["full_code"])
		
	#if it is the last step, only update the knows (nothing else needed)
	else:
		# #print("HERREEEe")
		# #print("TO DELETE", delete_in_neighborhood)
		for d in delete_in_neighborhood:
			# to delete:
			#update knows for every deleted edge & update degree
			if d[3] in fnhc[d[2]][bidi_connection]:
				fnhc[d[2]]["knows"].remove(d[3])
				fnhc[d[2]]["degree"] = fnhc[d[2]]["degree"] - 1
				fnhc[d[3]][bidi_connection].remove(d[2])
				fnhc[d[3]]["degree"] = fnhc[d[3]]["degree"] - 1

	# #print("Show that:")
	# for n in neighborhood:
	# 	#print("Friedns of ", n,"are", fnhc[n]["knows"], "\n")
	
	#print("Appart from that, all the affected codes from non-anonymized nodes are recomputed")

	return fnhc