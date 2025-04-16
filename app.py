from flask import Flask, render_template,flash,request
import os
import subprocess


app=Flask(__name__)

UPLOADFOLDER = "uploads"
os.makedirs(UPLOADFOLDER,mode=0o777, exist_ok=True)
LOGFOLDER = "logs"
os.makedirs(LOGFOLDER,mode=0o777, exist_ok=True)
@app.route('/',methods=['GET', 'POST'])
def upload():
    msg=""
    yes = False
    if request.method == 'POST':
        file=request.files['logfile']
        path=os.path.join(UPLOADFOLDER, file.filename)
        file.save(path)
        #os.rename(file.filename, UPLOADFOLDER+'/'+file.filename)
        if ".log" not in file.filename:
            msg = "Please upload a log file"
            os.remove(path)
            return render_template('log_upload.html', message=msg)
        subprocess.run(['awk','-f','awking.awk', path], check=True)   
        msg = "Log file uploaded and processed successfully"
        yes = True
        filename = file.filename[:-4]+".csv"
        os.path.join(LOGFOLDER, filename)
    return render_template('log_upload.html',message=msg,yes=yes)

@app.route('/display')
def display():
    files = os.listdir(LOGFOLDER)
    print(files)
    for file in files:
        with open(LOGFOLDER+'/'+file, 'r') as f:
            for line in f:
                line = line.strip()
                line = line.split(',')
                print(line)
                

    return render_template('log_display.html', files=files)

if __name__ == "__main__":
    app.run(debug=True)
