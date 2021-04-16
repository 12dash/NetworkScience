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

from faculty import ManageGraph, PositionGraph, ExcellenceGraph, Hire, FacultySubset

app = dash.Dash(external_stylesheets=[
                dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
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
        'background-color': "black",
        'width': "data(size)",
        'height': "data(size)"
    }},
    {'selector': 'edge',
     'style': {
         'width': "data(edge_size)",
         'height': "data(edge_size)"
     }
     },
    {
    'selector': ':selected',
    'style': {
        'background-color': "blue",
        'width': "data(size)",
        'height': "data(size)"
    }
}
]

FACULTY_GRAPH_STYLESHEET = [{
    'selector': 'node',
    'style': {
        'background-color': "data(color)",
        'width': "data(size)",
        'height': "data(size)"
    }
},
    {'selector': 'edge',
     'style': {
         'width': "data(edge_size)",
         'height': "data(edge_size)"
     }
     },
    {
    'selector': ':selected',
    'style': {
        'background-color': "blue",
        'width': "data(size)",
        'height': "data(size)"
    }
}]

YEAR = {}
OVERALL_GRAPHS = {}
FACULTY_SUBSET = None

RANKS_GRAPH = {}

MANAGE = ManageGraph()
LECT = PositionGraph('Lecturer')
SLECT = PositionGraph('Senior Lecturer')
ASST = PositionGraph('Assistant Professor')
ASSOC = PositionGraph('Associate Professor')
PROF = PositionGraph('Professor')
EXC = ExcellenceGraph()

HIRE = None


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
                        dbc.NavLink("Yearly Analysis",
                                    href="/year", active="exact"),
                        dbc.NavLink("Faculty Analysis",
                                    href="/faculty_analysis", active="exact"),
                        dbc.NavLink("Overall Information",
                                    href="/overall", active="exact"),
                        dbc.NavLink("Analysis based on ranks",
                                    href="/ranks", active="exact"),
                        dbc.NavLink("Analysis based on Management Position",
                                    href="/position", active="exact"),
                        dbc.NavLink("Analysis on areas",
                                    href="/areas", active="exact"),
                        dbc.NavLink("Analysis on excellence Node",
                                    href="/excellence", active="exact"),
                        dbc.NavLink("New Hire", href="/hire", active="exact")
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


def generateGraph(G, cytoscape_id, nodes_data=None, size="600px",size_by = 'degree', node_size=5, edge_size=0.3, stylesheet=None, layout='cose-bilkent'):
    def getNodes():
        nodes = []
        for node in G.nodes():
            temp = {'id': node, 'label': node}
            if nodes_data != None:
                for i in nodes_data:
                    if i == 'size':
                        if G.nodes[node][size_by] < 100:
                            temp[i] = f"{G.nodes[node][size_by] * node_size + node_size}%"
                        else:
                            temp[i] = f"15%"
                    else:
                        temp[i] = G.nodes[node][i]
            nodes.append({'data': temp})
        return nodes

    def getEdges():
        edges = []
        for edge in G.edges():
            edges.append({
                'data': {'source': edge[0], 'target': edge[1], 'edge_size': edge_size}
            })
        return edges

    nodes, edges = getNodes(), getEdges()

    width = size
    height = size

    if type(size) == list:
        width = size[0]
        height = size[1]

    graph = cyto.Cytoscape(
        id=cytoscape_id,
        layout={'name': layout},
        style={'width': width, 'height': height},
        elements=edges + nodes,
        stylesheet=stylesheet)
    return graph


def output_for_node(data):
    temp = None
    if data:
        temp = html.Div([
            html.H3(data['label']),
            html.Ul([
                html.Li(f"Degree : {data['degree']}"),
                html.Li(f"Betweeness Centrality: {data['betweenness']}"),
                html.Li(
                    f"Eigenvector Centrality: {data['eigenvector_centrality']}"),
                html.Li(
                    f"Closeness Centrality: {data['closeness_centrality']}"),
                html.Li(f"Degree Centrality: {data['degree_centrality']}"),
                html.Li(f"Clustering Coefficient : {data['clustering']}")])
        ])

    return temp


@app.callback(Output('cytoscape-mouseoverNodeData-output', 'children'), Input('year-graph', 'mouseoverNodeData'))
def displayTapNodeData(data):
    return output_for_node(data)


