from preprocess import fetch_faculty
import matplotlib.pyplot as plt
import networkx as nx
from bokeh.io import output_notebook, show, save
from bokeh.models import Range1d, Circle, ColumnDataSource, MultiLine, EdgesAndLinkedNodes, NodesAndLinkedEdges, LabelSet, Div
from bokeh.plotting import figure, from_networkx
from bokeh.palettes import Blues8, Reds8, Purples8, Oranges8, Viridis8, Spectral8
from bokeh.transform import linear_cmap
from bokeh.models.widgets import Tabs, Panel
from bokeh.layouts import row, layout
from collections import Counter

FACULTY, NAMES = fetch_faculty()

class Year:
    def __init__(self, year):
        self. year = year

        self.graph_nx = nx.Graph()
        self.graph_nx_till = nx.Graph()

        self.graph_nx_info = {}
        self.graph_nx_till_info = {}
        
        #self.build_graph()
        self.build_author_graph()
        self.get_information()
        self.add_properties_network()

    def build_graph(self):
        self.graph_nx.add_nodes_from(NAMES)
        self.graph_nx_till.add_nodes_from(NAMES)
        for faculty in FACULTY:
            for paper in FACULTY[faculty].papers:
                if paper.year == self.year:
                    for author in paper.authors:
                        if (author in NAMES) and (author != FACULTY[faculty].name) and not(self.graph_nx.has_edge(FACULTY[faculty].name, author)) and not(self.graph_nx.has_edge(author, FACULTY[faculty].name)):
                            self.graph_nx.add_edge(
                                FACULTY[faculty].name, author)
                if (paper.year <= self.year) and (paper.year > 1999):
                    for author in paper.authors:
                        if (author in NAMES) and (author != FACULTY[faculty].name) and not(self.graph_nx_till.has_edge(FACULTY[faculty].name, author)) and not(self.graph_nx_till.has_edge(author, FACULTY[faculty].name)):
                            self.graph_nx_till.add_edge(
                                FACULTY[faculty].name, author)
        return
    
    def build_author_graph(self):
        faculty = "Lee Bu Sung Francis"
        self.graph_nx.add_nodes_from(NAMES)
        self.graph_nx_till.add_nodes_from(NAMES)
        for paper in FACULTY[faculty].papers:
            if paper.year == self.year:
                for author in paper.authors:
                    if (author in NAMES) and (author != FACULTY[faculty].name) and not(self.graph_nx.has_edge(FACULTY[faculty].name, author)) and not(self.graph_nx.has_edge(author, FACULTY[faculty].name)):
                        self.graph_nx.add_edge(
                            FACULTY[faculty].name, author)
            if (paper.year <= self.year) and (paper.year > 1999):
                 for author in paper.authors:
                    if (author in NAMES) and (author != FACULTY[faculty].name) and not(self.graph_nx_till.has_edge(FACULTY[faculty].name, author)) and not(self.graph_nx_till.has_edge(author, FACULTY[faculty].name)):
                        self.graph_nx_till.add_edge(
                            FACULTY[faculty].name, author)
        return

    def display_networkx(self):
        plt.figure(figsize=(24, 12))
        pos = nx.spring_layout(self.graph_nx)
        nx.draw_random(self.graph_nx, with_labels=True, font_weight='bold')
        plt.show()
    
    def get_information(self):
        def get_info(network, network_dic):
            def get_average_degree(network):
                degrees = [i[1] for i in (network.degree())]
                degrees = sum(degrees)
                avg_degree = degrees/(network.number_of_nodes())
                return avg_degree
            
            def get_average_clustering(network):
                return nx.average_clustering(network)
            
            network_dic['average_degree']=get_average_degree(network)
            network_dic['average_clustering_coefficient']=get_average_clustering(network)
        
        get_info(self.graph_nx,self.graph_nx_info)
        get_info(self.graph_nx_till,self.graph_nx_till_info)

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

            adjusted_node_size = dict(
                [(node, degree+number_to_adjust_by) for node, degree in nx.degree(network)])
            nx.set_node_attributes(
                network, name='adjusted_node_size', values=adjusted_node_size)

            return

        get_graph_properties(self.graph_nx)
        get_graph_properties(self.graph_nx_till)
        return

    def draw_bokeh(self):
        def get_degree_distribution(network, title):
            degree = [i[1] for i in nx.degree(network)]
            values = sorted(degree)
            hist = Counter(values)
            l1 = []
            l2 = []
            for i in hist:
                l1.append(i)
                l2.append(hist[i])

            p = figure(title=title, plot_width=400, plot_height=400,
                       y_axis_type="log", x_axis_type="log")
            p.line(l1, l2, line_width=2)
            return p

        def get_network_plot(network, title):
            # plot with different sized node degrees + labels
            size_by_this_attribute = 'adjusted_node_size'
            color_by_this_attribute = 'adjusted_node_size'

            color_palette = Viridis8

            HOVER_TOOLTIPS = [("Faculty", "@index"), ("Degree", "@degree"),
                              ("Betweenness Centrality", "@betweenness"),
                              ("Clustering Coefficient", "@clustering")]

            plot = figure(tooltips=HOVER_TOOLTIPS, tools="pan,wheel_zoom,save,reset", active_scroll='wheel_zoom',
                          x_range=Range1d(-11.1, 11.1), y_range=Range1d(-11.1, 11.1), title=title, plot_width=400, plot_height=400)

            network_graph = from_networkx(
                network, nx.spring_layout, scale=10, center=(0, 0))

            minimum_value_color = min(
                network_graph.node_renderer.data_source.data[color_by_this_attribute])
            maximum_value_color = max(
                network_graph.node_renderer.data_source.data[color_by_this_attribute])
            network_graph.node_renderer.glyph = Circle(size=size_by_this_attribute, fill_color=linear_cmap(
                color_by_this_attribute, color_palette, minimum_value_color, maximum_value_color))
            network_graph.edge_renderer.glyph = MultiLine(
                line_alpha=0.5, line_width=1)
            plot.renderers.append(network_graph)

            return plot
        
        def get_row(title_plot, title_degree, network, network_dic):
            plots = get_network_plot(network,title_plot)
            degree_distribution = get_degree_distribution(network, title_degree)
            info = div = Div(text=f"<div><br/><br/><br/><br/><br/><br/><br/><br/><b>Average Degree</b> : {network_dic['average_degree']}<br /><b>Average Clustering Coefficient </b> : {network_dic['average_clustering_coefficient']}</div>", width = 400, height = 200)
            return row([plots,degree_distribution,info])

        row_1 = get_row(f"Collaboration in {self.year}", "Degree Distribution",self.graph_nx,self.graph_nx_info)
        row_2 = get_row(f"Collaboration since 2000", "Degree Distribution",self.graph_nx_till,self.graph_nx_till_info)        

        return layout([row_1,row_2])


if __name__ == "__main__":
    text = """<h1>Network Science</h1>
    <div>In an attempt to understand the collaboration between the different professors.</div>"""
    div = Div(text=text, width=200, height=100)
    div_text = Div(text="<h2>Collaboration Network Over the years from 2000<h2/><hr/>")

    tabs = []
    tab = None
    for i in range(2000, 2021):
        temp = Year(i)
        tabs.append(Panel(child=temp.draw_bokeh(), title=str(i)))
    tab = Tabs(tabs=tabs)

    disp = layout([div,div_text, tab])
    show(disp)
