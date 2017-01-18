import networkx as nx
import scipy.io as sc
import matplotlib.pyplot as plt

A = nx.read_edgelist('test.edges')
nx.draw(A)
plt.draw()
#plt.show()

firstNode = nx.nodes(A)[0]
print firstNode
dfs_list = list(nx.dfs_preorder_nodes(A, firstNode))

for node in dfs_list:
	print 'node:', node

