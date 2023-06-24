# ika-stats-parser
Statistics on wages and working conditions are crucial to understand economic and societal issues.  
IKA - EFKA (Greece national insurance organization) releases statistics on several issues on labor -market monthly and with greater "resolution" biannually.
The data are locate in the official website 
https://www.efka.gov.gr/el/miniaia-stoicheia-apascholeses-yearly
  
Unfortunately, IKA does not provides an API and/or directly machine readable data, making further analysis difficult.
The scope if this project is to parse PDF realesed by IKA - EFKA and transcribe the data to a format suitably for furhere analysis.  
Of-the-self approaches for reading tables from pdf are not suitable, as the tables are too complex to be parsed seemingly.  
## conf file
For each table to be parsed, a conf.file is constructed.  
The conf file contains keywords and keyphrases to help the script locate the table inside the pdf.  
Bear in mind that the encoding used, especially in some old pdfs is custom and it is difficult to simply match the words of the pdf with keywords.  
With a little tuning h, the script is capable of identifiying  the location  of the tables in the pdf.  
### conf file parameters  
* EXACT_STRING_TO_MATCH: An exact string to match in the page
* EXACT_STRING_TO_AVOID: An exact string to avoid in the page. 
* PAGE_RANGE:N1 N2 Table is located between pages N1 and N2
* SECTION S1/S0/S2 Table is located in specific section
* STRING_TO_REMOVE: An exact string to remove from the output stream
  
## usage
For parsing a single file  
parse_IKA --file=filename --conf=conf.file --addLines=0  
The included script loops over all pdf tow write a single csv file.
## how the script works
   The script is basic and its function is more-or-less trivial.  
   The most difficult part is identifying the correct page. A scoreboard approach is used, where keywords andf keyphrases are searched to find the most relevant pages in the document.
   The lines of the table are identified and used as a grid for placing text and numbers. The text located outside the grid is considered noise and is disregarded. Obviously, this text contains metadata and could be used to identify the table, had an approach of parsing the complete document been followd.
   Fianally the grid is printed row-wise or column wise depending on the orientation
   The grid is cleaned to remove rows or lines that are empty
   This version assumes that all PDF are correct, i.e. contain the sought table.  
   ### example conf files
   In the subfolders, example conf files for extracting specific tables are included.  
   The pdf data set used is the set of all biannual editions of IKA from 2006-2021
   In folder TABLE I.3 the pdf data set contained all published data from 2015 and a number of other docs from previous years.
## ToDo
   * Clean output from redundand data and noise 
   * Cleaner code
   * comment and document code
   * implement basic error-handling (i.e. wrong files, etc)
   * parse data schema from the table
   * handle different string encodings
   * implement a structure search, where the script matches the page to the dimensions of the table mined 
   
## Disclaimer
   The correctness of the parsed data is not throught tested. Use at your own risk.  
   The ownership of the data lies with IKA-EFKA. Use of the data might be subject to restrictions posed by IKA-EFKA. 
   The license explicitly DOES NOT hold for the datasets  which is not owned by the author
   
   
   
