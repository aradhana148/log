from flask import Flask, render_template,request
import os
import subprocess


app=Flask(__name__)

UPLOADFOLDER = "uploads"
os.makedirs(UPLOADFOLDER,mode=0o777, exist_ok=True)
@app.route('/',methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file=request.files['logfile']
        file.save(file.filename)
        os.rename(file.filename, UPLOADFOLDER+'/'+file.filename)  
        subprocess.run(['bash','awking.sh', UPLOADFOLDER+'/'+file.filename], check=True)   
    return render_template('log_upload.html')

if __name__ == "__main__":
    app.run(debug=True)
