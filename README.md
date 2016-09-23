# compbio-website
Filtering, formatting, and url hashing for the MIT Computational Biology Group's website. (http://compbio.mit.edu/explore.html)

This code generates an interactive, filterable, aesthetically appealing webpage showing the studies published by the Computational Biology Group. The webpage is generated from Pubmed data.

The main folder contains the HTML, stylesheet, JavaScript, and dependencies for the website page.

The `Initialization` folder contains files to automatically generate HTML from Pubmed study data. `grab_data_from_old_CB_website.py` parses HTML from the old, non-interactive version of the website in order to find study data that is not on Pubmed. `generate_master_spreadsheet_initial.py` combines this information with Pubmed XML to create a spreadsheet listing each study and its relevant information, so that the data can be reviewed (and if needed, corrected by the site administrator) before publishing. `HTML_generation_from_spreadsheet.py` creates a new HTML document using the spreadsheet.
