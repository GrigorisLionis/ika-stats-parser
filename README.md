# ika-stats-parser
Statistics on wages and working conditions are crucial to understand economic and societal issues.  
IKA - EFKA release statistics on several issues monthly and with greater "resolution" biannually.
The official website is located in 
https://www.efka.gov.gr/el/miniaia-stoicheia-apascholeses-yearly
  
Unfortunately, released data not in a directly machine readable format, making further analysis difficult.
The scope if this script is to parse PDF realesed by IKA - EFKA and transcribe the data to a format suitably for furhere analysis.  
## how to use
python scripy read_IKA_7.py (tested with python3.7) reads an IKA statistics pdf, identifies the pages with a specific
table and prints the table in a csv form (semicolon delimited).  
The script searches for table IV.12 entitiled  
DISTRIBUTION OF INSURED POPULATION, AVERAGE EMPLOYMENT (DAYS), AVERAGE WAGE & AVERAGE MONTHLY MONETARY EARNIGS BY OCCUPATION & SEX
The script iterates over all pdf on the current directory and outputs a result.out file
The file is readily readable using any statistics software
Bear in mind that in ist current form the file is uncleaned.  
Empty and metadata rows are included  
> res<-read.csv(file="results.out",sep=";",comment.char="#",header=FALSE,stringsAsFactors = FALSE)%>% as_tibble()  
> res %>% filter(V3=="93") %>% select(V1,V2,V5,V6,V3,V17)  
A tibble: 33 x 6
   V1    V2    V5      V6     V3    V17       
   <chr> <chr> <chr>   <chr>  <chr> <chr>     
 1 2006  06    104.135 28.933 93    926,80    
 2 2007  06    109.645 37.635 93    942,24    
 3 2009  06    100.423 49.274 93    946,88    
 4 2010  06    126.779 86.937 93    1.070,92  
 5 2011  06    119.760 88.607 93    1.074,97  
 6 2012  06    76.777  28.615 93    877,81    
 7 2013  06    80.696  29.251 93    823,03    
 8 2014  06    90.646  29.694 93    770,54    
 9 2015  06    96.828  35.873 93    754,87    
10 2016  06    104.102 39.549 93    740,80   
  
## how it wors
   The script is basic and its function is more-or-less trivial.  
   The lines of the table are identified and used a a grid for placing text and numbers
   Fianally the grid is printed row-wise or column wise depending on the orientation
## ToDo
   * Clean output 
   * Clean Code
   * Implement parsing of Different tables
   
## Disclaimer
   The correctness of the parsed data is not throught tested. Use at your own risk.  
   The ownership of the data lies with IKA-EFKA. Use of the data might be subject to restrictions posed by IKA-EFKA. 
   The license explicitly DOES NOT hold for the dataset (result.out), which is not owned by the author
   
   
   