@app.callback(Output('cytoscape-overall-output', 'children'), Input('cummulative-year-graph', 'mouseoverNodeData'))
def displayTapNodeData(data):
    return output_for_node(data)


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
        table_header = [html.Thead(
            html.Tr([html.Th("Name"), html.Th("Value")]))]
        l = []
        for i in INFORMATION:
            l.append(
                html.Tr([html.Td(i), html.Td(Year.year_info[INFORMATION[i]])]))
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
        fig = px.line(df, x="Degree", y="Probability",
                      title='Degree Distribution', log_y=True)
        return dcc.Graph(figure=fig)

    def buildYearGraph():
        nodes_data = ['size', 'betweenness', 'degree_centrality',
                      'closeness_centrality', 'eigenvector_centrality', 'degree', 'clustering']
        network_graph = generateGraph(
            network, "year-graph", nodes_data=nodes_data, stylesheet=YEAR_GRAPH_STYLESHEET)
        return network_graph

    def buildCummulative():
        nodes_data = ['size', 'betweenness', 'degree_centrality',
                      'closeness_centrality', 'eigenvector_centrality', 'degree', 'clustering']
        network_graph = generateGraph(network_overall, "cummulative-year-graph",
                                      node_size=2, nodes_data=nodes_data, stylesheet=YEAR_GRAPH_STYLESHEET)
        return network_graph

    def buildConnectedComponent():
        l = []
        for i in Year.year_info['connected_components']:
            l.append(generateGraph(i, "connected-components",
                     size="300px", layout='circle'))
        return html.Div(dbc.Row(l))

    output_list = [
        html.H5('Information'),
        build_table(),
        html.H5("Year Graph"),
        dbc.Row(
            [dbc.Col(buildYearGraph()), dbc.Col(
                html.P(id='cytoscape-mouseoverNodeData-output'))],
            justify="center", align="center"),
        html.H5("Probability Degree Distribution"),
        getDegreeDistribution(),
        html.H5("Connected Components"),
        buildConnectedComponent(),
        html.H5("Cummulative Year Graph"),
        dbc.Row(
            [dbc.Col(buildCummulative()), dbc.Col(
                html.P(id='cytoscape-overall-output'))],
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

    OVERALL_GRAPHS['Average Degree'] = getPlot(
        'average_degree', 'Average Degree', 'Average Degree over the years')
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

        html.P(id='placeholder', style={'display': 'none'}),

        dcc.Dropdown(id="Faculty", options=option, value='MTL',
                     multi=True, placeholder="Select the set of faculty"),
        dcc.Dropdown(id="year_id_faculty_subset", options=year_option,
                     value='2000', placeholder="Select the year"),
        html.Button('Submit', id='submit-val', n_clicks=0,
                    style={'border-radius': '8px'}),
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
                l.append(
                    html.Li(i + " : " + str(faculty.info[year_value][INFO[i]])))
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
        OVERALL_GRAPHS['Average Degree'],
        OVERALL_GRAPHS['Average Clustering Coefficient']
    ])


@app.callback(Output("yearContent", "children"), Input("year_id", "value"))
def render_year_graph(value):
    return YEAR[int(value)]


click = 0


@app.callback(Output("faculty-subset", "children"), [Input("Faculty", "value"), Input("submit-val", "n_clicks"), Input("year_id_faculty_subset", "value")])
def render_faculty(value, n_clicks, year_value):

    global FACULTY_SUBSET
    global click

    if n_clicks != click:
        FACULTY_SUBSET = facultySubsetContent(value, year_value)
        click = n_clicks

    return FACULTY_SUBSET


def buildGraphsContent(names, year, position):
    facultySubset = FacultySubset(names)
    graph = generateGraph(facultySubset.graph_years[int(year)], f"{position}-subset-graph",
                          nodes_data=['color'], size="300px", stylesheet=FACULTY_GRAPH_STYLESHEET)
    return graph


def display_nodes_rank_data(data):
    if data:
        return html.Div([
            html.H3(data['label'])
        ])

def outpuHirePara(data):
    if data:
        return html.Div([
            html.H3(data['label']),
            html.Ul([
                    html.Li(["Degree : ", data['degree']]),
                    html.Li(["Original Degree : ", data['original_degree']]),                   
                    html.Li(["Number of Excellence Paper published : ", data['excellent']]),
                    ])
        ])

