import sys
import subprocess
import re
import fitz
from numpy import True_
import re
import spacy 
import json
from textblob import TextBlob
nlp = spacy.load('en_core_web_lg')
def convert_to(folder, source, timeout=None):
    args = [libreoffice_exec(), '--headless', '--convert-to', '.pdf', '--outdir', folder, source]

    process = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    filename = re.search('-> (.*?) using filter', process.stdout.decode())

    return filename.group(1)


def libreoffice_exec():
    # TODO: Provide support for more platforms
    if sys.platform == 'darwin':
        return '/Applications/LibreOffice.app/Contents/MacOS/soffice'
    return 'libreoffice'
def scrape(filePath):
    results = [] # list of tuples that store the information as (text, font size, font name)
    size = []
    fonts=[]
    combination=[]
    pdf = fitz.open(filePath) # filePath is a string that contains the path to the pdf
    for page in pdf:
        dict = page.get_text("dict")
        blocks = dict["blocks"]
        for block in blocks:
            if "lines" in block.keys():
                spans = block['lines']
                for span in spans:
                    data = span['spans']
                    for lines in data:
                      if len(lines['text'])>=2: 
                            results.append([lines['text'], lines['size'], lines['font']])
                            size.append(lines['size'])
                            fonts.append(lines['font'])
                            combination.append((lines['size'], lines['font']))

                            # lines['text'] -> string, lines['size'] -> font size, lines['font'] -> font name
    pdf.close()
    return results ,size,fonts,combination  
  def bold_data(data):
    data_bold=[]
    for d in data:
      if 'Bold' in d[2] or d[0].isupper() :
        if d[0]!=' ':
          data_bold.append(d)
    return data_bold    
  def bold_filter(data):
  keywords=['summary','work experience','phone number','contact','email','address','education','languages','projects','skills','achievements','details','links','hobbies']
  new=[]
  for d in data:
    for key in keywords:
      search = nlp(d[0].lower())
      main = nlp(key)
      if main.similarity(search)>0.5:
        if d in new:
          continue
        new.append(d)
  return new
def data_organizer(data,headers):
    dict_data=dict()
    for i in range(len(headers)):
      try:
          dict_data[headers[i][0]]=data[data.index(headers[i])+1:data.index(headers[i+1])]
      except IndexError:  
          dict_data[headers[i][0]]=data[data.index(headers[i])+1:-1]
    return dict_data
def size_structures(data,state):
    temp=0
    memory=''
    tree=dict()
    for d in data:
        sentence = re.sub(r"\s+", "", d[0], flags=re.UNICODE)
        if sentence!='':
            if d[1]>=temp:
              if state==True:
                if 'Bold' in d[2]:
                  memory=d[0]
                  temp=d[1]
                  tree[d[0]]=[]
                  
              else:  
                  memory=d[0]
                  temp=d[1]
                  tree[d[0]]=[]
            else:
              tree[memory].append(d[0]) 
    return tree
def bold_state(data):
  state=False
  for d in data :
    if 'Bold' in d[2]:
      state=True
      break
  return state       
#section content size seperation
def size_seperator(dict_data):
  for k,v in dict_data.items():
      dict_data[k]=size_structures(v,bold_state(v))
  return  dict_data   
def date_period(input_string):
      # a generator will be returned by the datefinder module. I'm typecasting it to a list. Please read the note of caution provided at the bottom.
      matches = list(datefinder.find_dates(input_string))

      if len(matches) > 0:
          # date returned will be a datetime.datetime object. here we are only using the first match.
          return matches
      else:
          return ('No dates found')
def discription(ents,text):
  for k,v in ents.items():
      text=text.replace(v,' ')
  return text
def entities(text):
    doc = nlp(text)
    counter=0
    entities=dict()
    for entity in doc.ents:
      entities[entity.label_+str(counter)]= entity.text
      counter+=1
    return   entities
 def dic_check(dict0):
  state=False
  for k,v in dict0.items():
    if len(v)>0:
      state=True
      break
  return  state  
def _correct(text):
        
      gfg = TextBlob(text)
      
      # using TextBlob.correct() method
      gfg = gfg.correct()
      return str(gfg)
def structured_entities_based(dict_data):
    title=[]
    dates=[]
    jsons=dict()
    for k,v in dict_data.items():
          loader=dict()
          state=dic_check(v)
          if state==True:
            
            for c,d in v.items():
              obj_data=dict()
              text=''.join(d)
              ents1=entities(c)
              ents2=entities(text)
              discriptions='no data'
              if  bool(ents2) :
                  discriptions=_correct(discription(ents2,str(text)))
              obj_data['title']=c
              obj_data['full_text']=text
              obj_data['entities']=[ents1,ents2]
              obj_data['discription']=discriptions
              loader[c]=obj_data
              
            jsons[k]=loader
            
          else:
            obj_data=dict()
            text=''.join(v.keys())
            ents=entities(text)
            discriptions='no data'
            if  bool(ents) :
                  discriptions=_correct(discription(ents,str(text)))
            obj_data['full_text']=text
            obj_data['entities']=ents
            obj_data['discription']=discriptions
            jsons[k]=obj_data
    return  jsons      
  import json
def file_extraction(path):
  try:
    data,size,fonts,combination=scrape(path)
  except:
    result=convert_to('TEMP Directory',  path, timeout=30)
    data,size,fonts,combination=scrape(result)
  headers=bold_filter(bold_data(data))
  dict_data=  data_organizer(data,headers)
  #json file based on text featrures
  json_text=dict_data
  with open("json_text.json","w") as f:
    json.dump(json_text,f)
  # json files with more structure based on size and font style 
  dict_data=size_seperator(dict_data)
  json_size_font=dict_data
  with open("json_size_font.json","w") as f:
    json.dump(json_size_font,f)
  #json file based on extracting section entities and descriptions
  dict_data= structured_entities_based(dict_data)
  with open("entities_data.json","w") as f:
    json.dump(dict_data,f)

