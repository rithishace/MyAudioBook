#fitz and tesseract
# Importing the necessary Libraries
from flask_cors import cross_origin
from flask import Flask, render_template, request, redirect, url_for

import fitz
from PIL import Image 
import pytesseract 
import sys 
 
import os 
import random
import shutil

ALLOWED_EXTENSIONS = {'jpg'}
app = Flask(__name__, static_url_path="/static")
texts=''
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    print(DIR_PATH)
    if os.path.isdir(UPLOAD_FOLDER) is True:
        randomno=random.randint(1000,100000000)
        UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/uploads/'+str(randomno)+'/'

    os.makedirs(UPLOAD_FOLDER)  
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    
# import request
    if request.method == 'POST':
        pageno = request.form['page']
        uploaded_file = request.files['file']
        
        fp,lp=get_text(pageno)
        print(fp)
        print(lp)
        
        
        if uploaded_file.filename != '':
            filename = uploaded_file.filename
            uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            path=os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            global texts
            
            doc = fitz.open(path)
            k=1
            # If user wants to read a single page
            if lp == 0:
                page = doc.loadPage(fp-1) #number of page
                zoom_x = 2.0
               
                zoom_y = 2.0
                mat = fitz.Matrix(zoom_x,zoom_y)
                pix = page.getPixmap(matrix=mat)
                output = os.path.join(app.config['UPLOAD_FOLDER'], "image_to_read.jpg")
                pix.writeImage(output,"jpeg")
                
            # If user wants to read range of pages
            else:
                for i in range(fp-1,lp):
                    page = doc.loadPage(i) #number of page
                    zoom_x = 2.0
                    zoom_y = 2.0
                    
                    mat = fitz.Matrix(zoom_x,zoom_y)
                    pix = page.getPixmap(matrix=mat)
                    output = os.path.join(app.config['UPLOAD_FOLDER'], "image_"+str(k)+"_to_read.jpg")
                    pix.writeImage(output,"jpeg")
                    k+=1
            mytext = []
            dd= DIR_PATH+'/Tesseract-OCR/tesseract.exe'
            print(dd)
            pytesseract.pytesseract.tesseract_cmd =dd
            for file in os.listdir(os.path.join(app.config['UPLOAD_FOLDER'])):   
                if allowed_file(file):

                    data = pytesseract.image_to_string(Image.open(os.path.join(app.config['UPLOAD_FOLDER'],file)))
                    data = data.replace("|","I") # For some reason the image to text translation would put | instead of the letter I. So we replace | with I
                    data = data.split('\n')
                    mytext.append(data)

            
            # Here we make sure that the text is read correctly and we read it line by line. Because sometimes, text would end abruptly
            
            
            for text in mytext:
                for line in text:
                    line = line.strip()
                    # If line is small, ignore it
                    if len(line.split(" ")) < 10 and len(line.split(" "))>0:
                        texts= texts + " " + str(line) + "\n"

                    elif len(line.split(" "))<2:
                        pass
                    else:
                        if line[-1]!=".":
                            texts = texts + " " + str(line)
                        else:
                            texts = texts + " " + line + "\n"
            
            #shutil.rmtree(app.config['UPLOAD_FOLDER']) 
             
            
        return redirect(url_for('readingtext',texts=filename))
    else:
        return render_template('frontend.html')
@app.route('/reading',methods=['GET', 'POST'])
def readingtext():
    path=request.args['texts']
    print(texts)
    
    shutil.rmtree(app.config['UPLOAD_FOLDER'])  
    return render_template('upload.html',texts=texts)

if __name__ == "__main__":
    app.run( debug=True)
