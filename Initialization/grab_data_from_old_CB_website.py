# -*- coding: utf-8 -*-

'''
This file parses both the HTML from the old Computational Bio website ('CB_website_html.html')
and the XML data directly from PubMed ('Pubmed-Data.xml').
 
It produces a spreadhseet ('Old_website_data.xls') containing the PMID, Title, Keywords, 
Authors, Abstract, Article Link, PDF Link, Scholar Link, and Image Link of each study on the 
original website. This spreadsheet can then be usd as the main source of data for 
additioanl info on these studies, without having to rely on the obsolete HTML.

'''



import re
from bs4 import BeautifulSoup
import xlrd
import xlwt
import xml.etree.ElementTree as ET
#import string
from unicodedata import normalize

workbook = xlrd.open_workbook('Papers_annotated_withCategories.xlsx')
worksheet = workbook.sheet_by_index(0)

def parse_CB_HTML(): 
    f = open('CB_website_html.xml', 'r')
    doc = BeautifulSoup(f, 'html.parser')
    return doc
    
document = parse_CB_HTML()
    
def build_entry_by_id(doc):
    '''
    Goes through the old CB HTML and picks out the <table> elements that correspond to one study.
    Makes a dictionary that maps CB_ids to the corresponding HTML elements for further parsing.
    '''
    entries = {}
    tables = doc.find_all('a', attrs = {'name': True})
    for elt in tables: 
        if re.search('[0-9]', elt.get('name') ):
            entries[elt.get('name')] = elt
    return entries
    
entry_dict = build_entry_by_id(document)

def get_title_from_CB(CB_id):
    '''
    Uses id--> entry dict to get a title from a CB_id. Returns a string. 
    '''
    entry = entry_dict[CB_id]
    title = entry.b.text
    #strips the extra numbers and links included with the title to return only the appropriate text.
    id_regex = re.compile('^[A-Z]*[0-9]*.')
    title = re.sub(id_regex, '', title)
    end_text_regex = re.compile(' *\(pdf\) \(scholar\) *')
    end_match = re.search(end_text_regex, title)
    if end_match: 
        title = re.sub(end_text_regex, '', title)
    while title[0] == '.' or title[0] == ' ':
        title = title[1:]
    while title[-1] == ' ' or title[-1] == '.':
        title = title[:-1]
    title = title + '.'
    return str(title)

def build_ids_to_titles(doc):
    '''Uses get_title_from_CB to build a dictionary mapping an id to a title.'''
    titles = {}
    for CB_id in entry_dict: 
        title = get_title_from_CB(CB_id)
        titles[str(CB_id)] = str(title)
    return titles

ids_to_titles = build_ids_to_titles(parse_CB_HTML)
    
def id_to_CB_info(doc, CB_id, complete=False): 
    '''
    Returns a tuple containing info from the CompBio website HTML about the study with the given id. 
    If complete = False, returns link to PDF, link to scholar, additional link, and image
    If complete = True, returns the above plus title, authors, abstract
    '''
    entry = entry_dict[CB_id]
    all_links = entry.b.find_all('a') 
    if len(all_links) > 1: 
        #pulls out just the URL
        PDF = all_links[0].get('href')
        scholar = all_links[1].get('href')
    else: 
        PDF, scholar = '', ''        
    link = entry.find_all('a')[-1]
    image = 'http://compbio.mit.edu/' + entry.img.get('src')
    if not complete: 
        return (str(PDF), str(scholar), str(link), str(image))
    else: 
        title = get_title_from_CB(CB_id)
        authors = entry.ul.p.text
        abstract = entry.ul.find_all('p')[1].text
        ans = [PDF, scholar, link, image, title, authors, abstract]
        for elt in ans:
            if type(elt) == 'unicode':
                elt = normalize('NFKD', elt).encode('ASCII', 'ignore')
        return tuple(ans)

def build_titles_to_PMIDs(file_name):
    '''
    Parses an XML document. Builds a dictionary titles:PMID where the titles are lowercase (for better matching). 
    '''
    titles = {}
    tree = ET.parse(file_name)
    root = tree.getroot()
    for child in root: 
        title = child.findall('MedlineCitation/Article/ArticleTitle')[0].text
        title = title.lower()
        PMID = child.findall('MedlineCitation/PMID')[0].text
        titles[title] = PMID
    return titles
    
