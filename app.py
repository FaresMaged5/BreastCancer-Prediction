from flask import Flask, request, redirect, url_for, render_template
from flask import Flask, redirect, render_template, session, request
from werkzeug.utils import secure_filename
from functools import wraps
from pymongo import MongoClient
from pprint import pprint
from keras.preprocessing.image import ImageDataGenerator
from keras.models import load_model
import pymongo
import os
import keras


print("Loading model")
global model
# model = load_model('/Users/faresmaged/Documents/Model_Website/Models/DenseNet121.h5')
IMG_SIZE = 100

app = Flask(__name__)
app.secret_key = b'%7\x8c\nQ\x10\xf5O\xe0\xda5bYRC\x08'

# Database
client = pymongo.MongoClient("mongodb+srv://Fares:BCPS@cluster0.nqntv.mongodb.net/?retryWrites=true&w=majority")
db = client.breast_cancer_login

#Decorators
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect('/')
    return wrap


# Routes
from user import routes

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login/')
def login():
    return render_template('login.html')

@app.route('/register/')
def register():
    return render_template('register.html')

@app.route('/about/')
def about():
    return render_template('about.html')

@app.route('/dashboard/')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/userprofile/')
@login_required
def userprofile():
    return render_template('userprofile.html')

@app.route('/appointment/')
def appointment():
    return render_template('appointment.html')

@app.route('/predictnow/', methods=['GET', 'POST'])
@login_required
def main_page():
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(os.path.join('uploads/prediction', filename))
        return redirect(url_for('prediction', filename=filename))
    return render_template('predictnow.html')

@app.route('/prediction/<filename>')
@login_required
def prediction(filename):
    #Step 1
    path = os.path.join('uploads/prediction', filename)
    pathnew = os.path.abspath('uploads')

    #Load model
    model = keras.models.load_model('Model/DenseNet121_master.h5')

    #Input preprocessing
    dgen_test = keras.preprocessing.image.ImageDataGenerator(rescale=1. / 255)

    test_img = dgen_test.flow_from_directory(
        directory=pathnew,
        target_size=(100, 100),
        color_mode="rgb",
        batch_size=1,
        class_mode=None,
    )
    
    #Classify image
    regression = model.predict( test_img )
    prediction = regression.argmax(axis=-1)
    # classification = prediction

    if prediction == [1]:
        predictions = "Malignant"
    else:
        predictions="Benign"

    # predictions = {
    # "class1": prediction

    # }

    # print(classification)
    print(prediction)
    print(regression)
    print(predictions)
    os.remove(path)

    return render_template('prediction.html', predictions=predictions)

if __name__=='__main__':
    app.run(host="0.0.0.0", port=5000 )


