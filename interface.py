from pre import fetch_faculty
import matplotlib.pyplot as plt
import networkx as nx

FACULTY, NAMES = fetch_faculty()

class Year:
    def __init__(self, year):
        self. year = year
        self.graph_nx = nx.Graph()
        self.build_graph()
        self.display_networkx()
    
    def build_graph(self):
        self.graph_nx.add_nodes_from(NAMES)
        for faculty in FACULTY:
            for paper in FACULTY[faculty].papers:
                if paper.year == self.year:
                    for author in paper.authors:
                        if (author in NAMES) and (not self.graph_nx.has_edge(FACULTY[faculty].name, author)):
                                self.graph_nx.add_edge(FACULTY[faculty].name, author)
        return
    
    def display_networkx(self):
        plt.figure(figsize = (24,12))
        pos =  nx.spring_layout(self.graph_nx)
        nx.draw_random(self.graph_nx, with_labels = True, font_weight = 'bold')
        plt.show()

if __name__=="__main__":
    a = Year(2021)
    