def build_ids_to_PMIDs(file_name):
    '''
    Uses build_ids_to_titles and build_titles_to_PMIDs to match ids to PMIDs so that we can identify studies across different platforms. 
    '''
    ids_to_PMIDs = {}
    ids_to_titles = build_ids_to_titles(parse_CB_HTML())
    titles_to_PMIDs = build_titles_to_PMIDs(file_name)
    #Hard-coded in some studies that are equivalent but that aren't matching properly throgh title matching. 
    mismatches = {'60': '21994247', '46': '21177974', '56': '21900599', '121': '25481006', '115': '25159142', '98': '24170599', '58': '21994248'}
    for id_num in ids_to_titles: 
        title = ids_to_titles[id_num].lower()
        if title in titles_to_PMIDs: 
            ids_to_PMIDs[id_num] = titles_to_PMIDs[title]
        elif id_num in mismatches: 
            ids_to_PMIDs[id_num] = mismatches[id_num]
        else:
            ids_to_PMIDs[id_num] = None
    return ids_to_PMIDs

ids_to_PMIDs = build_ids_to_PMIDs('Pubmed-Data.xml')
    
def build_PMIDs_to_ids(file_name):
    '''
    Reverses the dictionary created by the above function. 
    '''
    PMIDs_to_ids = {}
    ids_to_PMIDs = build_ids_to_PMIDs(file_name)
    for key in ids_to_PMIDs: 
        PMID = ids_to_PMIDs[key]
        if PMID != None:
            PMIDs_to_ids[PMID] = key
    return PMIDs_to_ids
    
def get_categories():
    '''
    Makes a list of all the different keywords/categories on the CB website, for use in generating the HTML.
    '''
    categories = set()
    workbook = xlrd.open_workbook('Papers_annotated_withCategories.xlsx')
    sheet = workbook.sheet_by_index(0)
    for i in range(1, 159): 
        cat = sheet.cell(i, 1).value.split(',')
        for elt in cat: 
            categories.add(str(elt))
    categories = list(categories)
    return categories
    
all_categories = get_categories()

def build_CB_ids_to_categories():
    '''
    Using the spreadsheet, creates a dictionary CB_id: categories (space deliminated).
    '''
    dictionary = {}
    workbook = xlrd.open_workbook('Papers_annotated_withCategories.xlsx')
    sheet = workbook.sheet_by_index(0)
    for i in range(1, 159): 
        #row = sheet.row(i)
        CB_id = sheet.cell(i,0).value
        try: 
            #pdb.set_trace()
            CB_id = str(int(CB_id))
        except ValueError: 
            CB_id = str(CB_id)
        categories = sheet.cell(i, 1).value
        categories = str(re.sub(',', ' ', categories))
        dictionary[CB_id] = categories
    return dictionary
    
CB_ids_to_categories = build_CB_ids_to_categories()

def build_PMIDs_to_categories(file_name): 
    cats = {}
    ids_to_PMIDs = build_ids_to_PMIDs(file_name)
    for CB_id in ids_to_PMIDs: 
        PMID = ids_to_PMIDs[CB_id]
        cats[PMID] = CB_ids_to_categories[CB_id]
    return cats

def build_master_spreadsheet():
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet('Sheet_1')
    sheet.write(0, 0, 'CompBio Id')
    sheet.write(0, 1, 'PMID')
    sheet.write(0, 2, 'Title')
    sheet.write(0, 3, 'Keywords')
    sheet.write(0, 4, 'Authors')
    sheet.write(0, 5, 'Abstract')
    sheet.write(0, 6, 'Article Link')
    sheet.write(0, 7, 'PDF Link')
    sheet.write(0, 8, 'Scholar Link')
    sheet.write(0, 9, 'Image Link')
    CB_studies = entry_dict.keys()
    for i in range(len(CB_studies)):
        try:
            CB_studies[i] = int(CB_studies[i])
        except ValueError:
            pass
    CB_studies.sort()
    for i in range(len(CB_studies)):
        row = i + 1
        CB_id = str(CB_studies[i])
        sheet.write(row, 0, CB_id) #CB_id
        sheet.write(row, 1, ids_to_PMIDs[CB_id]) #PMID
        sheet.write(row, 2, ids_to_titles[CB_id]) #Title
        sheet.write(row, 3, CB_ids_to_categories[CB_id]) #Keywords
        info = id_to_CB_info(parse_CB_HTML(), CB_id, True) #link to PDF, link to scholar, additional link, image, title, authors, abstract
        sheet.write(row, 4, info[5]) #Authors
        sheet.write(row, 5, info[6]) #abstract
        sheet.write(row, 6, str(info[2])) #main link
        sheet.write(row, 7, info[0]) #PDF link
        sheet.write(row, 8, info[1]) #scholar link
        sheet.write(row, 9, info[3]) #img link
    workbook.save('Old_website_data.xls')

build_master_spreadsheet()
print "done"




                   
        
