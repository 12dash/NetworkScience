import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_cytoscape as cyto
import plotly.express as px

from collections import Counter
import networkx as nx
import pandas as pd

from faculty import FacultySubset
from preprocess import ManageGraph, PositionGraph, ExcellenceGraph

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
cyto.load_extra_layouts()

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "18rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

CONNECTED_COMPONENTS_STYLE = {
    'width': "300px",
    'height': "300px"
}

YEAR_GRAPH_STYLESHEET = [{
    'selector': 'node',
    'style': {
        'width': "data(size)",
        'height': "data(size)"
    }
}]

FACULTY_GRAPH_STYLESHEET = [{
    'selector': 'node',
    'style': {
        'background-color': "data(color)"
    }
}]

YEAR = {}
OVERALL_GRAPHS = {}
FACULTY_SUBSET = None
MANAGE = ManageGraph()
LECT = PositionGraph('Lecturer')
SLECT = PositionGraph('Senior Lecturer')
ASST = PositionGraph('Assistant Professor')
ASSOC = PositionGraph('Associate Professor')
PROF = PositionGraph('Professor')

MANAGE = ManageGraph()
LECT = PositionGraph('Lecturer')
SLECT = PositionGraph('Senior Lecturer')
ASST = PositionGraph('Assistant Professor')
ASSOC = PositionGraph('Associate Professor')
PROF = PositionGraph('Professor')
EXC = ExcellenceGraph()


def initialize_layout():
    '''
    Method to intialize the layout for the app including the sidebar and the creation of the div on the right
    '''

    global app

    def createSidebar():
        '''
        Generates the Sidebar and Specifies the links to the different pages
        '''
        sidebar = html.Div(
            [
                html.H2("Network Science", className="display-5"),
                html.Hr(),
                html.P(
                    "Analysis on the collaboration of the SCSE Faculties", className="lead"
                ),
                dbc.Nav(
                    [
                        dbc.NavLink("Home", href="/", active="exact"),
                        dbc.NavLink("Yearly Analysis", href="/year", active="exact"),
                        dbc.NavLink("Faculty Analysis", href="/faculty_analysis", active="exact"),
                        dbc.NavLink("Overall Information", href="/overall", active="exact"),
                    ],
                    vertical=True,
                    pills=True,
                ),
            ],
            style=SIDEBAR_STYLE,
        )
        return sidebar

    sidebar = createSidebar()
    content = html.Div(id="page-content", style=CONTENT_STYLE)
    app.layout = html.Div([dcc.Location(id="url"), sidebar, content])
    return


def generateGraph(G, cytoscape_id, nodes_data=None, size="600px", stylesheet=None, layout='cose-bilkent'):
    def getNodes():
        nodes = []
        for node in G.nodes():
            temp = {'id': node, 'label': node}
            if nodes_data != None:
                for i in nodes_data:
                    if i == 'size':
                        temp[i] = f"{G.nodes[node]['degree'] * 5 + 5}%"
                    else:
                        temp[i] = G.nodes[node][i]
            nodes.append({'data': temp})
        return nodes

    def getEdges():
        edges = []
        for edge in G.edges():
            edges.append({
                'data': {'source': edge[0], 'target': edge[1]}
            })
        return edges

    nodes, edges = getNodes(), getEdges()

    graph = cyto.Cytoscape(
        id=cytoscape_id,
        layout={'name': layout},
        style={'width': size, 'height': size},
        elements=edges + nodes,
        stylesheet=stylesheet)
    return graph


@app.callback(Output('cytoscape-mouseoverNodeData-output', 'children'), Input('year-graph', 'mouseoverNodeData'))
def displayTapNodeData(data):
    temp = None
    if data:
        temp = html.Div([
            html.H3(data['label']),
            html.Ul([
                html.Li(f"Degree : {data['degree']}"),
                html.Li(f"Betweeness Centrality: {data['betweenness']}"),
                html.Li(f"Eigenvector Centrality: {data['eigenvector_centrality']}"),
                html.Li(f"Closeness Centrality: {data['closeness_centrality']}"),
                html.Li(f"Degree Centrality: {data['degree_centrality']}"),
                html.Li(f"Clustering Coefficient : {data['clustering']}")])
        ])

    return temp

@app.callback(Output('cytoscape-overall-output', 'children'), Input('cummulative-year-graph', 'mouseoverNodeData'))
def displayTapNodeData(data):
    temp = None
    if data:
        temp = html.Div([
            html.H3(data['label']),
            html.Ul([
                html.Li(f"Degree : {data['degree']}"),
                html.Li(f"Betweeness Centrality: {data['betweenness']}"),
                html.Li(f"Eigenvector Centrality: {data['eigenvector_centrality']}"),
                html.Li(f"Closeness Centrality: {data['closeness_centrality']}"),
                html.Li(f"Degree Centrality: {data['degree_centrality']}"),
                html.Li(f"Clustering Coefficient : {data['clustering']}")])
        ])

    return temp


