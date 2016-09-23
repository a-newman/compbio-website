# -*- coding: utf-8 -*-
"""
This file parses the PubMed XML data ('Pubmed-Data.xml') and the spreadsheet containing info
about studies from the old CompBio website ('Old_website_data.xls') to create a master spreadsheet
containing important information about every study for which we have information (both from Pubmed)
and from the old website. If we do not have information of a certain category for a certain study,
the cell i sjust left blank. This information is stored in 'master_spreadsheet.xls'. This file can then
be quickly used to generate HTML for the new website. 
"""
# -*- coding: utf-8 -*-

#Create a master spreadsheet from PubMed Data and old CB_id data. Pretty much follow the model for
#the HTML creation, minus the HTML elements. Just put the info in a spreadhseet. 
#Only dependencies should be the old_CB_info spreadsheet and the PubMed Data

import xml.etree.ElementTree as ET
import xlrd
import xlwt
import string
#from HTML_generation_from_spreadsheet import get_categories

def build_PMIDs_to_CBids_using_spreadsheet(): 
    '''
    Returns a dictionary mapping PMIDs to CB_ids (both are given as strings). 
    If a PMID does not have an associated CB_id, it will not be included in the dictionary. 
    '''
    PMIDs_to_ids = {}
    workbook = xlrd.open_workbook('Old_website_data.xls')
    sheet = workbook.sheet_by_index(0)
    #i gives the row #
    for i in range(1, len(sheet.col_values(1))): 
        #if there exists a corresponding CB_id
        PMID = sheet.cell(i, 1).value
        if PMID:  
            PMIDs_to_ids[str(PMID)] = str(sheet.cell(i, 0).value)
    return PMIDs_to_ids
    
PMIDs_to_ids = build_PMIDs_to_CBids_using_spreadsheet()
    
#PMIDs_to_cats = build_PMIDs_to_categories('PubMed-Data.xml')
#PMIDs_to_ids = build_PMIDs_to_ids('PubMed-Data.xml')
    
def get_info_HTML_PM_and_CB(elt): 
    #elt is a child node in the PM XML doc 
    
    #PM info
    info = {}
    info['title'] = elt.findall('MedlineCitation/Article/ArticleTitle')[0].text
    info['PMID'] = elt.findall('MedlineCitation/PMID')[0].text
    info['PMID_link'] = 'http://www.ncbi.nlm.nih.gov/pubmed/' + str(info['PMID'])
    info['date'] = elt.findall('MedlineCitation/DateCreated/Month')[0].text + '/' + elt.findall('MedlineCitation/DateCreated/Day')[0].text + '/' + elt.findall('MedlineCitation/DateCreated/Year')[0].text
    
    if len(elt.findall('.//AbstractText')) > 0: 
        info['abstract'] = elt.findall('.//AbstractText')[0].text
    else: 
        info['abstract'] = ''
        
    author_list = elt.findall('.//Author')
    authors = ''
    for author in author_list: 
        if len(author.findall('Initials')) > 0: 
            initials = author.findall('Initials')[0].text
        else: 
            initials = ''
        if len(author.findall('LastName')) > 0: 
            lastname = author.findall('LastName')[0].text
        else: 
            lastname = ''
        if len(author.findall('CollectiveName')) > 0: 
            collectivename = author.findall('CollectiveName')[0].text
        else: 
            collectivename = ''
        authors += initials + ' ' + lastname + ', '
    info['authors'] = authors[:-2] + '.'    
    
    if info['PMID'] in PMIDs_to_ids: 
        CB_id = PMIDs_to_ids[info['PMID']]
        info['CB_id'] = CB_id
        workbook = xlrd.open_workbook('Old_website_data.xls')
        sheet = workbook.sheet_by_index(0)
        
        #find the row corresponding to the correct information
        for i in range(len(sheet.col_values(0))): 
            if str(sheet.cell(i, 0).value) == CB_id: 
                row = i 
        if not row: 
            print "ERROR: unmatched CB_id:", CB_id
        info['PDF'] = sheet.cell(row, 7).value
        info['PDF'] = '<a href ="%s">PDF</a>' %(info['PDF'])
        
        info['scholar'] = sheet.cell(row, 8).value
        info['scholar'] = '<a href ="%s">Google Scholar</a>' %(info['scholar'])
        
        info['link'] = sheet.cell(row, 6).value
        info['link'] = info['link'] + '<br>'
        
        info['image'] = sheet.cell(row, 9).value
        info['image'] = "<img src='%s'>\n" %(info['image'])
        
        info['keywords'] = sheet.cell(row, 3).value
        
    else: 
        #scholar link: 
        info['scholar'] = 'https://scholar.google.com/scholar?hl=en&q='
        info['scholar'] += string.join(string.split(info['title'], ' '), '%20')
        info['scholar'] = '<a href=' + info['scholar'] + '>Google Scholar</a>'
        
        #images and pdf link: 
        image_URL_id = info['PMID'] + '_' + author_list[0].findall('LastName')[0].text + '_'
        journal_raw = elt.findall('MedlineCitation/Article/Journal/Title')[0].text
        journal = ''
        for word in string.split(journal_raw, ' '): 
            journal += string.capitalize(word)
        image_URL_id += journal
        info['image'] = "<img src='http://compbio.mit.edu/publications/" + image_URL_id + ".png'>"
        info['PDF'] = '<a href ="publications/' + image_URL_id + '.pdf">PDF</a>'
        
        #keywords: include all by default: 
        info['keywords'] = string.join(['smRNAs', 'chromatin', 'robotics', 'editorials', 'genes', 'miRNAs', 'evolution', 'epigenomics', 'genomes', 'lncRNAs', 'phylogenomics', 'variation', 'motifs', 'ncRNAs', 'smallRNAs', 'networks', 'vision', 'algo'], ' ')
        
        #link
        EID = elt.findall('MedlineCitation/Article/ELocationID')
        if len(EID) > 0:
            info['link'] = '<a href="Dx.doi.org/' + elt.findall('MedlineCitation/Article/ELocationID')[0].text + '">' + journal_raw + '</a><br>'
        else: 
            print "no EID"
            info['link'] = journal_raw + '<br>'
        
        info['CB_id'] = ''
    
    return info

