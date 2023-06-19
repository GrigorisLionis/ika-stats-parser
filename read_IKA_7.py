#!/usr/bin/python3.7
# importing required modules
import fitz
import string
import numpy as np
import argparse
import re 
from sklearn.cluster import KMeans

parser = argparse.ArgumentParser(description='File to parse.')

parser.add_argument("--file", help="Prints the supplied argument.", default="dokimi.pdf")
parser.add_argument("--ver",help="Prints all data",default=0)
args = parser.parse_args()

pdffile=args.file
if(args.ver==0):
   verbose=False
else:
   verbose=True

verbose=True
result=re.search("([0-9][0-9])_(20[0-9][0-9])",pdffile)
year=result.group(2)
month=result.group(1)
if(verbose):
    print("#",year,month)
numerics="1234567890.,"
def IsNumber(string):
    count=0
    for i in string:
        if i in numerics:
           count=count+1
    if count==len(string):
       return True
    return False


checkwords=['ΠΛΗΡΗΣ', 'ΚΑΙ', 'ΜΕΡΙΚΗ', 'ΑΠΑΣΧΟΛΗΣΗ', 'ΚΑΤΑΝΟΜΗ', 'ΑΣΦΑΛΙΣΜΕΝΩΝ,', 'ΜΕΣΗΣ', 'ΑΠΑΣΧΟΛΗΣΗΣ', 'ΚΑΙ', 'ΜΕΣΟΥ', 'ΗΜΕΡΟΜΙΣΘΙΟΥ', 'ΑΝΑ', 'ΕΙΔΙΚΟΤΗΤΑ', 'ΚΑΙ', 'ΦΥΛΟ', 'ΤΑΒLΕ', 'ΙV.12']

doc = fitz.open(args.file)
pf=None
for page_i in range(0,len(doc)):
    fl1=0
    fl2=0
    fl3=1
    str1="DΙSΤRΙΒUΤΙΟΝ ΟF ΙΝSURΕD ΡΟΡULΑΤΙΟΝ"
    str2="ΟCCUΡΑΤΙΟΝ"
    str3="EARNINGS"
    page=doc[page_i]
    text_instances=page.get_text("blocks")
    pgstr=""
    for inst in text_instances:
        #print(inst)  
        string_to_parse=inst[4]
        string_to_parse=string_to_parse.translate(str.maketrans("ANBIEOPTYM","ΑΝΒΙΕΟΡΤΥΜ"))
        pgstr=pgstr+string_to_parse
#    print(pgstr)
    words=pgstr.split()
#    print(words)
    nw=0
    for w in checkwords:
       if w in words: nw=nw+1
    if (nw>15) or ('ΙV.12' in words):
      print("#",page,page_i,"FOUND PAGE")
      #print(words)
      pf=page_i