def buildYearContent(Year):
    network = Year.graph_year
    network_overall = Year.graph_previous_years

    INFORMATION = {
        'No. of Edges': 'number_of_edges',
        'Average Degree': 'average_degree',
        'Avg Clustering Coefficient': 'average_clustering_coefficient',
        'Avg Shortest Path Length': 'avg_dist',
        'Density': 'density',
        'No. of Connected Components': 'number_of_connected_components',
        'Degree Correlation': 'degree_correlation_coefficient'
    }

    def build_table():
        table_header = [html.Thead(html.Tr([html.Th("Name"), html.Th("Value")]))]
        l = []
        for i in INFORMATION:
            l.append(html.Tr([html.Td(i), html.Td(Year.year_info[INFORMATION[i]])]))
        table_body = [html.Tbody(l)]
        table = dbc.Table(table_header + table_body, bordered=True, dark=True, hover=True, responsive=True,
                          striped=True)
        return table

    def getDegreeDistribution():
        hist = Counter(sorted([i[1] for i in nx.degree(network)]))
        total = network.number_of_nodes()
        l1, l2 = [], []
        for i in hist:
            l1.append(i)
            l2.append(hist[i] / total)
        df = pd.DataFrame.from_dict({'Degree': l1, 'Probability': l2})
        fig = px.line(df, x="Degree", y="Probability", title='Degree Distribution', log_y=True)
        return dcc.Graph(figure=fig)

    def buildYearGraph():
        nodes_data = ['size', 'betweenness', 'degree_centrality', 'closeness_centrality', 'eigenvector_centrality','degree', 'clustering']
        network_graph = generateGraph(network, "year-graph", nodes_data=nodes_data, stylesheet=YEAR_GRAPH_STYLESHEET)
        return network_graph

    def buildCummulative():
        nodes_data = ['size', 'betweenness', 'degree_centrality', 'closeness_centrality', 'eigenvector_centrality','degree', 'clustering']
        network_graph = generateGraph(network_overall, "cummulative-year-graph", nodes_data=nodes_data, stylesheet=YEAR_GRAPH_STYLESHEET)
        return network_graph
    

    def buildConnectedComponent():
        l = []
        for i in Year.year_info['connected_components']:
            l.append(generateGraph(i, "connected-components", size="300px", layout='circle'))
        return html.Div(dbc.Row(l))

    output_list = [
        html.H5('Information'),
        build_table(),
        html.H5("Year Graph"),
        dbc.Row(
            [dbc.Col(buildYearGraph()), dbc.Col(html.P(id='cytoscape-mouseoverNodeData-output'))],
            justify="center", align="center"),
        html.H5("Probability Degree Distribution"),
        getDegreeDistribution(),
        html.H5("Connected Components"),
        buildConnectedComponent(),
        html.H5("Cummulative Year Graph"),
        dbc.Row(
            [dbc.Col(buildCummulative()), dbc.Col(html.P(id='cytoscape-overall-output'))],
            justify="center", align="center")
        ]

    return html.Div(output_list)


def buildYear(year):
    global YEAR
    for i in range(2000, 2022):
        YEAR[i] = buildYearContent(year[int(i)])
    return


def buildOverall(year):
    global OVERALL_GRAPHS

    def getPlot(name, y_axis, title):
        l1 = [i for i in range(2000, 2022)]
        l2 = [year[i].year_info[name] for i in range(2000, 2022)]
        df = pd.DataFrame.from_dict({'Year': l1, name: l2})
        fig = px.line(df, x="Year", y=name, title=title)
        return dcc.Graph(figure=fig)

    OVERALL_GRAPHS['Average Degree'] = getPlot('average_degree', 'Average Degree', 'Average Degree over the years')
    OVERALL_GRAPHS['Average Clustering Coefficient'] = getPlot('average_clustering_coefficient',
                                                               'Average Clustering Coefficient',
                                                               'Average Clustering Coefficient over the years')

    return

def contentHomePage():
    return


def contentYearPage():
    option = [{"label": i, "value": i} for i in range(2000, 2022)]
    return (
        html.Div([
            html.Label('Year'),
            dcc.Dropdown(
                id="year_id",
                options=option,
                value='2000'
            ), html.Div(id="yearContent")]))


