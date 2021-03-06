
#usinf teseract and poppler
# Importing the necessary Libraries
from flask_cors import cross_origin
from flask import Flask, render_template, request, redirect, url_for
#from main import text_to_speech


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
            lp=fp+1
        pop_path= DIR_PATH+'/poppler-21.02.0/Library/bin'
        pytesseract.pytesseract.tesseract_cmd =  DIR_PATH+'/Tesseract-OCR/tesseract.exe'
        if uploaded_file.filename != '':
            filename = uploaded_file.filename
            uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            path=os.path.join(app.config['UPLOAD_FOLDER'], filename)
            pages = convert_from_path(path, 500,first_page=fp ,last_page=lp,poppler_path =pop_path)
            image_counter = 1
            global texts
            texts=''
            mytext=[]
            for page in pages:
                filename='page_'+str(image_counter)+'.jpg'
                page.save(os.path.join(app.config['UPLOAD_FOLDER'], filename),'jpeg')
                image_counter+=1
            filelimit=image_counter-1
            for i in range (1,filelimit+1):
                filename = "page_"+str(i)+".jpg"
                text = str(((pytesseract.image_to_string(Image.open(os.path.join(app.config['UPLOAD_FOLDER'], filename)))))) 
                text= text.replace("|","I") # For some reason the image to text translation would put | instead of the letter I. So we replace | with I
                text = text.split('\n')
                mytext.append(text)
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
            
            #os.remove(path)
            shutil.rmtree(app.config['UPLOAD_FOLDER']) 
             
            
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
    app.run( debug=True)