#UPDATE THIS FUNCTION TO DRAW FROM THE SPREADSHEET I CREATED, AS OPPOSED TO DIRECTLY FROM THE FUNCTIONS
def get_info_HTML_CB_only(CB_id, row = None): 
    info = {}
    workbook = xlrd.open_workbook('Old_website_data.xls')
    sheet = workbook.sheet_by_index(0)
    
    #find the right row of the spreadsheet
    if not row: 
        for i in range(len(sheet.col_values(0))): 
                if str(sheet.cell(i, 0).value) == CB_id: 
                    row = i 
    if not row: 
        print "ERROR: unmatched CB_id" 
    
    info['CB_id'] = sheet.cell(row, 0).value
    
    info['PDF'] = sheet.cell(row, 7).value
    info['PDF'] = '<a href ="%s">PDF</a>' %(info['PDF'])
    
    info['scholar'] = sheet.cell(row, 8).value
    info['scholar'] = '<a href ="%s">Google Scholar</a>' %(info['scholar'])
    
    info['link'] = sheet.cell(row, 6).value
    info['link'] = info['link'] + '<br>'
    
    info['image'] = sheet.cell(row, 9).value
    info['image'] = "<img src='%s'>\n" %(info['image'])
    
    info['title'] = sheet.cell(row, 2).value
    info['authors'] = sheet.cell(row, 4).value
    info['abstract'] = sheet.cell(row, 5).value
    info['keywords'] = sheet.cell(row, 3).value
    
    info['date'], info['PMID_link'], info['PMID'] = '', '', ''
    
    return info
    
#order of columns: 
    # PMID, CB_id, Title, Keywords, Authors, Date, Abstract, Article Link, PDF LInk, Scholar Link, 
    #Image Link, PMID Link
    
def write_info_to_spreadsheet(info, sheet, i): 
    #if (not sheet.cell(i, 0)) or (not sheet.cell(i, 1)): 
        #print "INDEXING ERROR: row", i, "is already full." 
    sheet.write(i, 0, info['PMID'])
    sheet.write(i, 1, info['CB_id'])
    sheet.write(i, 2, info['title'])
    sheet.write(i, 3, info['keywords'])
    sheet.write(i, 4, info['authors'])
    sheet.write(i, 5, info['date'])
    sheet.write(i, 6, info['abstract'])
    sheet.write(i, 7, info['link'])
    sheet.write(i, 8, info['PDF'])
    sheet.write(i, 9, info['scholar'])
    sheet.write(i, 10, info['image'])
    sheet.write(i, 11, info['PMID_link'])
    
def build_master_spreadsheet(): 
    tree = ET.parse('PubMed-Data.xml')
    root = tree.getroot()
    
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet('Sheet_1')
    sheet.write(0, 0, 'PMID')
    sheet.write(0, 1, 'CompBio Id')
    sheet.write(0, 2, 'Title')
    sheet.write(0, 3, 'Keywords')
    sheet.write(0, 4, 'Authors')
    sheet.write(0, 5, 'Date')
    sheet.write(0, 6, 'Abstract')
    sheet.write(0, 7, 'Article Link')
    sheet.write(0, 8, 'PDF Link')
    sheet.write(0, 9, 'Scholar Link')
    sheet.write(0, 10, 'Image Link')
    sheet.write(0, 11, 'PMID Link')
    
    i = 1
    for child in root: 
        info = get_info_HTML_PM_and_CB(child)
        write_info_to_spreadsheet(info, sheet, i)
        i += 1
    
    old_data_workbook = xlrd.open_workbook('Old_website_data.xls')
    old_data_sheet = old_data_workbook.sheet_by_index(0)
    for j in range(1, len(old_data_sheet.col_values(0))): 
        #CB_id = old_data_sheet.cell(j, 0).value
        PMID = old_data_sheet.cell(j, 1).value
        if not PMID: 
            info = get_info_HTML_CB_only(None, j)
            write_info_to_spreadsheet(info, sheet, i)
            i += 1
            
    workbook.save('master_spreadsheet.xls')
    print "Workbook 'master_spreadsheet.xls' succesfully created."
    
build_master_spreadsheet()