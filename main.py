from preprocess import fetch_faculty
from faculty import Year, Faculty
from interface_new import show_html


if __name__ == "__main__":
    
    FACULTY, NAMES = fetch_faculty()

    year_graph = {}

    for i in range(2000,2021):
        year_graph[i] = Year(i, NAMES, FACULTY)

    name = "A S Madhukumar"
    faculty = Faculty(name)

    show_html(year_graph,name, faculty)




