#!/usr/bin/python3.7
# importing required modules
import fitz
import string
import numpy as np
import argparse
import re 
import sys

TABLE_LEN=3 #pages that the table spans
DEBUG_LINES=False #logical argument, to print lines on pdf for debugg
MATCH_WORDS=15
wfile=None

parser = argparse.ArgumentParser(description='File to parse.')
parser.add_argument("--file", help="Prints the supplied argument.", default="dokimi.pdf")
parser.add_argument("--ver",help="Prints all data",default=0)
parser.add_argument("--addLines",help="1 for adding Lines",default=0)
parser.add_argument("--conf",help="conf file ",default=None)
parser.add_argument("--debug",help="debug file",default="garbage.out")
parser.add_argument("--output",help="output file",default="data.out")

args = parser.parse_args()
pdf_file=args.file
add_lines=args.addLines
wfile=args.conf
debug=args.debug
output=args.output

sec2=["SΕCΤΙΟΝ ΙΙ:","ΤΜΗΜΑ ΙΙ:","Εnterprises with less than 10 employees"]
sec1=["SΕCΤΙΟΝ Ι:","ΤΜΗΜΑ Ι:","Εnterprises with 10 or more employees"]
sec0=["SΕCΤΙΟΝ 0:","ΤΜΗΜΑ 0:","Detailed statistics for Ιnsured"]


if add_lines=="1":
   DEBUG_LINES=True

file_debug=open(debug,"w")
file_output=open(output,"a")

result=re.search("([0-9][0-9])_(20[0-9][0-9])",pdf_file)
year=result.group(2)
month=result.group(1)
#find year and month from the file name, 
print("#",year,month,file=file_debug) #output to debug file

numerics="1234567890.,"
def IsNumber(string):
    for i in string:
        if i not in numerics:
             return False
    return True
#simple function to test if string is numeric or not
#usuall convention is . for thousand seperator and , for decimal


lower=None
upper=None
#bounds of pages to search for table

#Strings to Match and to avoid
strings_to_match=[]
strings_to_avoid=[]


#string to remove - noise
strings_to_remove=[]

checkwords=['ΠΛΗΡΗΣ', 'ΚΑΙ', 'ΜΕΡΙΚΗ', 'ΑΠΑΣΧΟΛΗΣΗ', 'ΚΑΤΑΝΟΜΗ', 'ΑΣΦΑΛΙΣΜΕΝΩΝ,', 'ΜΕΣΗΣ', 'ΑΠΑΣΧΟΛΗΣΗΣ', 'ΚΑΙ', 'ΜΕΣΟΥ', 'ΗΜΕΡΟΜΙΣΘΙΟΥ', 'ΑΝΑ', 'ΕΙΔΙΚΟΤΗΤΑ', 'ΚΑΙ', 'ΦΥΛΟ', 'ΤΑΒLΕ', 'ΙV.12']
#list of words to find page we seek
if( wfile is not None):
   f=open(wfile,"r")
   lines = [line.rstrip() for line in f]

   checkwords=[]
   for line in lines:
      if ( not line[0]=="#"):
           checkwords.append(line)
      if "NUMBER_OF_WORDS" in line:
           l=line.split()
           MATCH_WORDS=int(l[1])
      if "TABLE_LEN" in line:
           l=line.split()
           TABLE_LEN=int(l[1])
      if "EXACT_STRING_TO_MATCH" in line:
          string=line[23:]
          strings_to_match.append(string)
          match_strings=True
      if "PAGE_RANGE" in line:
          pp=line.split()
          lower=int(pp[1])
          upper=int(pp[2]) 
      if "EXACT_STRING_TO_AVOID" in line:
          string=line[23:]
          strings_to_avoid.append(string)
      if "#SECTION" in line:
          pp=line.split()
          section_of_table=pp[1].strip()
      if "STRING_TO_REMOVE" in line:
          TtC=line[18:]
          strings_to_remove.append(TtC)
        


def checkGraphs(page):
    #simply hack to check page. If there are "c" drawings,  it is probably a graph
    lines=page.get_drawings() #get all drawings
    ln=0
    rn=0
    cn=0
    qu=0
    for line in lines:
      obj=line["items"][0]     
      if(obj[0]=="c"):cn=cn+1
      if(obj[0]=="l"):ln=ln+1
      if(obj[0]=="re"):rn=rn+1
      if(obj[0]=="qu"):qu=qu+1
