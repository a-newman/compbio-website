# -*- coding: utf-8 -*-
"""
This file creates HTML for the new website ('newHTML.html') based on master_spreadsheet.xml. 


"""
from unicodedata import normalize
#from map_nums_to_PMID_v2 import build_PMIDs_to_categories, build_PMIDs_to_ids, entry_dict, document, id_to_CB_info, CB_ids_to_categories, all_categories
import xlrd

workbook = xlrd.open_workbook('master_spreadsheet.xls')
sheet = workbook.sheet_by_index(0) 
    
def get_info_from_spreadsheet(row): 
    info = {}
    info['PMID'] = sheet.cell(row, 0).value
    info['CB_id'] = sheet.cell(row, 1).value
    info['title'] = sheet.cell(row, 2).value
    info['keywords'] = sheet.cell(row, 3).value
    info['authors'] = sheet.cell(row, 4).value
    info['date'] = sheet.cell(row, 5).value
    info['abstract'] = sheet.cell(row, 6).value
    info['link'] = sheet.cell(row, 7).value
    info['PDF'] = sheet.cell(row, 8).value
    info['scholar'] = sheet.cell(row, 9).value
    info['image'] = sheet.cell(row, 10).value
    info['PMID_link'] = sheet.cell(row, 11).value
    return info   

def build_HTML(info): 
    HTMLstring = ""
    HTMLstring += '''
            <div class='grid-item %s'>''' %(info['keywords'])
    if info['image']: 
        HTMLstring += '''
                %s''' %(info['image'])
    HTMLstring += '''
                <h3 class='title'>%s</h3>''' %(info['title'])
    HTMLstring += '''
                    <p class='authors'>%s</p>''' %(info['authors'])
    HTMLstring += '''
                    <p class='date'>%s</p>''' %(info['date'])
    HTMLstring += '''
                    <p class='abstract'>%s</p>''' %(info['abstract'])
    HTMLstring += '''
                    <div class='links'>%s<br>
                        <div class='PDF-Google-PM'>
                            %s 
                            %s 
                            <a href='%s'>PubMed</a>
                        </div>
                    </div>''' %(info['link'], info['PDF'], info['scholar'], info['PMID_link'])
    HTMLstring += '''
            </div>
            '''
    return HTMLstring

def build_HTML_whole_grid():
    master_HTML = '''
        <div class="grid">
        '''
    for row in range(1, max(len(sheet.col_values(0)), len(sheet.col_values(1)))):
        info = get_info_from_spreadsheet(row)
        master_HTML += build_HTML(info)
    master_HTML += '''
        </div>'''
    return master_HTML
    
def get_HTML_header_and_footer(): 
    header = '''<!DOCTYPE html>\
<!-- saved from url=(0017)http://localhost/ -->
<html>
    <head>
    <!-- jquery -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.0/jquery.min.js"></script>
    <!-- isotope -->
    <script src="isotope.js"></script>
    <!-- implementing isotope-->
    <script src="filtering.js"></script>
    <!--Images loaded: so I can reload the page w/o having operlap-->
    <script src="imagesloaded.pkgd.min.js"></script>
    <!-- CSS -->
    <link rel="stylesheet" type="text/css" href="stylesheet.css">
</head>

<body>
    <h1>CompBio Sample Website</h1>'''
    footer = '''
    </body>
</html>'''
    return header, footer
    
def get_categories():
    '''
    Makes a list of all the different keywords/categories, for use in generating the HTML.
    '''
    categories = set()
    for i in range(1, len(sheet.col_values(1))): 
        cat = sheet.cell(i, 3).value.split(' ')
        for elt in cat: 
            if elt!= '': 
                categories.add(str(elt))
    categories = list(categories)
    return categories

def build_HTML_filtering(): 
    keywords = get_categories()
    HTML = '''
        <div>
        <h2>Filter by Topic</h2>
            <div class="select-topics">'''
    display_keyword = {'variation': 'Variation and Disease', 'genomes': 'Genome Interpretation', 'lncRNAs': 'Long Non-coding RNAs', 'miRNAs': 'MicroRNAs', 'genes': 'Genes', 'epigenomics': 'Epigenomics', 'motifs': 'Regulatory Motifs', 'networks': 'Bio Networks', 'evolution': 'Evolution', 'phylogenomics': 'Phylogenomics', 'algo': 'Algorithms', 'vision': 'Geometry/Vision', 'robotics': 'Robotics/AI', 'editorials': 'Editorials', 'smallRNAs': 'SmallRNAs', 'chromatin': 'Chromatin', 'ncRNAs': 'Non-Coding RNAs', 'smRNAs': 'SMRNAs'}
    for elt in keywords: 
        if elt in display_keyword: 
            display = display_keyword[elt]
        else: 
            display = str(elt)
        HTML += '''
                    <label><input type="checkbox" id="%s" value=".%s">%s</label>''' %(elt, elt, display)
    HTML += '''
            </div>
            '''
    return HTML
    
def get_HTML_show_hide(): 
    return '''
        <h2>Show/Hide Information</h2>
            <div class="show-hide">
			<label><input type="checkbox" id="hide-abstract" value=".grid .abstract" checked>Show Abstracts</label>
			<label><input type="checkbox" id="hide-pictures" value=".grid img" checked>Show Pictures</label>
			<label><input type="checkbox" id="hide-authors" value=".grid .authors" checked>Show Authors</label>
			<label><input type="checkbox" id="hide-links" value=".grid .links" checked>Show Links</label>
		</div>'''
def get_HTML_search():
    return '''
        <h2>Search</h2>
        <div style="margin: 10px">
            <input type="text" id="search" style="display: inline-block">
            <form id="search-select" style="display: inline-block">
                <input type="radio" name="search-option" value="h3" id="search-titles">Titles
                <input type="radio" name="search-option" value="p.abstract" id="search-abstract">Abstracts
                <input type="radio"  name="search-option" value ="p.authors" id="search-authors">Authors
                <input type="radio" name="search-option" value="" id="search-all" checked>All
            </form><br></div>
            '''
    
def build_HTML_whole_site(): 
    string = get_HTML_header_and_footer()[0] + get_HTML_show_hide() + build_HTML_filtering() + get_HTML_search() + build_HTML_whole_grid() + get_HTML_header_and_footer()[1]
    #string = build_HTML_whole_grid()
    f = open('newHTML.html', 'w')
    string = normalize('NFKD', string).encode('ASCII', 'ignore')
    f.write(string)
    print "Website HTML succesfully generated."

build_HTML_whole_site()


#if a cell is empty, sheet.cell(x, y).value returns '' and evaluates to False