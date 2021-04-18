#using pdf reader 
# Importing the necessary Libraries
from flask_cors import cross_origin
from flask import Flask, render_template, request, redirect, url_for
#from main import text_to_speech

import PyPDF2
from PIL import Image 
import pytesseract 
import sys 
from pdf2image import convert_from_path 
import os 
import random
import shutil


app = Flask(__name__, static_url_path="/static")
texts=''

def get_text(value):
        
    string = value
    string = string.strip()
    if "-" in string:
        first_page_number = int(string.split("-")[0])
        last_page_number = int(string.split("-")[1])
    else:
        first_page_number = int(string)
        last_page_number = 0
            
    return first_page_number,last_page_number
@app.route('/', methods=['POST', 'GET'])
@cross_origin()
def homepage():
    randomno=random.randint(1000,100000000)
    UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/uploads/'+str(randomno)+'/'
    
    DIR_PATH = os.path.dirname(os.path.abspath(__file__))
    if os.path.isdir(UPLOAD_FOLDER) is True:
        randomno=random.randint(1000,100000000)
        UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/uploads/'+str(randomno)+'/'

    os.makedirs(UPLOAD_FOLDER)  
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    # limit upload size upto 8mb
    #app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024
# import request
    if request.method == 'POST':
        no = request.form['page']
        uploaded_file = request.files['file']
        
        fp,lp=get_text(no)
        
        if lp == 0:
            lp=fp+1
        
        if uploaded_file.filename != '':
            filename = uploaded_file.filename
            uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            path=os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            global texts
            
            pfo = open(path,'rb')
            pdfReader= PyPDF2.PdfFileReader(pfo)
            pageno=pdfReader.getNumPages()
            
            print(fp)
            print(lp)   
            if pageno <lp :
                lp=pageno               
            for i in range(fp,lp):
                
                pobj=pdfReader.getPage(i)
                text=pobj.extractText()
                print(text)
                texts=texts+'  '+text
                
            
            pfo.close()
            #os.remove(path)
            #shutil.rmtree(app.config['UPLOAD_FOLDER']) 
             
            
        return redirect(url_for('readingtext'))
    else:
        return render_template('frontend.html')
@app.route('/reading')
def readingtext():

   
    print(texts)
    
    shutil.rmtree(app.config['UPLOAD_FOLDER'])  
    return render_template('upload.html',texts=texts)

if __name__ == "__main__":
    app.run( debug=True)