#      if not ( (obj[0]=="c" or obj[0]=="l" or obj[0]=="re")): print(obj)
    print("#Page has ",len(lines) ,"elements, ",rn,"rectangles,",ln,"lines, ",cn,"c and ",qu,"Quads",file=file_debug)
    if len(lines)==0 : return ("Text")
    if cn < 0.05*len(lines) : return ("Table")
    return ("Graph")



def clean_string(string):
    st=string
    for s in strings_to_remove:
        st=st.replace(s," ")
    return(st)



current_section=None
doc = fitz.open(args.file)
pf=None
NoP=0
scoreboard={}
section_score_mult=1
if(lower==None):
   lower=0
   upper=len(doc)

for page_i in range(0,len(doc)):
   
    ExactMatch=False
    page=doc[page_i]
    
    ans=checkGraphs(page)
    print("#page :",page_i,"is probably",ans,file=file_debug)
    if(ans=="Text"):mult=0
    if(ans=="Graph"):mult=0.5
    if(ans=="Table"):mult=1
    text_instances=page.get_text("blocks") #read all page test in block mode
    pgstr=""
    for inst in text_instances:

        string_to_parse=inst[4] #concat into large string
        string_to_parse=string_to_parse.translate(str.maketrans("ANBIEOPTYM","ΑΝΒΙΕΟΡΤΥΜ")) #change latin
        pgstr=pgstr+string_to_parse

    words=pgstr.split() 
    for string in sec2:
         if (string in pgstr) and (len(words)<30): 
                    #print ("#BEG of SEC2")
                    current_section="S2"
                    break
    for string in sec1:
         if (string in pgstr) and (len(words)<30): 
                    #print ("#BEG of SEC1")
                    current_section="S1"
                    break
    for string in sec0:
         if (string in pgstr) and (len(words)<30): 
                    #print ("#BEG of SEC0")
                    current_section="S0"
                    break    


    if (page_i<lower or page_i>upper):continue      # keep inside limits

    if (current_section is not None):
         section_score_mult=0.5
         if (section_of_table==current_section):
                section_score_mult=1
         #print("#SECTION test...: CS:",current_section," TS:",section_of_table," Mult:",section_score_mult)
    nw=0
    for w in checkwords:
       if w in words:
            nw=nw+1
    print("#",page_i,nw,end=" ",file=file_debug)
    eS=0
    if(match_strings):
        avoid=1.0
        for string in strings_to_match:
            if (string in pgstr): 
                eS=eS+1
        for string in strings_to_avoid:
          if (string in pgstr): 
              avoid=0
        

    if(match_strings):
        score=avoid*mult*(nw/MATCH_WORDS+eS/len(strings_to_match))
    else:
        score=mult*(nw/MATCH_WORDS)
    score=score*section_score_mult
    
    #attribute a score for wach page
    scoreboard[page_i]=(score,nw,eS,section_score_mult)      

print("#",scoreboard,file=file_debug)
score_max=0
pf=0
for i in scoreboard:
    sc=scoreboard[i]
    if(sc[0]>score_max):
         score_max=sc[0]
         pf=i
print("#best match is page",pf,"with score:",scoreboard[pf])
print ("In",pdf_file,"best match is",pf,"with score",score_max,file=sys.stderr)

if(pf==None):
    print ("In",pdffile,"#TABLE not Found",file=sys.stderr)
    quit()

#an more elaborate test should be added
#in current form page estimation always is true

HZL={}
VRL={} #empty dictionaries of Horizontal and Verical Lines

def add_line(x1,x2,y1,y2):
    #function to add line to dictionaries
    if (abs(x1-x2)<1):   # verical line, same x1,x2    
               hzx=x1
               if hzx not in HZL:   #if there is no line in HZX add one
                  HZL[hzx]=[(y1,y2)]
               else:
                  HZL[hzx].append((y1,y2)) #if there is, append the endpoints of the line in the list as tuple
    
    if (abs(y1-y2)<1):   #vertical line
               vr=y1
               if vr not in VRL: 
                  VRL[vr]=[(x1,x2)]
               else:
                  VRL[vr].append((x1,x2))
 
    if (abs(y1-y2)>=1 and abs(x1-x2)>=1):
       print("#Diagonal Line. Probably Error")
       return False
    return True
   
