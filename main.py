from preprocess import fetch_faculty
from faculty import Year, Faculty
from interface import show_html
import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("name", help="Faculy Name")
    args = parser.parse_args()
    
    FACULTY, NAMES = fetch_faculty()    

    year_graph = {}

    for i in range(2000,2021):
        year_graph[i] = Year(i, NAMES, FACULTY)

    name = args.name
    if name != None:
        faculty = Faculty(name)

    show_html(year_graph,name, faculty)




