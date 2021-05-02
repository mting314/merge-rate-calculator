import os
from flask import Flask, flash, request, redirect, render_template, session, send_file, make_response
# from flask_session import Session
from werkzeug.utils import secure_filename
import pandas as pd
from io import StringIO, BytesIO
from dotenv import load_dotenv


from calculations import calculate_merge_rate, path_leaf


load_dotenv();

app = Flask(__name__)

# Set the secret key to some random bytes and keep it secret.
# A secret key is needed in order to use sessions.
app.secret_key = b"_j'yXdW7.63}}b7"
UPLOAD_FOLDER = 'processed_data'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}


ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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


            merge_rate, missing_my_fips, actual_merge_error = calculate_merge_rate(df, cityname=cityname)

            attachment_filename = "{0}_{2}{1}".format(*os.path.splitext(filename) + ("missing_my_fips",))
            session["missing_my_fips_filepath"] = os.path.join(app.config['UPLOAD_FOLDER'], attachment_filename)

            # save df to disk, retrieve with download button
            missing_my_fips.to_csv(session["missing_my_fips_filepath"])

            return render_template("base.html", merge_rate=merge_rate,
                missing_my_fips   =[missing_my_fips.head(100).to_html(classes='data', header="true")],
                actual_merge_error=[actual_merge_error.head(100).to_html(classes='data', header="true")],
            )
    return render_template("base.html", merge_rate=None, missing_my_fips=None, actual_merge_error=None)


@app.route("/download_missing_my_fips", methods=["POST"])
def download_missing_my_fips():
    df = pd.read_csv(session["missing_my_fips_filepath"])
    os.remove(session["missing_my_fips_filepath"])

    filename = path_leaf(session["missing_my_fips_filepath"])

    resp = make_response(df.to_csv(index=False))
    resp.headers["Content-Disposition"] = f"attachment; filename={filename}"
    resp.headers["Content-Type"] = "text/csv"
    return resp

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