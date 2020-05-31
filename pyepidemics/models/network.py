

import networkx as nx
import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings("ignore") 

class CompartmentNetwork:
    def __init__(self,nodes = None):
        self.graph = nx.DiGraph()
        self.static = {}
        if nodes is not None:
            self.add_nodes(nodes)

    def add_node(self,node):
        self.graph.add_node(node)

    def add_nodes(self,nodes):
        self.graph.add_nodes_from(nodes)
    
    def add_transition(self,start,end,transition):
        attributes = {"transition":transition}
        self.graph.add_edge(start,end,**attributes)

    def add_static_derivative(self,node,fn):
        self.static[node] = fn

    def get_static_derivative(self,node,y,t):

        if node in self.static:
            return self.static[node](y,t)
        else:
            return 0


    def get_in_neighbors(self,node):
        in_edges = list(self.graph.in_edges(node))
        if len(in_edges) > 0:
            return [x[0] for x in in_edges]
        else:
            return []

    def get_out_neighbors(self,node):
        out_edges = list(self.graph.out_edges(node))
        if len(out_edges) > 0:
            return [x[1] for x in out_edges]
        else:
            return []

    def get_transition(self,start,end,y,t):
        value = self.graph[start][end]["transition"]
        if callable(value):
            value = value(y,t)
        return value


    def compute_derivative(self,node,y,t):

        derivative = 0

        # Substract for out neighbors
        for neighbor in self.get_out_neighbors(node):
            derivative -= self.get_transition(node,neighbor,y,t)
        
        # Add for in neighbors
        for neighbor in self.get_in_neighbors(node):
            derivative += self.get_transition(neighbor,node,y,t)

        # Add node derivative
        derivative += self.get_static_derivative(node,y,t)

        # Safety check to avoid getting an iterable in granular models
        def iterable(obj):
            try:
                iter(obj)
            except Exception:
                return False
            else:
                return True

        if iterable(derivative):
            raise Exception(f"Derivative should not be an iterable but a float value, here found {derivative}")

        return derivative

    def compute_derivatives(self,compartments,y,t):
        return [self.compute_derivative(node,y,t) for node in compartments]


    def show(self,k = 1,layout = "spring",figsize = (15,4),separate_components = True,largest_component = True,node_size = 3000):
        assert layout in ["spring","kamada"]


        def plot_network(G):
            options = {'node_color': '#00ADD0','node_size': node_size}
            plt.figure(figsize = figsize)
            if layout == "spring":
                pos = nx.spring_layout(G,k = k)
            else:
                pos = nx.kamada_kawai_layout(G)

            nx.draw(G,with_labels = True,pos = pos,**options)
            plt.show()

        components_generator = nx.weakly_connected_component_subgraphs(self.graph)

        if largest_component:
            print("[INFO] Displaying only the largest graph component, graphs may be repeated for each category")
            graph = max(components_generator, key=len)
            plot_network(graph)

        elif separate_components:
            for graph in components_generator:
                plot_network(graph)
        else:
            plot_network(self.graph)
            
