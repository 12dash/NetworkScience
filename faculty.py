import networkx as nx
import matplotlib.pyplot as plt
import numpy

NAMES = None
FACULTY = None

class Year:

    '''
    Builds a Collaboration Network for the individual years
    '''   

    def __init__(self, year, NAME_, FACULTY_):

        global NAMES 
        global FACULTY

        NAMES = NAME_
        FACULTY = FACULTY_

        self.year = year

        self.graph_year = nx.Graph()
        self.graph_previous_years = nx.Graph() 

        self.year_info = {}
        self.previous_year_info = {}

        self.build_graph()
        self.set_information()
        self.add_properties_network()

    def build_graph(self):

        self.graph_year.add_nodes_from(NAMES)
        self.graph_previous_years.add_nodes_from(NAMES)

        for faculty in FACULTY:
            for paper in FACULTY[faculty].papers:               
                if (paper.year <= self.year) and (paper.year > 1999):
                    for author in paper.authors:
                        if (author in NAMES) and (author != FACULTY[faculty].name) and not(self.graph_previous_years.has_edge(FACULTY[faculty].name, author)) and not(self.graph_previous_years.has_edge(author, FACULTY[faculty].name)):
                            self.graph_previous_years.add_edge(FACULTY[faculty].name, author)
                            if paper.year == self.year:
                                self.graph_year.add_edge(FACULTY[faculty].name, author)

        return

    def set_information(self):

        def get_info(network, network_dic):

            def get_average_degree(network):
                degrees = [i[1] for i in (network.degree())]
                degrees = sum(degrees)
                avg_degree = degrees/(network.number_of_nodes())
                return avg_degree
            
            def get_average_clustering(network):
                return nx.average_clustering(network)          

            def get_number_edges(network):
                '''
                Returns the number of edges in the network
                '''
                return network.number_of_edges()

            def get_connected_components(network):
                connected_components = nx.connected_components(network)
                num = 0    
                connected_components_list = []
                for i in connected_components :
                    if len(i) > 1 : 
                        num += 1
                        temp = network.subgraph(list(i)).copy()       
                        connected_components_list.append(temp) 
                return num, connected_components_list

            def get_dist(network):
                average=[]
                for C in (network.subgraph(c).copy() for c in nx.connected_components(network)):
                    average.append(nx.average_shortest_path_length(C))
                sum=0
                for i in range(len(average)):
                    if average[i]!=0:
                        sum+=average[i]
                count=network_dic['number_of_connected_components']
                return sum/count

            def get_smallworld_sigma(network):
                for C in (network.subgraph(c).copy() for c in nx.connected_components(network)):
                    if len(C)>3:
                        sigma=nx.sigma(C, niter=1, nrand=1, seed=0)
                print(sigma)

            def get_most_edge_faculty(network):
                return sorted(network.degree, key=lambda x: x[1], reverse=True)

            def get_density(network):
                density=0
                for C in (network.subgraph(c).copy() for c in nx.connected_components(network)):
                    density+=nx.density(C)
                count = network_dic['number_of_connected_components']
                return density/count

            network_dic['average_degree']=get_average_degree(network)
            network_dic['average_clustering_coefficient']=get_average_clustering(network)
            network_dic['number_of_edges'] = get_number_edges(network)
            network_dic['number_of_connected_components'], network_dic['connected_components'] = get_connected_components(network)
            network_dic['avg_dist'] = get_dist(network)
            network_dic['most_edge_faculty'] = get_most_edge_faculty(network)
            #network_dic['smallworld_sigma'] = get_smallworld_sigma(network)
            network_dic['density'] = get_density(network)

        get_info(self.graph_year,self.year_info)
        get_info(self.graph_previous_years,self.previous_year_info)

        return

    def display_networkx(self):
        '''
        Displays the network_x graph
        '''
        plt.figure(figsize=(24, 12))
        nx.draw_random(self.graph_year, with_labels=True, font_weight='bold')
        plt.show()
        return

    def add_properties_network(self):

        def get_graph_properties(network):
            degrees = dict(nx.degree(network))
            betweenness_centrality = nx.betweenness_centrality(network)
            clustering = nx.clustering(network)

            nx.set_node_attributes(network, name='degree', values=degrees)
            nx.set_node_attributes(network, name='betweenness', values=betweenness_centrality)
            nx.set_node_attributes(network, name='clustering', values=clustering)

            number_to_adjust_by = 5

            adjusted_node_size = dict([(node, degree+number_to_adjust_by) for node, degree in nx.degree(network)])
            nx.set_node_attributes(network, name='adjusted_node_size', values=adjusted_node_size)

            return

        get_graph_properties(self.graph_year)
        get_graph_properties(self.graph_previous_years)

        return


class Faculty:

    def __init__(self, name):
        self.name = name

        self.graph_years = {}
        self.graph_years_all = {}

        self.generate_graph_years()

    def generate_graph_years(self):
        def build_graph(year):
            graph = nx.Graph()
            graph_all = nx.Graph() 

            for paper in FACULTY[self.name].papers:
                if paper.year == year:
                    for author in paper.authors:
                        if (author != FACULTY[self.name].name) and not(graph.has_edge(FACULTY[self.name].name, author)) and not(graph.has_edge(author, FACULTY[self.name].name)):
                            graph_all.add_edge(FACULTY[self.name].name, author)
                            if (author in NAMES):
                                graph.add_edge( FACULTY[self.name].name, author)


            self.graph_years[year] = graph 
            self.graph_years_all[year] = graph_all        

            return
        
        for i in range(2000,2021):
            build_graph(i)

        return