@app.callback(Output('hire-excellence-node-output', 'children'), Input('hire-graph-excellence', 'mouseoverNodeData'))
def displayTapNodeData(data):
    return outpuHirePara(data)

@app.callback(Output('hire-degree-node-output', 'children'), Input('hire-graph-degree', 'mouseoverNodeData'))
def displayTapNodeData(data):
    return outpuHirePara(data)





@app.callback(Output("lecturers-faculty-information", "children"), Input("lecturers-subset-graph", "mouseoverNodeData"))
def lecturer_info(data):
    return display_nodes_rank_data(data)


@app.callback(Output("senior_lecturers-faculty-information", "children"), Input("senior_lecturers-subset-graph", "mouseoverNodeData"))
def senior_lecturer_info(data):
    return display_nodes_rank_data(data)


@app.callback(Output("assistant-faculty-information", "children"), Input("assistant-subset-graph", "mouseoverNodeData"))
def assistant_info(data):
    return display_nodes_rank_data(data)


@app.callback(Output("assosicate-faculty-information", "children"), Input("assosicate-subset-graph", "mouseoverNodeData"))
def assosicate_info(data):
    return display_nodes_rank_data(data)


@app.callback(Output("professors-faculty-information", "children"), Input("professors-subset-graph", "mouseoverNodeData"))
def professors_info(data):
    return display_nodes_rank_data(data)


@app.callback(Output("ranks-content", "children"), Input("ranks_year_id", "value"))
def render_rank_year_graph(value):
    positions = {
        'lecturers': ["Lecturers", LECT.nodes],
        'senior_lecturers': ["Senior Lecturers", SLECT.nodes],
        'assistant': ["Assistant Professors", ASST.nodes],
        'assosicate': ["Associate Professors", ASSOC.nodes],
        'professors': ["Professors", PROF.nodes]
    }

    def build_names_list(names):
        output_list = []
        for i in names:
            output_list.append(html.Li(i))
        return html.Ul(output_list)
    output_list = []
    for i in positions:
        output_list.append(html.Div([
            html.H4(positions[i][0]),
            dbc.Row([
                buildGraphsContent(positions[i][1], int(value), i),
                html.Div(id=f"{i}-faculty-information")
            ], align="center")
        ]))
    output = html.Div(output_list)
    return output


def createRankPage():
    option = [{"label": i, "value": i} for i in range(2000, 2022)]
    return (
        html.Div([
            html.Label('Year'),
            dcc.Dropdown(
                id="ranks_year_id",
                options=option,
                value='2000'
            ), html.Div(id="ranks-content")]))


def createPosition():
    pass


def createAreas():
    pass


def createExcellence():
    return"Excellence Node"


def buildHire():
    global HIRE
    hire = Hire()
    print("Hire object created")
    nodes_data = ['size', 'degree', 'color','original_degree','excellent']
    graph1 = generateGraph(hire.graph_excellence, "hire-graph-excellence", size=['800px', '600px'],
                          edge_size=0.1, node_size=0.5, size_by='excellent', nodes_data=nodes_data, stylesheet=FACULTY_GRAPH_STYLESHEET)
    graph2 = generateGraph(hire.graph_degree, "hire-graph-degree", size=['800px', '600px'],
                          edge_size=0.1, node_size=0.5, size_by='excellent', nodes_data=nodes_data, stylesheet=FACULTY_GRAPH_STYLESHEET)
    temp = html.Div([
        dbc.Row([graph1,html.Div(id='hire-excellence-node-output')], align='center'),
        dbc.Row([graph2,html.Div(id='hire-degree-node-output')], align='center')
    ])
    HIRE = temp
    return


def newHire():
    global HIRE
    return HIRE


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
    elif pathname == '/ranks':
        return createRankPage()
    elif pathname == '/position':
        return createPosition()
    elif pathname == '/areas':
        return createAreas()
    elif pathname == '/excellence':
        return createExcellence()
    elif pathname == '/hire':
        return newHire()
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


def getApp(year):
    global app
    print("Building Year Graph...")
    buildYear(year)
    print("Building Overall Graph...")
    buildOverall(year)
    print("Building Hire informations")
    buildHire()
    print("Initializing...")
    initialize_layout()

    return app
