from flask import Flask, render_template,request,send_file,session
import os
import subprocess
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from myfunctions import csv_parser,DateTime,ConvertInputEventId

app=Flask(__name__)
app.secret_key="oompa loompa"

UPLOADFOLDER = "uploads"
os.makedirs(UPLOADFOLDER,mode=0o777, exist_ok=True)

@app.route('/',methods=['GET', 'POST'])
def upload():
    msg=""
    yes = False
    if request.method == 'POST':
        file=request.files['logfile']
        print(file.filename)
        print("yes")
        path=os.path.join(UPLOADFOLDER, file.filename)
        
        if file.filename =="":
            msg="Please select file"
            msg_cat="error"
            return render_template('log_upload2.html', message=msg,msg_cat=msg_cat)
        file.save(path)
        if not file.filename.endswith('.log'):
            msg = "Please upload a log file"
            msg_cat="error"
            os.remove(path)
            return render_template('log_upload2.html', message=msg,msg_cat=msg_cat)
        subprocess.run(['awk','-f','awking.awk', path], check=True) 
        if "log.csv" not in os.listdir("."):
            msg= "Please upload Apache log"
            msg_cat="error"
            os.remove(path)
            return render_template('log_upload2.html',message=msg,msg_cat=msg_cat)
        
        session["upload_yes"]=True
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

    
    return render_template('log_upload2.html',message=msg,yes=yes,msg_cat="no_error")

            
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
    filter_msg=False
    filter_post=False
    with open("log.csv","r") as f:
        for line in f:
            if i==0:
                headList=line.split(',')
                i=1
            else:
                line=csv_parser(line)
                dataList.append(line)
        session["selectedLevel"]="all"
        session["selectedEventId"]="all"
    if request.method=="POST":
        filter_post=True
        level=request.form.get("level")
        if level=="all":
            session["selectedLevel"]="notice,error"
        else:
            session["selectedLevel"]=level
        eventId=request.form.get("eventid")
        session["selectedEventId"]=eventId
        eventId=ConvertInputEventId(eventId)
        
        if eventId==False:
            filter_msg="Please enter correct event Ids"
            with open("log.csv","r") as f:
                for line in f:
                    if i==0:
                        headList=line.split(',')
                        i=1
                    else:
                        linep=csv_parser(line)
                        dataList.append(linep)     
        else: 
            i=0
            dataList=[]
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
    return render_template('log_display.html',headList=headList,dataList=dataList,tableName=session.get('uploadedFileName'),levelsList=session.get('levelsList'),eventIdsList=session.get('eventIdsList'),selectedLevel=session.get('selectedLevel'),selectedEventId=session.get('selectedEventId'),filter_msg=filter_msg,filter_post=filter_post)


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
        if sdate>31:
            return render_template('graphs_plots.html',yearlist1=session.get('yearlist1'),monthlist1=session.get('monthlist1'),yearlist2=session.get('yearlist2'),monthlist2=session.get('monthlist2'),firstTime=session.get('firstTime'),lastTime=session.get('lastTime'),lastDate=session.get('lastDate'),firstDate=session.get('firstDate'),firstMonth=session.get('firstMonth'),lastMonth=session.get('lastMonth'),firstYear=session.get('firstYear'),lastYear=session.get('lastYear'),timeerror="Please enter valid Start Time")
        stime = request.form.get("stime")
        stime=stime.split(":")
        try:
            stime=[int(i) for i in stime]
            if len(stime)!=3 or stime[0]>24 or stime[1]>60 or stime[2]>60:
                return render_template('graphs_plots.html',yearlist1=session.get('yearlist1'),monthlist1=session.get('monthlist1'),yearlist2=session.get('yearlist2'),monthlist2=session.get('monthlist2'),firstTime=session.get('firstTime'),lastTime=session.get('lastTime'),lastDate=session.get('lastDate'),firstDate=session.get('firstDate'),firstMonth=session.get('firstMonth'),lastMonth=session.get('lastMonth'),firstYear=session.get('firstYear'),lastYear=session.get('lastYear'),timeerror="Please enter valid Start Time")
            stime=stime[0]+stime[1]*0.01+stime[2]*0.0001
        except:
            return render_template('graphs_plots.html',yearlist1=session.get('yearlist1'),monthlist1=session.get('monthlist1'),yearlist2=session.get('yearlist2'),monthlist2=session.get('monthlist2'),firstTime=session.get('firstTime'),lastTime=session.get('lastTime'),lastDate=session.get('lastDate'),firstDate=session.get('firstDate'),firstMonth=session.get('firstMonth'),lastMonth=session.get('lastMonth'),firstYear=session.get('firstYear'),lastYear=session.get('lastYear'),timeerror="Please enter valid Start Time")
        eyear = int(request.form.get("eyear"))
        emonth = int(monthno[request.form.get("emonth")])
        edate=int(request.form.get("edate"))
        if edate>31:
            return render_template('graphs_plots.html',yearlist1=session.get('yearlist1'),monthlist1=session.get('monthlist1'),yearlist2=session.get('yearlist2'),monthlist2=session.get('monthlist2'),firstTime=session.get('firstTime'),lastTime=session.get('lastTime'),lastDate=session.get('lastDate'),firstDate=session.get('firstDate'),firstMonth=session.get('firstMonth'),lastMonth=session.get('lastMonth'),firstYear=session.get('firstYear'),lastYear=session.get('lastYear'),timeerror="Please enter valid End Time")
        etime = request.form.get("etime")
        etime=etime.split(":")
        try:
            etime=[int(i) for i in etime]
            if len(etime)!=3 or etime[0]>24 or etime[1]>60 or etime[2]>60:
                return render_template('graphs_plots.html',yearlist1=session.get('yearlist1'),monthlist1=session.get('monthlist1'),yearlist2=session.get('yearlist2'),monthlist2=session.get('monthlist2'),firstTime=session.get('firstTime'),lastTime=session.get('lastTime'),lastDate=session.get('lastDate'),firstDate=session.get('firstDate'),firstMonth=session.get('firstMonth'),lastMonth=session.get('lastMonth'),firstYear=session.get('firstYear'),lastYear=session.get('lastYear'),timeerror="Please enter valid End Time")
            etime=etime[0]+etime[1]*0.01+etime[2]*0.0001
        except:
            return render_template('graphs_plots.html',yearlist1=session.get('yearlist1'),monthlist1=session.get('monthlist1'),yearlist2=session.get('yearlist2'),monthlist2=session.get('monthlist2'),firstTime=session.get('firstTime'),lastTime=session.get('lastTime'),lastDate=session.get('lastDate'),firstDate=session.get('firstDate'),firstMonth=session.get('firstMonth'),lastMonth=session.get('lastMonth'),firstYear=session.get('firstYear'),lastYear=session.get('lastYear'),timeerror="Please enter valid End Time")
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
    plt.figure(figsize=(17,15))
    times=time.keys()
    times=list(times)
    #print(times)
    noof=time.values()
    plt.plot(times,noof,color='#ff8500')
    plt.xlabel('Time',fontsize=14)
    plt.ylabel('Number of Events',fontsize=14)
    plt.title('Events vs Time',fontsize=16)
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
    plt.tight_layout()
    plt.clf()

    y=[error,notice]
    labels=["error","notice"]
    colors=["#ff8500","#219ebc"]
    plt.figure()
    plt.pie(y,labels=labels,colors=colors)
    plt.title("Level State Distribution")
    plt.legend(labels,loc="best")
    for i in range(3):
        plotname="level_state_distribution"+downasList[i]
        plotPath=os.path.join("static",plotname)
        plt.savefig(plotPath)
    plt.clf()
    
    plt.figure()
    events=[f"E{i}" for i in range(1,7)]
    plt.title('Event Code Distribution')
    plt.xlabel('Event ID')
    plt.ylabel('Number of Occurrences')
    plt.bar(events,eventCount,width=0.5,color='#219ebc')
    for i in range(3):
        plotname="event_code_distribution"+downasList[i]
        plotPath=os.path.join("static",plotname)
        plt.savefig(plotPath)
    plt.clf()
    return render_template('graphs_plots.html',yearlist1=session.get('yearlist1'),monthlist1=session.get('monthlist1'),yearlist2=session.get('yearlist2'),monthlist2=session.get('monthlist2'),firstTime=session.get('firstTime'),lastTime=session.get('lastTime'),lastDate=session.get('lastDate'),firstDate=session.get('firstDate'),firstMonth=session.get('firstMonth'),lastMonth=session.get('lastMonth'),firstYear=session.get('firstYear'),lastYear=session.get('lastYear'),displayFrom=session.get('displayFrom'),displayTo=session.get('displayTo'),displayyes=displayyes)

@app.route('/download_graph',methods=['GET','POST'])
def downloadGraph():
    downas=request.form.get('download_as')
    plotType=request.form.get('plotType')
    downasDict={"PNG":".png","JPEG":".jpeg","PDF":".pdf"}
    plotTypeDict={"Events logged with time (Line Plot)":"events_vs_time","Level State Distribution (Pie Chart)":"level_state_distribution","Event Code Distribution (Bar Plot)":"event_code_distribution"}
    plotname=plotTypeDict[plotType]+downasDict[downas]
    plotPath=os.path.join("static",plotname)
    return send_file(plotPath,as_attachment=True,download_name=plotname)

@app.route('/custom',methods=['GET','POST'])
def customGraph():
    emsg=""
    if request.method == 'POST':
        code=request.form.get('code')
        try:
            df=pd.read_csv('log.csv')
            plt.figure()  
            exec(code)
            plt.clf()
        except Exception as err:
            emsg = str(emsg)
    return render_template('custom.html',emsg=emsg)

@app.route('/downloadCustom')
def downloadCustom():
    return send_file('static/custom.png',as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)

