from flask import Flask, render_template,request,send_file,session
import os
import subprocess
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from myfunctions import csv_parser,DateTime,ConvertInputEventId

app=Flask(__name__)
app.secret_key="chocolate oompa loompa"

UPLOADFOLDER = "uploads"
os.makedirs(UPLOADFOLDER,mode=0o777, exist_ok=True)

@app.route('/',methods=['GET', 'POST'])
def upload():
    msg=""
    show_links_to_other_pages_yes = False
    if request.method == 'POST':
        file=request.files['logfile']
        print(file.filename)
        print("yes")
        path=os.path.join(UPLOADFOLDER, file.filename)
        
        if file.filename =="":
            msg="Please select a file"
            msg_cat="error" # message category
            return render_template('log_upload.html', message=msg,msg_cat=msg_cat)
        file.save(path)
        # Check if file is log file
        if not file.filename.endswith('.log'):
            msg = "Please upload log file"
            msg_cat="error"  # message category
            os.remove(path)
            return render_template('log_upload.html', message=msg,msg_cat=msg_cat)
        subprocess.run(['awk','-f','awking.awk', path], check=True) 
        # Check if file is Apache log file
        if "log.csv" not in os.listdir("."):
            msg= "Please upload Apache log file"
            msg_cat="error" # message category
            os.remove(path)
            return render_template('log_upload.html',message=msg,msg_cat=msg_cat)
        
        session["upload_yes"]=True
        session["uploadedFileName"]=file.filename[:-4]  
        msg = "Log file uploaded and processed successfully"
        show_links_to_other_pages_yes = True
        i=0
        yearlist=[0] # the list of years in the log file
        session["yearlist"]=yearlist

        month_no={}
        month_no={"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}
 
        # To find the first(start) and last(end) Datetime of the log file and get a list of all the years(yearlist) in the log file
        start_time="" 
        end_time=""
        start_date=""
        end_date=""
        start_month=""
        end_month=""
        with open("log.csv","r") as f:
            for line in f:
                line=csv_parser(line)
                dt=line[1]
                if i==0:
                    i=1
                else:
                    if int(dt[-4:])>yearlist[len(yearlist)-1]:
                        yearlist.append(int(dt[-4:]))
                    if start_time =="":
                        start_time=dt[-12:-5]
                        start_date=dt[8:10]
                        start_month=dt[4:7]
                        session["firstTime"]=start_time
                        session["firstDate"]=start_date
                        session["firstMonth"]=start_month
                end_time=dt[-12:-5]
                end_date=dt[8:10]
                end_month=dt[4:7]

        session["lastTime"]=end_time
        session["lastDate"]=end_date
        session["lastMonth"]=end_month
        yearlist.pop(0)
        session['yearlist1']=yearlist[1:]
        session['yearlist2']=yearlist[:len(yearlist)-1]
        a=list(month_no.keys())
        b=list(month_no.keys())
        a.pop(month_no[start_month]-1)
        b.pop(month_no[end_month]-1)
        session['monthlist1']=a
        session['monthlist2']=b
        session["firstYear"]=yearlist[0]
        session["lastYear"]=yearlist[len(yearlist)-1]

    
    return render_template('log_upload.html',message=msg,show_links_to_other_pages_yes=show_links_to_other_pages_yes,msg_cat="no_error")

            
@app.route('/display',methods=['GET','POST'])
def display():
    i=0
    headList=None # the list of the table head elements
    dataList=[] # list of list of table body elements
    LevelsList=["all","notice","error"]
    session["levelsList"]=LevelsList
    filter_msg=False
    filter_post=False # to check if the filter query is submitted
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
        eventId=ConvertInputEventId(eventId) # converts the input from Event/s text box to event id list or returns False if the input is not proper
        
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
    # if filter_post is False and filter_msg is not False, then the Download Filtered csv button wont appear so when the filter is not submitted, the button wont appear.
    return render_template('log_display.html',headList=headList,dataList=dataList,tableName=session.get('uploadedFileName'),levelsList=session.get('levelsList'),selectedLevel=session.get('selectedLevel'),selectedEventId=session.get('selectedEventId'),filter_msg=filter_msg,filter_post=filter_post)


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
        month_no={"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}
        start_year = int(request.form.get("start_year"))
        start_month = int(month_no[request.form.get("start_month")])
        start_date=int(request.form.get("start_date"))
        if start_date>31:
            return render_template('graphs_plots.html',yearlist1=session.get('yearlist1'),monthlist1=session.get('monthlist1'),yearlist2=session.get('yearlist2'),monthlist2=session.get('monthlist2'),firstTime=session.get('firstTime'),lastTime=session.get('lastTime'),lastDate=session.get('lastDate'),firstDate=session.get('firstDate'),firstMonth=session.get('firstMonth'),lastMonth=session.get('lastMonth'),firstYear=session.get('firstYear'),lastYear=session.get('lastYear'),timeerror="Please enter valid Start Time")
        start_time = request.form.get("start_time")
        start_time=start_time.split(":")
        try:
            start_time=[int(i) for i in start_time] # list of hour,minute,seconds
            if len(start_time)!=3 or start_time[0]>24 or start_time[1]>60 or start_time[2]>60:
                return render_template('graphs_plots.html',yearlist1=session.get('yearlist1'),monthlist1=session.get('monthlist1'),yearlist2=session.get('yearlist2'),monthlist2=session.get('monthlist2'),firstTime=session.get('firstTime'),lastTime=session.get('lastTime'),lastDate=session.get('lastDate'),firstDate=session.get('firstDate'),firstMonth=session.get('firstMonth'),lastMonth=session.get('lastMonth'),firstYear=session.get('firstYear'),lastYear=session.get('lastYear'),timeerror="Please enter valid Start Time")
            start_time=start_time[0]+start_time[1]*0.01+start_time[2]*0.0001
        except:
            return render_template('graphs_plots.html',yearlist1=session.get('yearlist1'),monthlist1=session.get('monthlist1'),yearlist2=session.get('yearlist2'),monthlist2=session.get('monthlist2'),firstTime=session.get('firstTime'),lastTime=session.get('lastTime'),lastDate=session.get('lastDate'),firstDate=session.get('firstDate'),firstMonth=session.get('firstMonth'),lastMonth=session.get('lastMonth'),firstYear=session.get('firstYear'),lastYear=session.get('lastYear'),timeerror="Please enter valid Start Time")
        end_year = int(request.form.get("end_year"))
        end_month = int(month_no[request.form.get("end_month")])
        end_date=int(request.form.get("end_date"))
        if end_date>31:
            return render_template('graphs_plots.html',yearlist1=session.get('yearlist1'),monthlist1=session.get('monthlist1'),yearlist2=session.get('yearlist2'),monthlist2=session.get('monthlist2'),firstTime=session.get('firstTime'),lastTime=session.get('lastTime'),lastDate=session.get('lastDate'),firstDate=session.get('firstDate'),firstMonth=session.get('firstMonth'),lastMonth=session.get('lastMonth'),firstYear=session.get('firstYear'),lastYear=session.get('lastYear'),timeerror="Please enter valid End Time")
        end_time = request.form.get("end_time")
        end_time=end_time.split(":")
        try:
            end_time=[int(i) for i in end_time] # list of hour,minute,seconds
            if len(end_time)!=3 or end_time[0]>24 or end_time[1]>60 or end_time[2]>60:
                return render_template('graphs_plots.html',yearlist1=session.get('yearlist1'),monthlist1=session.get('monthlist1'),yearlist2=session.get('yearlist2'),monthlist2=session.get('monthlist2'),firstTime=session.get('firstTime'),lastTime=session.get('lastTime'),lastDate=session.get('lastDate'),firstDate=session.get('firstDate'),firstMonth=session.get('firstMonth'),lastMonth=session.get('lastMonth'),firstYear=session.get('firstYear'),lastYear=session.get('lastYear'),timeerror="Please enter valid End Time")
            end_time=end_time[0]+end_time[1]*0.01+end_time[2]*0.0001
        except:
            return render_template('graphs_plots.html',yearlist1=session.get('yearlist1'),monthlist1=session.get('monthlist1'),yearlist2=session.get('yearlist2'),monthlist2=session.get('monthlist2'),firstTime=session.get('firstTime'),lastTime=session.get('lastTime'),lastDate=session.get('lastDate'),firstDate=session.get('firstDate'),firstMonth=session.get('firstMonth'),lastMonth=session.get('lastMonth'),firstYear=session.get('firstYear'),lastYear=session.get('lastYear'),timeerror="Please enter valid End Time")
    start_DateTime=start_year*10000+start_month*100+start_date+start_time*0.01 # to convert start datetime to number
    end_DateTime=end_year*10000+end_month*100+end_date+end_time*0.01 # to convert end datetime to number
    displayFrom=request.form.get("start_month")+" "+str(start_date)+" "+request.form.get("start_time")+" "+str(start_year)
    displayTo=request.form.get("end_month")+" "+str(end_date)+" "+request.form.get("end_time")+" "+str(end_year)
    
    session['displayFrom']=displayFrom
    session['displayTo']=displayTo
    error=0
    notice=0
    time={} # dictionary of Date time and their corresponding frequency
    times=[] #list of Date times.
    no_of_time=[] #list of no of times of a specifc Date time.
    eventCount=[0,0,0,0,0,0] # to count the no of times each event occurs
    with open("log.csv","r") as f:
        a=0
        for line in f:
            line=csv_parser(line)
            if a==1:
                if start_DateTime>end_DateTime:
                    return render_template('graphs_plots.html',yearlist1=session.get('yearlist1'),monthlist1=session.get('monthlist1'),yearlist2=session.get('yearlist2'),monthlist2=session.get('monthlist2'),firstTime=session.get('firstTime'),lastTime=session.get('lastTime'),lastDate=session.get('lastDate'),firstDate=session.get('firstDate'),firstMonth=session.get('firstMonth'),lastMonth=session.get('lastMonth'),firstYear=session.get('firstYear'),lastYear=session.get('lastYear'),msg=True)
                if DateTime(line)>end_DateTime:
                    break
                if start_DateTime<=DateTime(line)<=end_DateTime:
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
    downasList=[".png",".jpeg",".pdf"] #download as list
    # for line plot Events vs Time :
    plt.figure(figsize=(17,15))
    times=time.keys()
    times=list(times)
    no_of_time=time.values()
    plt.plot(times,no_of_time,color='#ff8500')
    plt.xlabel('Time',fontsize=14)
    plt.ylabel('Number of Events',fontsize=14)
    plt.title('Events vs Time',fontsize=16)
    if len(times)>20:
        arr=np.linspace(0,len(times)-1,20)
        arr=list(arr)
        arr=[int(i) for i in arr]
        xticks=[times[i][4:] for i in arr]
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
 
    # for pie plot Level State Distribution :
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
    
    # for bar plot Event Code Distribution :
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
    #to download the plots in the chosen file type
    downas=request.form.get('download_as')
    plotType=request.form.get('plotType')
    downasDict={"PNG":".png","JPEG":".jpeg","PDF":".pdf"}
    plotTypeDict={"Events logged with time (Line Plot)":"events_vs_time","Level State Distribution (Pie Chart)":"level_state_distribution","Event Code Distribution (Bar Plot)":"event_code_distribution"}
    plotname=plotTypeDict[plotType]+downasDict[downas]
    plotPath=os.path.join("static",plotname)
    return send_file(plotPath,as_attachment=True,download_name=plotname)

@app.route('/custom',methods=['GET','POST'])
def customGraph():
    # Embedded python code editor for custom analysis
    show_custom_yes=False
    error_msg=""
    if request.method == 'POST':
        code=request.form.get('code')
        try:
            df=pd.read_csv('log.csv')
            plt.figure()  
            exec(code)
            plt.clf()
            show_custom_yes=True
        except Exception as error:
            error_msg = str(error)
            print(error_msg)
    return render_template('custom.html',error_msg=error_msg,show_custom_yes=show_custom_yes)

@app.route('/downloadCustom')
def downloadCustom():
    return send_file('static/custom.png',as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)

