# this csv_parser is specific to Apache log files only
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

# Converts line from the csv file to a number so that i can compare times
def DateTime(line):
    monthno={"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}
    # line[1] is the time in the csv line list
    return (int(line[1][-4:])*10000+int(monthno[line[1][4:7]])*100+int(line[1][8:10]) + 0.01*(int(line[1][-13:-11])+int(line[1][-10:-8])*0.01+int(line[1][-7:-5])*0.0001))

# Converts the input from Event/s text box to event id list or returns False if the input is not proper
def ConvertInputEventId(event):
    try:
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
    except:
        return False
