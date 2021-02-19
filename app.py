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
    
    DIR_PATH = os.path.dirname(os.path.realpath(__file__))
    if os.path.isdir(UPLOAD_FOLDER) is True:
        randomno=random.randint(1000,100000000)
        UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/uploads/'+str(randomno)+'/'

    os.makedirs(UPLOAD_FOLDER)  
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    # limit upload size upto 8mb
    #app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024
# import request
    if request.method == 'POST':
        pageno = request.form['page']
        uploaded_file = request.files['file']
        
        fp,lp=get_text(pageno)
        print(fp)
        print(lp)
        if lp==0:
            lp=fp
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        if uploaded_file.filename != '':
            filename = uploaded_file.filename
            uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            path=os.path.join(app.config['UPLOAD_FOLDER'], filename)
            pages = convert_from_path(path, 500,first_page=fp ,last_page=lp,poppler_path = r'C:\flaskenv\Lib\site-packages\poppler-21.02.0\Library\bin')
            image_counter = 1
            global texts
            
            for page in pages:
                filename='page_'+str(image_counter)+'.jpg'
                page.save(os.path.join(app.config['UPLOAD_FOLDER'], filename),'jpeg')
                image_counter+=1
            filelimit=image_counter-1
            for i in range (1,filelimit+1):
                filename = "page_"+str(i)+".jpg"
                text = str(((pytesseract.image_to_string(Image.open(os.path.join(app.config['UPLOAD_FOLDER'], filename)))))) 
                text = text.replace('-\n', ' ')
                texts+=text
            os.remove(path)
             
            
        return redirect(url_for('readingtext',texts=filename))
    else:
        return render_template('frontend.html')
@app.route('/reading',methods=['GET', 'POST'])
def readingtext():
    path=request.args['texts']
    print(texts)
    
    #shutil.rmtree(app.config['UPLOAD_FOLDER'])  
    return render_template('upload.html',texts=texts)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