def facultyContent():
    year_option = [{'label': i, 'value': i} for i in range(2000, 2022)]
    option = []

    for i in pd.read_csv("Faculty.csv")['Faculty'].to_list():
        option.append({'label': i, 'value': i})

    return html.Div([

        html.P(id='placeholder', style={'display':'none'}),
        
        dcc.Dropdown(id="Faculty",options=option, value='MTL', multi=True, placeholder="Select the set of faculty"), 
        dcc.Dropdown(id="year_id_faculty_subset", options=year_option, value='2000',placeholder = "Select the year"),
        html.Button('Submit', id='submit-val', n_clicks = 0, style = {'border-radius' : '8px'}),

        html.Button('Management', id='manageload', n_clicks = 0, style = {'border-radius' : '8px'}),
        html.Button('Lecturers', id='lectload', n_clicks = 0, style = {'border-radius' : '8px'}),
        html.Button('Sen. Lecturers', id='slectload', n_clicks = 0, style = {'border-radius' : '8px'}),
        html.Button('Asst. Prof.', id='asstload', n_clicks = 0, style = {'border-radius' : '8px'}),
        html.Button('Assoc. Prof.', id='assocload', n_clicks = 0, style = {'border-radius' : '8px'}),
        html.Button('Prof.', id='profload', n_clicks = 0, style = {'border-radius' : '8px'}),
        html.Button('Exc. Nodes', id='excload', n_clicks = 0, style = {'border-radius' : '8px'}),
        html.Div(id="faculty-subset")
    ])


def facultySubsetContent(value, year_value):
    year_value = int(year_value)

    def faculty_grid(faculty):
        def generateList():
            l = []
            INFO = {"Numbers of collaborators in SCSE": 'scse_collaboration',
                    "Total number of collaborators": "all_collaboration"}
            for i in INFO:
                l.append(html.Li(i + " : " + str(faculty.info[year_value][INFO[i]])))
            return html.Ul(l)

        graph1 = generateGraph(faculty.graph_years_scse[int(year_value)], "faculty-graph" + faculty.name, size="300px",
                               nodes_data=['color'], stylesheet=FACULTY_GRAPH_STYLESHEET)
        graph2 = generateGraph(faculty.graph_years_all[int(year_value)], "faculty-graph-all" + faculty.name,
                               size="300px", nodes_data=['color'], stylesheet=FACULTY_GRAPH_STYLESHEET)

        ul = generateList()

        out = html.Div([
            html.H3(faculty.name),
            ul,
            dbc.Row([
                dbc.Col(graph1),
                dbc.Col(graph2)
            ])
        ])
        return out

    facultySubset = FacultySubset(value)
    overall_graph = generateGraph(facultySubset.graph_years[int(year_value)], "faculty-subset-graph",
                                  nodes_data=['color'], stylesheet=FACULTY_GRAPH_STYLESHEET)
    l = []
    for i in facultySubset.faculty:
        l.append(faculty_grid(facultySubset.faculty[i]))

    return html.Div([dbc.Col(overall_graph), dbc.Col(l)])


def createOverallPage():
    global OVERALL_GRAPHS
    return html.Div([
        OVERALL_GRAPHS['Average Degree'], OVERALL_GRAPHS['Average Clustering Coefficient']
    ])


@app.callback(Output("yearContent", "children"), Input("year_id", "value"))
def render_year_graph(value):
    return YEAR[int(value)]


click = 0
@app.callback(Output("faculty-subset","children"), [Input("Faculty","value"), Input("submit-val", "n_clicks"), Input("year_id_faculty_subset","value")])
def render_faculty(value, n_clicks, year_value):
    
    global FACULTY_SUBSET
    global click

    if n_clicks != click: 
        FACULTY_SUBSET =  facultySubsetContent(value, year_value)  
        click = n_clicks   
        

    return FACULTY_SUBSET
    
catclick=[0, 0, 0, 0, 0, 0, 0]
@app.callback(Output("Faculty", "value"), Input("manageload","n_clicks"), Input("lectload","n_clicks"), 
              Input("slectload","n_clicks"), Input("asstload","n_clicks"), Input("assocload","n_clicks"),
              Input("profload","n_clicks"), Input('excload', 'n_clicks'))
def load_category(manageload, lectload, slectload, asstload, assocload, profload, excload):

    ctx = dash.callback_context

    global catclick

    value='MTL'

    c= [manageload, lectload, slectload, asstload, assocload, profload, excload]

    if c != catclick:

        if(c[0]!=catclick[0]):
            value=MANAGE.nodes
        elif(c[1]!=catclick[1]):
            value=LECT.nodes
        elif(c[2]!=catclick[2]):
            value=SLECT.nodes
        elif(c[3]!=catclick[3]):
            value=ASST.nodes
        elif(c[4]!=catclick[4]):
            value=ASSOC.nodes
        elif(c[5]!=catclick[5]):
            value=PROF.nodes
        elif(c[6]!=catclick[6]):
            value=EXC.nodes

        catclick=c

    return value


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return contentHomePage()
    elif pathname == "/year":
        return contentYearPage()
    elif pathname == "/faculty_analysis":
        return facultyContent()
    elif pathname == "/overall":
        return createOverallPage()
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


def getApp(year):
    global app
    buildYear(year)
    buildOverall(year)
    initialize_layout()
    return app





