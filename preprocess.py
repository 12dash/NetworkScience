import xml.etree.ElementTree as ET
import os
import pandas as pd

FACULTY_DF = pd.read_csv("Faculty.csv")
FACULTY_PID = {}

top=[
    'nips','sigmod',
    'kdd','sigir',
    'cvpr','sigcomm',
    'ccs', 'icse',
    'isca','chi',
    'podc', 'siggraph',
    'recomb', 'mm']

class PublishedPaper:

    def __init__(self, xml_raw):
        
        self.xml_raw = xml_raw 

        self.authors = []
        self.title = None
        self.year = None
        self.paper_type = None     

        self.excellentPaper = False   

        self.fetch_info() 
        
    def fetch_info(self):
        for x in self.xml_raw.iter():
            if x.tag == "article":
                self.paper_type = "journal"
            elif x.tag == "inproceedings":
                self.paper_type = "conference"            
            if x.tag == "author":
                try:
                    self.authors.append(FACULTY_PID[x.attrib['pid']])
                except Exception as e:
                    author_name = (x.text)
                    author_name = ''.join([i for i in author_name if not i.isdigit()])
                    self.authors.append(author_name)

            elif x.tag == "year":
                self.year = (int)(x.text)
            elif x.tag == "title":
                self.title = x.text 

            #Check to see if it is a conference as well as not a workshop paper
            if(x.tag=='crossref' and x.text[:5]=='conf/' and x.text[-1]!='w'):
                if(x.text[5:x.text.index('/', 5, -1)] in top):
                    self.excellentPaper=True  
       
class Faculty:    
    
    excellenceThreshold=8

    def __init__(self,name):      

        self.position = None
        self.gender = None
        self.managment = None
        self.xml = None
        self.area = None

        self.excellenceNode = False

        self.papers = []

        self.name = name
        self.xml_path = f"./Data/{name}.xml"

        self.get_data_df()
        self.load_xml()
        self.parse_xml()
        self.checkExcellence()

        
    def checkExcellence(self):
        '''
        Checks if the faculty qualifies as excellence node or not 
        '''  
        excellence=0        
        for x in self.papers:
            if(x.year>=2010 and x.excellentPaper):
                excellence+=1                
        if(excellence>=Faculty.excellenceThreshold):
            self.excellenceNode=True
        
    
    def get_data_df(self):

        row = FACULTY_DF[FACULTY_DF["Faculty"]==self.name]

        self.gender = row.Gender.to_list()[0]
        self.position = row.Position.to_list()[0]
        self.managment = row.Management.to_list()[0]
        self.area = row.Area.to_list()[0]

        return

    def load_xml(self):
        self.xml = ET.parse(self.xml_path)
        return
    
    def parse_xml(self):
        root = self.xml.getroot()
        for x in root:            
            if(x.tag == 'r'):
                self.papers.append(PublishedPaper(x))
        return

    def printFaculty(self):
        print(f"{self.name}\t\t{self.gender}\t\t{self.position}\t\t{self.managment}\t\t{self.area}")
        return

def faculty_pid(name):
    xml_path = f"./Data/{name}.xml"
    xml = ET.parse(xml_path)
    root=xml.getroot()
    pid=root.attrib['pid']
    FACULTY_PID[pid] = name


def fetch_faculty():
    faculty_names = (os.listdir("./Data"))
    faculty_names = [i[:i.rfind(".")] for i in faculty_names]
    faculty = {}
    for i in faculty_names:
        faculty_pid(i)
    for i in faculty_names:
        faculty[i] = Faculty(i)
    return faculty, faculty_names


if __name__=="__main__":
    faculty_names = (os.listdir("./Data"))
    faculty_names = [i[:i.rfind(".")] for i in faculty_names]
    faculty = {}
    for i in faculty_names:
        faculty[i] = Faculty(i)