for page_i in range(pf,pf+TABLE_LEN): 

    HZL={}
    VRL={} #empty dictionaries of Horizontal and Verical Lines
   
    page=doc[page_i]
    
    lines=page.get_drawings() #get all drawings
    nr=0
    nl=0
    NoL=0
    for line in lines:
        
        obj=line["items"][0] 
        clr=line["color"] 
        fill=line["fill"]
        if (fill==(1.0,1.0,1.0)):
                   continue     #drop obj if it has a white filling. 
        if(obj[0]=="re"): #if object is rectagular
          nr=nr+1
          
          rect=obj[1]
          x0=rect.x0
          x1=rect.x1
          y0=rect.y0
          y1=rect.y1

          if(abs(x0-x1)<3): # case of a degenerate rectangular with very small width
               hzx=(x0+x1)/2 # 
               if(not add_line(hzx,hzx,y0,y1)):
                      #the addline func retruns false
                      #problem
                      print("#Location of problem : page",page,"on doc :",file)
                      quit()
         
          if(abs(y0-y1)<3):
               vr=(y0+y1)/2
               if( not add_line(x0,x1,vr,vr)):      
                      print("#Location of problem : page",page,"on doc :",file)
                      quit()
          #if True:#(abs(y0-y1)>=3 and abs(x0-x1)>=3):          
          #       add_line(x0,x0,y0,y1)
          #       add_line(x1,x1,y0,y1)
          #       add_line(x0,x1,y0,y0)
          #       add_line(x0,x1,y1,y1)
          #       NoL=NoL+4
                 #add four lines  



        if(obj[0]=="l"):  # second case, there is a line object.
           nl=nl+1
           P1=obj[1]
           P2=obj[2]
           x1=P1.x
           y1=P1.y
           x2=P2.x
           y2=P2.y
           
           if(abs(x1-x2)<0.01):
                if(not add_line(x1,x1,y1,y2)):
                   print("#Location of problem : page",page,"on doc :",file)
                   quit()
                NoL=NoL+1
           if(abs(y1-y2)<0.01):
                if(not add_line(x1,x2,y1,y1)):
                    print("#Location of problem : page",page,"on doc :",file)
                    quit()
                NoL=NoL+1
           
                
    if (DEBUG_LINES):     #part of code to write lines on pdf for debug.
        nol=0             #should go on different function
        for vs in VRL:
           #print(vs)
           for v in VRL[vs]:
              (xmin,xmax)=v
              shape=page.new_shape()
              shape.draw_line((xmin,vs),(xmax,vs))
              shape.finish(color=(1, 1, 0))
              shape.commit()   
              nol=nol+1
        for hz in HZL:
           #print(vs)
           for h in HZL[hz]:
              (ymin,ymax)=h
              shape=page.new_shape()
              shape.draw_line((hz,ymin),(hz,ymax))
              shape.finish(color=(1, 1, 0))
              shape.commit() 
              nol=nol+1
        print("NOL is ",nol,"******",NoL,file=file_debug)
        print("RE:",nr,"LI:",nl,file=file_debug)
    VRL_R={} # new dic with... clean lines..we treat parallel libes close to each other as a single line
     
    for v1 in VRL: 
       if VRL_R=={}:
          VRL_R[v1]=VRL[v1] #if reduced is empty, we fill it with the first entry. 
       found=False
       for v2 in VRL_R:  #we iterate over all elemetnts of the new dic
         if(v1==v2): continue
         if (abs(v1-v2)<2): #if there is a line close to the one checked
            VRL_R[v2]=VRL_R[v2]+VRL[v1] #we regard them as one line
            found=True
            continue
         
       if(found): continue #if a line already exists on VRL_R we do nothing
       VRL_R[v1]=VRL[v1]  #if not, we include line v along its enpoints in the new dic


    VRL=VRL_R
    vl=[]
    for v in VRL:
       
       vrl=VRL[v]
       xmin=1000
       xmax=0
       l=0

       for ls in vrl:
          (x1,x2)=ls
          l=l+(x2-x1)
          if(x1<xmin): xmin=x1
          if(x2>xmax): xmax=x2  #the pdf has line segments broken down to multiple line segments, leaving small holes
                                #we "glue" together all these to a large segment 
       vl.append(v)
  
       if (DEBUG_LINES ):
           shape=page.new_shape()
           shape.draw_line((xmin,v),(xmax,v))
           shape.finish(color=(1, 0, 0))
           shape.commit()
           
    HZL_R={}
    for h1 in HZL:              #same cleaning for HZ lines.
       if HZL_R=={}:            #a func could have been used
          HZL_R[h1]=HZL[h1]
       found=False
       for h2 in HZL_R:
         if(h1==h2): continue
         if (abs(h1-h2)<2):
            HZL_R[h2]=HZL_R[h2]+HZL[h1]
            found=True
            continue
         
       if(found): continue
       HZL_R[h1]=HZL[h1]

    HZL=HZL_R
    hl=[]
    for h in HZL:
       hzl=HZL[h]
       ymin=1000
       ymax=0
       l=0
       #print(vrl)
       for ls in hzl:
          (y1,y2)=ls
          l=l+(y2-y1)
          if(y1<ymin): ymin=y1
          if(y2>ymax): ymax=y2
        
       if(DEBUG_LINES ):
           shape=page.new_shape()
           shape.draw_line((h,ymin),(h,ymax)) 
           shape.finish(color=(1, 0, 0))
           shape.commit()
       hl.append(h)




    hl.sort() #the lines as sorted 
    vl.sort()
    
    col_n=len(hl)-1 #the number of rows and columns of the data grid is computed
    row_n=len(vl)-1 
    

    
    

    MAT={} #matrix for storing the text of the page
    
    text_instances=page.get_text("words",sort=True)
    #the text is broked down to words

    for inst in text_instances:
       
        string_to_parse=inst[4]
        x=0.5*(inst[0]+inst[2])
        y=0.5*(inst[1]+inst[3])
        text=inst[4] #the position of the word is estimated in the middle of the enclosing rectangular
        text=clean_string(text) #strings that need to be removed (conf.file) are removed
        xpos=None
        ypos=None

        for i in range(0,col_n):
            r=hl[i]
            l=hl[i+1]
            if (x>r) and (x<l):
                 xpos=i         #the x position is found
        for j in range(0,row_n):
            l=vl[j]
            u=vl[j+1]
            if (y>l) and (y<u):
                 ypos=j        #the y position
        
               
        #if the word is outside the grided matrix, either x or y will be None
        # in this version the end points are considered implicitly
        # that is, the segments are considered to span all the length of the paper
        # but only the words in the intersection of the segmets (ie were both x and y positions are not None are inside the grid
        if (not xpos==None) and (not ypos==None):
            pos=(xpos,ypos)
            if( pos in MAT):
                MAT[pos]=MAT[pos]+" "+text.strip()
            else:
                MAT[pos]=text.strip() 
    rowsv=[]
    colsv=[]
    drop=False
    #check if a row or a column is comletely empry, and drop
    # a completely empty row /column means spurious entry on the matrix
    for i in range(0,col_n):
      for j in range(0,row_n):
           pos=(i,j)
           if pos in MAT:
              colsv.append(i)
              drop=True
              continue
      if(drop):continue
 
    for j in range(0,row_n):
      for i in range(0,col_n):
           pos=(i,j)
           if pos in MAT:
              rowsv.append(j)
              drop=True
              continue
      if(drop):continue
 

    if page.rotation==90:   #some docs are rotated. Need to handle rotation
       for i in range(0,col_n):
          if not(i in colsv):continue
          print(year,month,sep=";",end=";",file=file_output)
          for j in range(0,row_n):
             if not(j in rowsv):continue
             pos=(i,row_n-j-1)
             st="NA"
             if pos in MAT: st=MAT[pos]
             print(st,end=";",file=file_output)
          print("",file=file_output)
    else:
     for i in range(0,row_n):
         if not(i in rowsv):continue
         print(year,month,sep=";",end=";",file=file_output)
         for j in range(0,col_n):
             if not (j in colsv):continue
             pos=(j,i)
             st="NA"
             if pos in MAT: st=MAT[pos]
             print(st,end=";",file=file_output)
         print("",file=file_output)

if(DEBUG_LINES):
   doc.save("LINES.pdf")

