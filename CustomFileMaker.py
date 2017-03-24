'''
Created on Jan 24, 2017

@author: Rob

Convert the corpus from the NITF v3.3 XML standard into text files which contain
the article title on the first line, date of publication on the second line, and the text of
the article on the third and subsequent lines of the file.  

The NITF standard includes large amounts of meta-data for each document, but the LDA
analysis only requires a "bag of words" representation of the documents. This module
thus has the added benefit of reducing the memory space occupied by the corpus. The 
documents are sufficiently compressed that the LDA can be performed on a laptop computer.
'''
import os
import codecs
import re
import xml.etree.ElementTree as ET

def incr(curr_num):
  next_num = str(int(curr_num) + 1)
  padding = 7 - len(next_num)
  return("0"*padding + next_num)

years = range(1987, 2008)
months = range(1, 13)
days_of_month = [None, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

write_stub = r'C:\Users\Rob\Desktop\Perry Thesis\nyt_corpus_LDC2008T19\nyt_corpus\iranarticles' + "\\"
stub1 = r'C:\Users\Rob\Desktop\Perry Thesis\nyt_corpus_LDC2008T19\nyt_corpus\data'

doc_tuple_list = [] # of form (title, date, text)
curr_doc_num = "0000000"

# Loop through documents and extract (title, date, article text) tuples
for year in years:
  print("Beginning " + str(year))
  if year % 4 == 0:
    days_of_month[2] = 29
  else:
    days_of_month[2] = 28
  
  if year == 2007:
    months = range(1, 7)
    days_of_month[6] = 19
    
  stub2 = stub1 + "\\" + str(year)
  for month in months:
    if month < 10:
      stub3 = stub2 + "\\" + str(0) + str(month)
    else:
      stub3 = stub2 + "\\" + str(month)
      
    for day in range(1, days_of_month[month] + 1):
      if day < 10:
        mydir = stub3 + "\\" + str(0) + str(day)
      else:
        mydir = stub3 + "\\" + str(day)
        
      file_list = os.listdir(mydir)
      
      for doc_name in file_list:
        date = str(month) + "/" + str(day) + "/" + str(year)
        title = "miss"
        text = ""
        line_length = 0
        address = mydir + "\\" + doc_name
        tree = ET.parse(address)
        root = tree.getroot()
        for elem in root.iter():
          tag = elem.tag
          if tag == "title" and elem.text != None:
            title = elem.text
          if tag == "p" and elem.text != None:
            if line_length < 100:
              text = text + " " + re.sub("[0-9]", '', elem.text)
              line_length += len(elem.text)
            else:
              text = text + '\n' + re.sub("[0-9]", '', elem.text)
              line_length = 0
        doc_tuple = (title, date, text)
        
        # Extract only articles which contain "Iran" in their title or text
        title_match = re.search('(Iran)|(iran)', doc_tuple[0])
        text_match = re.search('(Iran)|(iran)', doc_tuple[2])
        title_find = None
        text_find = None
        if title_match != None:
          title_find = title_match.group(0)
        if text_match != None:
          text_find = text_match.group(0)  
        if title_find != None or text_find != None:
            doc_tuple_list.append(doc_tuple)
  # Write (title, date, article) tuples to files which will be read by LDA module    
  for doc in doc_tuple_list:
    try:
      tfile = open(write_stub + curr_doc_num + ".txt", 'w')
      tfile.write(codecs.encode(doc[0], 'utf-8'))
      tfile.write('\n')
      tfile.write(codecs.encode(doc[1], 'utf-8'))
      tfile.write('\n')
      tfile.write(codecs.encode(doc[2], 'utf-8'))
      tfile.write('\n')
      curr_doc_num = incr(curr_doc_num)
    finally:
      tfile.close()
  doc_tuple_list = []
  
  