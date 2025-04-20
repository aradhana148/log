from flask import Flask, render_template,request,send_file,session,redirect
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

def DateTime(line):
    monthno={"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}
    return (int(line[1][-4:])*10000+int(monthno[line[1][4:7]])*100+int(line[1][8:10]) + 0.01*(int(line[1][-13:-11])+int(line[1][-10:-8])*0.01+int(line[1][-7:-5])*0.0001))

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
        i=0
        yearlist=[0]
        session["yearlist"]=yearlist

        monthno={}
        monthno={"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}
        session["monthlist"]=list(monthno.keys())

        stime=""
        etime=""
        sdate=""
        edate=""
        smon=""
        emon=""
        with open("log.csv","r") as f:
            for line in f:
                line=csv_parser(line)
                dt=line[1]
                if i==0:
                    i=1
                else:
                    if int(dt[-4:])>yearlist[len(yearlist)-1]:
                        yearlist.append(int(dt[-4:]))
                    if stime =="":
                        stime=dt[-12:-5]
                        sdate=dt[8:10]
                        smon=dt[4:7]
                        session["firstTime"]=stime
                        session["firstDate"]=sdate
                        session["firstMonth"]=smon
                etime=dt[-12:-5]
                edate=dt[8:10]
                emon=dt[4:7]

        session["lastTime"]=etime
        session["lastDate"]=edate
        session["lastMonth"]=emon
        yearlist.pop(0)
        print(yearlist)
        session["firstYear"]=yearlist[0]
        session["lastYear"]=yearlist[len(yearlist)-1]
    
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


@app.route('/graphs',methods=['GET','POST'])
def graphs():
    if request.method =='GET':
        return render_template('graphs_plots.html',yearlist=session.get('yearlist'),monthlist=session.get('monthlist'),firstTime=session.get('firstTime'),lastTime=session.get('lastTime'),lastDate=session.get('lastDate'),firstDate=session.get('firstDate'),firstMonth=session.get('firstMonth'),lastMonth=session.get('lastMonth'),firstYear=session.get('firstYear'),lastYear=session.get('lastYear'))
    if request.method == 'POST':
        monthno={"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}
        syear = int(request.form.get("syear"))
        smonth = int(monthno[request.form.get("smonth")])
        sdate=int(request.form.get("sdate"))
        stime = request.form.get("stime")
        stime=stime.split(":")
        stime=[int(i) for i in stime]
        stime=stime[0]+stime[1]*0.01+stime[2]*0.0001
        eyear = int(request.form.get("eyear"))
        emonth = int(monthno[request.form.get("emonth")])
        edate=int(request.form.get("edate"))
        etime = request.form.get("etime")
        etime=etime.split(":")
        etime=[int(i) for i in etime]
        etime=etime[0]+etime[1]*0.01+etime[2]*0.0001
    sDateTime=syear*10000+smonth*100+sdate+stime*0.01
    eDateTime=eyear*10000+emonth*100+edate+etime*0.01
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
 
                if DateTime(line)>=eDateTime:
                    break
                if sDateTime<=DateTime(line)<=eDateTime:
                    print("ooo")
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
    #print(error,notice)
    y=[error,notice]
    plt.figure()
    plt.pie(y,labels=["error","notice"])
    plt.savefig('static/level_pie.png')
    plt.clf()
    plt.figure()
    times=time.keys()
    noof=time.values()
    plt.plot(times,noof)
    plt.savefig('static/line_plot.png')
    plt.clf()
    plt.figure()
    events=[f"E{i}" for i in range(1,7)]
    plt.bar(events,eventCount,width=0.5)
    plt.savefig('static/bar.png')
   
    plt.clf()
    return render_template('graphs_plots.html',yearlist=session.get('yearlist'),monthlist=session.get('monthlist'),firstTime=session.get('firstTime'),lastTime=session.get('lastTime'),lastDate=session.get('lastDate'),firstDate=session.get('firstDate'),firstMonth=session.get('firstMonth'),lastMonth=session.get('lastMonth'),firstYear=session.get('firstYear'),lastYear=session.get('lastYear'))


    
if __name__ == "__main__":
    app.run(debug=True)
