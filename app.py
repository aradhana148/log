from flask import Flask, render_template,request,send_file,session
import os
import subprocess
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

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

def ConvertInputEventId(event):
    if event==None:
        return None
    comma=event.split(',')
    eventlist=[]
    for i in comma:
        if '-' not in i:
            eventlist.append(i)
        if '-' in i:
            toexpand=i.split('-')
            for j in range(int(toexpand[0][1]),int(toexpand[1][1])+1):
                eventlist.append("E"+str(j))
    return eventlist

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
        session['yearlist1']=yearlist[1:]
        session['yearlist2']=yearlist[:len(yearlist)-1]
        a=list(monthno.keys())
        b=list(monthno.keys())
        a.pop(monthno[smon]-1)
        b.pop(monthno[emon]-1)
        session['monthlist1']=a
        session['monthlist2']=b
        #print(yearlist)
        session["firstYear"]=yearlist[0]
        session["lastYear"]=yearlist[len(yearlist)-1]
    
    return render_template('log_upload.html',message=msg,yes=yes)

            
@app.route('/display',methods=['GET','POST'])
def display():
    i=0
    headList=None
    dataList=[]
    LevelsList=["all","notice","error"]
    EventIdsList=[("E"+str(i)) for i in range(1,7)]
    EventIdsList=["all"]+EventIdsList
    session["levelsList"]=LevelsList
    session["eventIdsList"]=EventIdsList
    level=request.form.get("level")
    if level=="all":
        session["selectedLevel"]="notice,error"
    else:
        session["selectedLevel"]=level
    eventId=request.form.get("eventid")
    session["selectedEventId"]=eventId
    eventId=ConvertInputEventId(eventId)
    with open("filtered_log.csv","w") as ff:
        with open("log.csv","r") as f:  
            for line in f:
                if i==0:
                    ff.write(line)
                    headList=line.split(',')
                    i=1
                else:
                    linep=csv_parser(line)
                    if (level=="all" or level==linep[2]) and (linep[4] in eventId):
                        dataList.append(linep)
                        ff.write(line)

    return render_template('log_display.html',headList=headList,dataList=dataList,tableName=session.get('uploadedFileName'),levelsList=session.get('levelsList'),eventIdsList=session.get('eventIdsList'),selectedLevel=session.get('selectedLevel'),selectedEventId=session.get('selectedEventId'))


@app.route('/download')
def download():
    return send_file('log.csv',as_attachment=True,download_name=session.get('uploadedFileName')+".csv")

@app.route('/downloadFilter')
def downloadFilter():
    return send_file('filtered_log.csv',as_attachment=True)

@app.route('/graphs',methods=['GET','POST'])
def graphs():
    if request.method =='GET':
        return render_template('graphs_plots.html',yearlist1=session.get('yearlist1'),monthlist1=session.get('monthlist1'),yearlist2=session.get('yearlist2'),monthlist2=session.get('monthlist2'),firstTime=session.get('firstTime'),lastTime=session.get('lastTime'),lastDate=session.get('lastDate'),firstDate=session.get('firstDate'),firstMonth=session.get('firstMonth'),lastMonth=session.get('lastMonth'),firstYear=session.get('firstYear'),lastYear=session.get('lastYear'))
    if request.method == 'POST':
        displayyes=True
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
    displyFrom=request.form.get("smonth")+" "+str(sdate)+" "+request.form.get("stime")+" "+str(syear)
    displayTo=request.form.get("emonth")+" "+str(edate)+" "+request.form.get("etime")+" "+str(eyear)
    
    session['displayFrom']=displyFrom
    session['displayTo']=displayTo
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
                if sDateTime>eDateTime:
                    return render_template('graphs_plots.html',yearlist1=session.get('yearlist1'),monthlist1=session.get('monthlist1'),yearlist2=session.get('yearlist2'),monthlist2=session.get('monthlist2'),firstTime=session.get('firstTime'),lastTime=session.get('lastTime'),lastDate=session.get('lastDate'),firstDate=session.get('firstDate'),firstMonth=session.get('firstMonth'),lastMonth=session.get('lastMonth'),firstYear=session.get('firstYear'),lastYear=session.get('lastYear'),msg=True)
                if DateTime(line)>eDateTime:
                    break
                if sDateTime<=DateTime(line)<=eDateTime:
                    #print("ooo")
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
    downasList=[".png",".jpeg",".pdf"]
    plt.figure(figsize=(19,12))
    times=time.keys()
    times=list(times)
    #print(times)
    noof=time.values()
    plt.plot(times,noof)
    if len(times)>20:
        arr=np.linspace(0,len(times)-1,20)
        arr=list(arr)
        arr=[int(i) for i in arr]
        #print(arr)
        xticks=[times[i][4:] for i in arr]
        #print(xticks)
        plt.xticks(arr,xticks,rotation=45,ha='right')
    if 6<=len(times)<=20:
        xticks=[times[i][4:] for i in range(0,len(times))]
        arr=[i for i in range(0,len(times))]
        plt.xticks(arr,xticks,rotation=45,ha='right')
    for i in range(3):
        plotname="events_vs_time"+downasList[i]
        plotPath=os.path.join("static",plotname)
        plt.savefig(plotPath)
    plt.clf()

    y=[error,notice]
    labels=["error","notice"]
    plt.figure()
    plt.pie(y,labels=labels)
    plt.title("Log level")
    plt.legend(labels,loc="upper right")
    for i in range(3):
        plotname="level_state_distribution"+downasList[i]
        plotPath=os.path.join("static",plotname)
        plt.savefig(plotPath)
    plt.clf()
    
    plt.figure()
    events=[f"E{i}" for i in range(1,7)]
    plt.bar(events,eventCount,width=0.5)
    for i in range(3):
        plotname="event_code_distribution"+downasList[i]
        plotPath=os.path.join("static",plotname)
        plt.savefig(plotPath)
    plt.clf()
    return render_template('graphs_plots.html',yearlist1=session.get('yearlist1'),monthlist1=session.get('monthlist1'),yearlist2=session.get('yearlist2'),monthlist2=session.get('monthlist2'),firstTime=session.get('firstTime'),lastTime=session.get('lastTime'),lastDate=session.get('lastDate'),firstDate=session.get('firstDate'),firstMonth=session.get('firstMonth'),lastMonth=session.get('lastMonth'),firstYear=session.get('firstYear'),lastYear=session.get('lastYear'),displayFrom=session.get('displayFrom'),displayTo=session.get('displayTo'),displayyes=displayyes)

@app.route('/download_graph',methods=['GET','POST'])
def downloadGraph():
    downas=request.form.get('download_as')
    print(downas)
    plotType=request.form.get('plotType')
    downasDict={"PNG":".png","JPEG":".jpeg","PDF":".pdf"}
    plotTypeDict={"Events logged with time (Line Plot)":"events_vs_time","Level State Distribution (Pie Chart)":"level_state_distribution","Event Code Distribution (Bar Plot)":"event_code_distribution"}
    plotname=plotTypeDict[plotType]+downasDict[downas]
    print(plotname)
    plotPath=os.path.join("static",plotname)
    return send_file(plotPath,as_attachment=True,download_name=plotname)

@app.route('/custom',methods=['GET','POST'])
def customGraph():
    if request.method == 'POST':
        code=request.form.get('code')
        df=pd.read_csv('log.csv')
        plt.figure()  
        exec(code)
        plt.clf()
    return render_template('custom.html')


if __name__ == "__main__":
    app.run(debug=True)
