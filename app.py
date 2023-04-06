from flask import Flask, render_template, request, redirect, send_from_directory, flash, url_for
import random
from pipeline import run_external
import os
from werkzeug.utils import secure_filename
import json
from google.cloud import storage
from PIL import Image
from io import BytesIO
import datetime
import uuid

ext = {'jpg','jpeg','png'}
project_name = "tagebuchbucket"
url_prefix = f"https://storage.googleapis.com/{project_name}/static"

basepath = os.path.join(os.path.dirname(__file__),'static')
if not os.path.exists(basepath):
    os.mkdir(basepath)
paths = ['inputs','outputs','masks','tmp']
for name in paths:
    if not os.path.exists(os.path.join(basepath,name)):
        os.mkdir(os.path.join(basepath,name))

def read_image(filename):
    storage_client = storage.Client()
    bucket = storage_client.bucket(project_name)
    blob = bucket.blob(filename)
    img = Image.open(BytesIO(blob.download_as_bytes()))
    return img

def read_settings():
    storage_client = storage.Client()
    bucket = storage_client.bucket(project_name)
    blob = bucket.blob("settings.json")
    data = json.loads(blob.download_as_string(client=None))
    return data

def update_settings(data):
    storage_client = storage.Client()
    bucket = storage_client.bucket(project_name)
    blob = bucket.blob("settings.json")
    blob.upload_from_string(json.dumps(data))

def upload_image(filepath, path, filename):
    try:
        client = storage.Client()
        bucket = client.bucket(project_name)
        bucket.blob(path+filename).upload_from_filename(filepath)
        return True
    except Exception as e:
        print(e)
    return False

def upload_svg(data, path, filename):
    try:
        client = storage.Client()
        bucket = client.bucket(project_name)
        bucket.blob(path+filename).upload_from_string(data,content_type="image/svg+xml")
        return True
    except Exception as e:
        print(e)
    return False

app = Flask(__name__,
            static_url_path='/static',
            static_folder='static',
            template_folder='templates')
app.config['UPLOAD_FOLDER'] = '/app/static/inputs'
app.config['RESULT_FOLDER'] = '/app/static/outputs'

@app.route("/upload")
def hello():
    obj_id = uuid.uuid1()
    myvar = "hey"
    templateData = {
        'title': 'Hello World',
        'subtitle': myvar,
        'num':obj_id
        }
    #run_external(obj_id)
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
        fn = 'tmpx.jpg'#str(num).zfill(4) + ".jpg"
        cfn = str(num).zfill(4) + ".jpg"
        svg_fn = str(num).zfill(4) + ".svg"
        basepath = './static'
        file_path = os.path.join(
            basepath,'inputs', fn)
        f.save(file_path)

        success = upload_image(file_path,"static/uploads/",cfn)
        if not success:
            print("upload failed!!")
        output_svg,settings_data = run_external(basepath,num,title,subtitle,fgcol,bgcol)
        success = upload_svg(output_svg,"static/results/",svg_fn)

        #update settings
        data = read_settings()
        data.append(settings_data)
        update_settings(data)

        templateData = {
            'num' : str(num),
            'fpath': str(num).zfill(4)+".jpg",
            'rpath': str(num).zfill(4)+".svg",
            'mpath': str(num).zfill(4)+".png",
            'prefix': url_prefix
            }
        return render_template('result.html',**templateData)
    return ""

@app.route('/', methods=['GET'])
def comp():
    data = read_settings()
    data = sorted(data, key=lambda x: -x['timestamp'])
    templateData = {
        'data' : data[:10],
        'prefix': url_prefix
        }
    return render_template('comp.html',**templateData)

@app.route('/test', methods=['GET'])
def home():
    return "hello from flask 2: "


@app.route('/delete/<num>', methods=['POST','GET'])
def delete(num):
    data = read_settings()
    res = [el for el in data if not (str(el['id']) == num)]
    update_settings(res)
    return redirect('/')