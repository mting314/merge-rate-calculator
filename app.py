import os
from flask import Flask, flash, request, redirect, url_for, render_template
# from flask_session import Session
from werkzeug.utils import secure_filename
import pandas as pd
from io import StringIO
from dotenv import load_dotenv

from calculations import calculate_merge_rate


load_dotenv();

app = Flask(__name__)

# ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @app.route('/')
# def index():
#     return f'<h2>Hi' \
#            f'<small><a href="/sign_out">[sign out]<a/></small></h2>' \
#            f'<a href="/playlists">my playlists</a> | ' \
#            f'<a href="/currently_playing">currently playing</a> | ' \
# 		   f'<a href="/current_user">me</a>' \

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            s=str(file.read(),'utf-8')

            data = StringIO(s) 

            df=pd.read_csv(data)

            # guess cityname
            cityname = filename[:filename.find("_Dispatch")]


            merge_rate = calculate_merge_rate(df, cityname=cityname)
            return render_template("base.html", merge_rate=merge_rate)
    return render_template("base.html", merge_rate=None)


'''
Following lines allow application to be run more conveniently with
`python app.py` (Make sure you're using python3)
(Also includes directive to leverage pythons threading capacity.)
'''
if __name__ == '__main__':
    # app.run(threaded=True,debug=True, port=int(os.environ.get("PORT",
    #                                                os.environ.get("SPOTIPY_REDIRECT_URI", "8080").split(":")[-1])))
    app.run(threaded=True,debug=True, port=int(os.environ.get("PORT",
                                                os.environ.get("SPOTIPY_REDIRECT_URI", "8080").split(":")[-1])))