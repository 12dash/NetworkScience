from preprocess import fetch_faculty
import matplotlib.pyplot as plt
import networkx as nx
from bokeh.io import  output_notebook, show, save
from bokeh.models import Range1d, Circle, ColumnDataSource, MultiLine, EdgesAndLinkedNodes, NodesAndLinkedEdges, LabelSet
from bokeh.plotting import figure, from_networkx
from bokeh.palettes import Blues8, Reds8, Purples8, Oranges8, Viridis8, Spectral8
from bokeh.transform import linear_cmap
from bokeh.models.widgets import Tabs, Panel
from bokeh.layouts import row
FACULTY, NAMES = fetch_faculty()

class Year:
    def __init__(self, year):
        self. year = year
        self.graph_nx = nx.Graph()       
        self.graph_nx_till = nx.Graph() 
        self.build_graph()
        self.add_properties_network()
        
    
    def build_graph(self):
        self.graph_nx.add_nodes_from(NAMES)
        self.graph_nx_till.add_nodes_from(NAMES)
        for faculty in FACULTY:            
            for paper in FACULTY[faculty].papers:
                if paper.year == self.year:
                    for author in paper.authors:
                        if (author in NAMES) and (author != FACULTY[faculty].name) and not(self.graph_nx.has_edge(FACULTY[faculty].name, author))and not(self.graph_nx.has_edge(author,FACULTY[faculty].name)):
                                self.graph_nx.add_edge(FACULTY[faculty].name, author)
                if (paper.year <= self.year) and (paper.year > 1999):
                    for author in paper.authors:
                        if (author in NAMES) and (author != FACULTY[faculty].name) and not(self.graph_nx_till.has_edge(FACULTY[faculty].name, author))and not(self.graph_nx_till.has_edge(author,FACULTY[faculty].name)):
                                self.graph_nx_till.add_edge(FACULTY[faculty].name, author)
        return
    
    def display_networkx(self):
        plt.figure(figsize = (24,12))
        pos =  nx.spring_layout(self.graph_nx)
        nx.draw_random(self.graph_nx, with_labels = True, font_weight = 'bold')
        plt.show()   
    
    def add_properties_network(self):     
        def get_graph_properties(network):
            degrees = dict(nx.degree(network))
            betweenness_centrality = nx.betweenness_centrality(network)

            nx.set_node_attributes(network, name='degree', values=degrees)
            nx.set_node_attributes(network, name='betweenness', values=betweenness_centrality)

            number_to_adjust_by = 5

            adjusted_node_size = dict([(node, degree+number_to_adjust_by) for node, degree in nx.degree(network)])
            nx.set_node_attributes(network, name='adjusted_node_size', values=adjusted_node_size)

            return

        get_graph_properties(self.graph_nx)   
        get_graph_properties(self.graph_nx_till)  
        return
    
    def draw_bokeh(self): 
        def get_plot(network, title):
            # plot with different sized node degrees + labels           
            size_by_this_attribute = 'adjusted_node_size'
            color_by_this_attribute = 'adjusted_node_size'

            color_palette = Viridis8

            HOVER_TOOLTIPS = [("Faculty", "@index"),("Degree", "@degree"),("Betweenness Centrality", "@betweenness")]

            plot = figure(tooltips = HOVER_TOOLTIPS, tools="pan,wheel_zoom,save,reset", active_scroll='wheel_zoom',
                    x_range=Range1d(-11.1, 11.1), y_range=Range1d(-11.1, 11.1), title=title, plot_width = 500, plot_height = 500)
            
            network_graph = from_networkx(network, nx.spring_layout, scale=10, center=(0, 0))

            minimum_value_color = min(network_graph.node_renderer.data_source.data[color_by_this_attribute])
            maximum_value_color = max(network_graph.node_renderer.data_source.data[color_by_this_attribute])
            network_graph.node_renderer.glyph = Circle(size=size_by_this_attribute, fill_color=linear_cmap(color_by_this_attribute, color_palette, minimum_value_color, maximum_value_color))

            network_graph.edge_renderer.glyph = MultiLine(line_alpha=0.5, line_width=1)
            plot.renderers.append(network_graph)

            return plot

        p1 = get_plot(self.graph_nx,"Collaboration for the current year")
        p2 = get_plot(self.graph_nx_till,"Collaboration since 2000")       

        return row(p1,p2)   

if __name__=="__main__":
    tabs = []
    tab = None
    for i in range(2000,2022):
        temp = Year(i)
        tabs.append(Panel(child = temp.draw_bokeh(), title = str(i)))  
    tab = Tabs(tabs=tabs)
    show(tab)
    

