from flask import Flask, render_template, request, redirect, send_from_directory, flash, url_for
import random
from pipeline import run_external
import os
from werkzeug.utils import secure_filename
import json

ext = {'jpg','jpeg','png'}

app = Flask(__name__,
            static_url_path='',
            static_folder='./static',
            template_folder='templates')
app.config['UPLOAD_FOLDER'] = './static/inputs'
app.config['RESULT_FOLDER'] = './static/outputs'

@app.route('/inputs/<filename>')
def upload_img(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/outputs/<filename>')
def result_img(filename):
    return send_from_directory(app.config['RESULT_FOLDER'], filename)



@app.route("/upload")
def hello():
    num = random.randint(1000,9999)
    print(num)
    myvar = "hey"
    templateData = {
        'title': 'Hello World',
        'subtitle': myvar,
        'num':num
        }
    #run_external(num)
    return render_template('index.html',**templateData)

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        # Get the file from post request
        
        num = request.form.get('num')
        title = request.form.get('title')
        subtitle = request.form.get('subtitle')
        fgcol = request.form.get('fgcol')
        bgcol = request.form.get('bgcol')
        
        f = request.files['file']
        fn = str(num).zfill(4) + ".jpg"
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath,'static','inputs', fn)
        
        f.save(file_path)
        file_name=os.path.basename(file_path)
        run_external(num,title,subtitle,fgcol,bgcol)
        myvar = "hey"
        templateData = {
        'num' : str(num),
            'fpath': "inputs/"+str(num).zfill(4)+".jpg",
            'rpath': "outputs/"+str(num).zfill(4)+".svg",
            'mpath': "masks/"+str(num).zfill(4)+".png"
            }
        return render_template('result.html',**templateData)
    return ""

@app.route('/testpredict', methods=['GET', 'POST'])
def predicttest():
    # Get the file from post request
    num = 12
    templateData = {
        'num' : str(num),
        'fpath': "inputs/"+str(num).zfill(4)+".jpg",
        'rpath': "outputs/"+str(num).zfill(4)+".svg",
        'mpath': "masks/"+str(num).zfill(4)+".png"
        }
    return render_template('result.html',**templateData)

@app.route('/comp', methods=['GET'])
def comp():
    data = []
    for el in os.listdir('static/settings'):
        dp = json.load(open('static/settings/'+el))
        data.append(dp)
    data = sorted(data, key=lambda x: -x['timestamp'])
    templateData = {
        'data' : data
        }
    return render_template('comp.html',**templateData)

@app.route('/', methods=['GET'])
def home():
    return "hello"

@app.route('/delete/<num>', methods=['POST'])
def delete(num):
    basepath = os.path.dirname(__file__)
    os.remove(os.path.join(basepath,'static','settings',num+".json"))
    return redirect('/comp')


@app.route('/edit/<num>', methods=['GET'])
def edit(num):
    templateData = {
        'num' : str(num),
        'fpath': url_for('static', filename="inputs/"+str(num).zfill(4)+".jpg"),
        'rpath': url_for('static', filename="outputs/"+str(num).zfill(4)+".svg"),
        'mpath': url_for('static', filename="masks/"+str(num).zfill(4)+".png")
        }
    return render_template('result.html',**templateData)

if __name__ == '__main__':
        app.run(debug=True, host="localhost", port=8080)