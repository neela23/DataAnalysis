import networkx as nx
import scipy.io as sc
from random import uniform
from random import choice
from collections import OrderedDict
import random
import heapq
import community


class Epidemics:

	def __init__(self,graph,infected_nodes, contact_rate,recovery_rate, r_to_s, budget, t, max_iterations):
		self.graph = graph
		self.infected_nodes = infected_nodes
		self.contact_rate = contact_rate
		self.recovery_rate = recovery_rate
		self.r_to_s = r_to_s
		self.budget = budget
		self.t = t
		self.max_iterations = max_iterations
		self.susceptible = []	
		self.immunized = OrderedDict() 
		self.centrality = dict() 
		self.communities = dict()
		self.infectedCommunities = []
		self.totalCommunities = []
		self.isCentralityUsed = False

	def calculateBetweenness(self,count):
		self.centrality = nx.betweenness_centrality(self.graph, k= count, normalized=True, weight=None, endpoints=False, seed=None)
	def calculateDegree(self):
		self.centrality = nx.degree_centrality(self.graph)
	def calculateCloseness(self):
		self.centrality = nx.closeness_centrality(self.graph)
	def calculateEigenvector(self, count):
		self.centrality = nx.eigenvector_centrality(self.graph)

	def computeCommunities(self):
		print("Computing communities....")
		self.communities = community.best_partition(self.graph)
		self.totalCommunities = set(self.communities.values())
		print ("Total Communities:" , len(self.totalCommunities))

	def immunize_communities(self, index):
		immunize_target = []
		now_infected = set([value for key,value in self.communities.items() if key in self.infected_nodes])
		self.infectedCommunities = list(now_infected)
		if(len(now_infected) == len(self.totalCommunities)):
			print "All communities infected...."
			self.isCentralityUsed = 1
		for node in self.infected_nodes:
			neighbors = self.graph.neighbors(node)
			if(len([x for x in neighbors if self.communities[x] not in self.infectedCommunities])):
				immunize_target.append(node)
			
			#if(len ([x for x in neighbors if self.communities[x] not in self.infectedCommunities])):
			'''flag = 0
			for neigh in neighbors:
				if(self.communities[neigh] not in self.infectedCommunities):
					flag =1
					break
			if(flag ==1):	
				immunize_target.append(node)'''
		immunized_nodes = [] 
		for node in immunize_target:
			if self.budget> 0: # Atleast one immunization left per iteration
				self.budget-=1
				randomProb = uniform(0,1)
	                        if self.recovery_rate > randomProb:        	  
					 immunized_nodes.append(node)
                          		 self.infected_nodes.remove(node)
                self.immunized[index] = immunized_nodes
		print ("Shots left:", self.budget)

	def susceptible_nodes(self):
		self.susceptible = []
		for node in self.infected_nodes:
			self.susceptible.extend(self.graph.neighbors(node))
		self.susceptible = set(self.susceptible) # Only unique elements
		self.susceptible = [x for x in self.susceptible if x not in  self.infected_nodes] # Remove elements from infected
		self.susceptible = [x for x in self.susceptible if x not in self.immunized.values()] # immunized are not susceptible
	
	def spread_infection(self):
		for node in self.susceptible:
			randomProb = uniform(0,1)
			#print "Random Prob:", randomProb
			if self.contact_rate > randomProb:
				self.infected_nodes.add(node)
	
	def printNodes(self):
		print "Susceptible Nodes:",len(self.susceptible)
		print "Infected nodes:", len(self.infected_nodes)
		length = 0
		for key in self.immunized:
			length+=len(self.immunized[key])
		print "Immunized nodes:", length

	def kill_immunization_effect(self, count):
		lost_immunization = []	
		for node in self.immunized[count]:
			randomProb = uniform(0,1)
                        if(self.r_to_s < randomProb):
                               	 lost_immunization.append(node)
		print("Immunizations lost:", len(lost_immunization))
		new_values = [x for x in self.immunized[count] if x not in lost_immunization]
		self.immunized[count] = new_values
		
		'''for index in self.immunized.keys(): #iterating through keys
			if(index<=count):
				lost_immunization = []
				for node in self.immunized[index]:
					randomProb = uniform(0,1)
					if(self.r_to_s > randomProb):
						lost_immunization.append(node)
				print "Lost Immunization", len(lost_immunization)
				new_values =[x for x in self.immunized[index] if x not in lost_immunization]	
				self.immunized[index]= new_values
			else:
				break
		'''
	
	def immunize_nodes_random(self, budget_per_iteration,index):
		infected_list = list(self.infected_nodes)
		immunized_nodes = []
		for k in range(budget_per_iteration): # Assuming full probability of recovery . Needs change
                        randomProb = uniform(0,1)
                        if k < len(infected_list) and self.recovery_rate > randomProb:
                                immunized_nodes.append(infected_list[k])
                                self.infected_nodes.remove(infected_list[k])
                self.immunized[index] = immunized_nodes
	
	def immunize_nodes_random_degree(self, budget_per_iteration, index):
		infected_list = list(self.infected_nodes)
                immunized_nodes = []
		for i in range(budget_per_iteration):
			randomNode1 = choice(infected_list)
			randomNode2 = choice(infected_list)
			immunized_nodes.append(randomNode1 if self.graph.degree(randomNode1) > self.graph.degree(randomNode2) else randomNode2)
		
                self.infected_nodes = set([x for x in self.infected_nodes if x not in immunized_nodes])
                self.immunized[index] = immunized_nodes
		
					
	def immunize_nodes_centrality(self, budget_per_iteration, index):
		immunized_nodes = []
		# 1. Create a dictionary of elements that are infected with centrality
		infected_centrality = dict()
		for node in self.infected_nodes:
			infected_centrality[node]=self.centrality[node]
	        #2. Pick elements with largest centrality
		target = heapq.nlargest(budget_per_iteration, infected_centrality, key = infected_centrality.get)
		#3.  Update infected and immunized list
		self.infected_nodes = set([x for x in self.infected_nodes if  x not in target])
                self.immunized[index] = target

	def iterate_spread(self):
		
		#self.calculateBetweenness(40) # Other centrality measured can be used to compare performance.
		#self.calculateDegree()
		#self.calculateCloseness()

		self.calculateEigenvector(10) # Needed only if disease spreads over all communities. Computing beforehand to avoid unnecessary delay in the middle
		self.computeCommunities()
		leftBudget = self.budget
		for count in range(self.max_iterations):
			print("Step ", count+1)
			self.susceptible_nodes()
			self.spread_infection()
			self.printNodes()
			if(self.isCentralityUsed):
				self.immunize_nodes_centrality(leftBudget, count)
			else:
				self.immunize_communities(count)
				leftBudget = self.budget/(self.max_iterations-count)
			if(count - self.t > 0):
				self.kill_immunization_effect(count-self.t)
			self.printNodes()
			#self.immunize_nodes_betweenness(self.budget/self.max_iterations, count)
		print "Total Infected:", len(self.infected_nodes)


#~~~~~~~~~~~~ Input Graph

A = nx.read_edgelist('fb-uf.edges') # Name of the .edges file
print('Finished Reading graph')

#~~~~~~~~~ Parameters 

contact_rate = 0.01 
recovery_rate = 0.6
r_to_s = 0.7 # Recovered to Susceptible rate
budget = 3000
t = 40 # Life of immunization
max_iterations = 400
no_initial_infected = 100

#~~~~~~~
initial_infected = []

for count in range(no_initial_infected):
	initial_infected.append(choice(A.nodes()))
initial_infected = set(initial_infected)

print("Total number initially infected:", len(initial_infected))

obj = Epidemics(A, initial_infected, contact_rate, recovery_rate, r_to_s, budget, t, max_iterations)
obj.iterate_spread()