for page_i in range(pf,pf+3): #range(0,len(doc)):

    HZL={}
    VRL={}
    fl1=0
    fl2=0
    fl3=1
    page=doc[page_i]
    
    lines=page.get_drawings()
    for line in lines:
        
        #print(line["items"])
        obj=line["items"][0]
        if(obj[0]=="re"):
      
          
          rect=obj[1]
          x0=rect.x0
          x1=rect.x1
          y0=rect.y0
          y1=rect.y1
           #print(rect.x1,rect.y1,rect.x0,rect.y0)
          if(abs(x0-x1)<3):
               #print ("DEGEN, is VR Line at x=",(x0+x1)/2)
               hzx=(x0+x1)/2
               
                
               if hzx not in HZL: 
                  HZL[hzx]=[(y0,y1)]
               else:
                  HZL[hzx].append((y0,y1))


          if(abs(y0-y1)<3):
               #print ("DEGEN, is HR Line at y=",(y0+y1)/2)
               vr=(y0+y1)/2
               
                
               if vr not in VRL: 
                  VRL[vr]=[(x0,x1)]
               else:
                  VRL[vr].append((x0,x1))
          #print("NON DEG RECTANGLE")
           #must do all the work... haha 
                      
          hzx=x0
          if hzx not in HZL: 
              HZL[hzx]=[(y0,y1)]
          else:
             HZL[hzx].append((y0,y1)) 
          hzx=x1
          if hzx not in HZL: 
             HZL[hzx]=[(y0,y1)]
          else:
             HZL[hzx].append((y0,y1)) 
           
          vr=y0
          if vr not in VRL: 
             VRL[vr]=[(x0,x1)]
          else:
             VRL[vr].append((x0,x1))
          vr=y1
          if vr not in VRL: 
             VRL[vr]=[(x0,x1)]
          else:
             VRL[vr].append((x0,x1))



        if(obj[0]=="l"):
           #print(obj[1],"->",obj[2])
           P1=obj[1]
           P2=obj[2]
           x1=P1.x
           y1=P1.y
           x2=P2.x
           y2=P2.y
           if(x1==x2):
                hzx=x1
                
                if hzx not in HZL: 
                     HZL[hzx]=[(y1,y2)]
                else:
                     HZL[hzx].append((y1,y2))
           if(y1==y2):
                vr=y1
                
                if vr not in VRL: 
                     VRL[vr]=[(x1,x2)]
                else:
                     VRL[vr].append((x1,x2))

           #if(y1==y2): print ("VR Line from ",x1," to ",x2)
     
       
 
    VRL_R={}

    for v1 in VRL:
       if VRL_R=={}:
          VRL_R[v1]=VRL[v1]
       found=False
       for v2 in VRL_R:
         if(v1==v2): continue
         if (abs(v1-v2)<2):
            VRL_R[v2]=VRL_R[v2]+VRL[v1]
            found=True
            continue
         
       if(found): continue
       VRL_R[v1]=VRL[v1]


    VRL=VRL_R
    vl=[]
    for v in VRL:
       
       vrl=VRL[v]

       xmin=1000
       xmax=0
       l=0
       #print(vrl)
       for ls in vrl:
          
          (x1,x2)=ls
          l=l+(x2-x1)
          if(x1<xmin): xmin=x1
          if(x2>xmax): xmax=x2
       #print("VRLINE, at:",v," spanning from",xmin,xmax)
       shape=page.new_shape()

       shape.draw_line((xmin,v),(xmax,v))
       shape.finish(color=(1, 0, 0))
       shape.commit()
       vl.append(v)
    HZL_R={}

    for h1 in HZL:
       if HZL_R=={}:
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
        
       #print("HZL, at:",h," spanning from",ymin,ymax)
       shape=page.new_shape()
       shape.draw_line((h,ymin),(h,ymax)) 
       shape.finish(color=(1, 0, 0))
       shape.commit()
       hl.append(h)

    hl.sort()
    vl.sort()
    #print(hl)
    #print(vl)
    col_n=len(hl)-1
    row_n=len(vl)-1
    

    
    

    MAT={}
    
    text_instances=page.get_text("words",sort=True)
    #print("Rotation is :",page.rotation)
    #page.set_rotation(0)
    #print("Rotation is :",page.rotation)
    for inst in text_instances:
        #print(inst)  
        
        string_to_parse=inst[4]
        x=0.5*(inst[0]+inst[2])
        y=0.5*(inst[1]+inst[3])
        text=inst[4]
    
        xpos=None
        ypos=None

        for i in range(0,col_n):
            r=hl[i]
            l=hl[i+1]
            if (x>r) and (x<l):
                 #print("FOUND", x, "is on cell",i)
                 xpos=i
        for j in range(0,row_n):
            l=vl[j]
            u=vl[j+1]
            if (y>l) and (y<u):
                 #print("FOUND", y, "is on cell",j)
                 ypos=j
        
               
        #print(text,x,y,xpos,ypos)
        if (not xpos==None) and (not ypos==None):
            pos=(xpos,ypos)
            if( pos in MAT):
                MAT[pos]=MAT[pos]+" "+text.strip()
            else:
                MAT[pos]=text.strip() 
   # for m in MAT:
   #    print(m,MAT[m])
 
    if page.rotation==90:
       for i in range(0,col_n):
          print(year,month,sep=";",end=";")
          for j in range(0,row_n):
             pos=(i,row_n-j-1)
             st="NA"
             if pos in MAT: st=MAT[pos]
             print(st,end=";")
          print("")
    else:
     for i in range(0,row_n):
         print(year,month,sep=";",end=";")
         for j in range(0,col_n):
             pos=(j,i)
             st="NA"
             if pos in MAT: st=MAT[pos]
             print(st,end=";")
         print("")

doc.save("x.pdf")

