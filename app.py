from flask import Flask, render_template,request,send_file,session
import os
import subprocess
import matplotlib.pyplot as plt

def csv_parser(line):
    linelist=[]
    j=0
    for i in line:
        if i==",":
            linelist.append(line[:j])
            break
        j+=1
    l=j+1
    for k in range(j+1,len(line)):
        if line[k]=='"' and line[k+1]=="," and line[k+2]=='"':
            linelist.append(line[l+1:k].strip())
            l=k+2
    if (line[len(line)-2])==',':
        linelist.append(line[l+1:len(line)-4].strip('\n'))
        linelist.append("")
        linelist.append("")
    else:
        linelist.append(line[l+1:len(line)].strip('"\n'))
    return linelist
        

app=Flask(__name__)
app.secret_key="oompa loompa"

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
        
        if ".log" not in file.filename:
            msg = "Please upload a log file"
            os.remove(path)
            return render_template('log_upload.html', message=msg)
        subprocess.run(['awk','-f','awking.awk', path], check=True) 
        if "log.csv" not in os.listdir("."):
            msg= "Please upload Apache log"
            os.remove(path)
            return render_template('log_upload.html',message=msg)
        session["uploadedFileName"]=file.filename[:-4]  
        msg = "Log file uploaded and processed successfully"
        yes = True
    # i=0
    # global yearlist
    # yearlist=[0]
    # monthno={"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}
    # global monthlist
    # monthlist=[]
    # with open("log.csv","r") as f:
    #     for line in f:
    #         line=csv_parser(line)
    #         dt=line[1]
    #         if i==0:
    #             i=1
    #         else:
    #             if int(dt[-5:-2])>yearlist[len(yearlist)-1]:
    #                 yearlist.append(int(dt[-5:-2]))
    #             if dt[4:7] in monthno.keys():
    #                 monthlist[dt[4:7]]=monthno[dt[4:7]]          
            
    return render_template('log_upload.html',message=msg,yes=yes)

@app.route('/display')
def display():
    i=0
    headList=None
    dataList=[]
    
    with open("log.csv","r") as f:    
        for line in f:
            if i==0:
                headList=line.split(',')
                i=1
            else:
                line=csv_parser(line)
                dataList.append(line)

    return render_template('log_display.html',headList=headList,dataList=dataList,tableName=session.get('uploadedFileName'))

@app.route('/download')
def download():
    return send_file('log.csv',as_attachment=True,download_name=session.get('uploadedFileName')+".csv")

@app.route('/graphs')
def graphs():
    error=0
    notice=0
    time={}
    times=[]
    noof=[]
    eventCount=[0,0,0,0,0,0]
    with open("log.csv","r") as f:
        a=0
        for line in f:
            line=csv_parser(line)
            if a==1:
                try:
                    time[line[1]]+=1
                except KeyError:
                    time[line[1]]=1

                if line[4]!='':
                    eventCount[int(line[4][1])-1]+=1
                if line[2]=='error':
                    error+=1
                else:
                    notice+=1
            a=1
    y=[error,notice]
    print(error,notice)
    plt.pie(y,labels=["error","notice"])
    plt.savefig('static/level_pie_chart.png')
    plt.figure()
    times=time.keys()
    noof=time.values()
    plt.plot(times,noof)
    plt.savefig('static/line_plot.png')
    plt.figure()
    events=[f"E{i}" for i in range(1,7)]
    plt.bar(events,eventCount,width=0.5)
    plt.savefig('static/bar.png')
    return render_template('graphs_plots.html')
    
if __name__ == "__main__":
    app.run(debug=True)
