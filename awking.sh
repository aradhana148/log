file=$1
if [[ "$file" == *.log ]]; then
    echo '"LineId","Time","Level","Content","EventId","EventTemplate"' > log.csv
    awk '
    BEGIN{
        FS="] "
        OFS=","
        RS="\n"
        ORS="\n"
        lineno=0
        events["E1"]="jk2_init() Found child <*> in scoreboard slot <*>";
        events["E2"]="workerEnv.init() ok <*>";
        events["E3"]="mod_jk child workerEnv in error state <*>";
        events["E4"]="[client <*>] Directory index forbidden by rule: <*>";
        events["E5"]="jk2_init() Can'\''t find child <*> in scoreboard";
        events["E6"]="mod_jk child init <*> <*>";

        regexOfEvents["E1"]="jk2_init\(\) Found child .* in scoreboard slot.*";
        regexOfEvents["E2"]="workerEnv\.init\(\) ok.*";
        regexOfEvents["E3"]="mod_jk child workerEnv in error state.*";
        regexOfEvents["E4"]="\[client .*\] Directory index forbidden by rule:.*";
        regexOfEvents["E5"]="jk2_init\(\) Can'\''t find child .* in scoreboard";
        regexOfEvents["E6"]="mod_jk child init.*";
    }
    {
        lineno++
        time="\"" substr($1,2) "\""
        level="\"" substr($2,2) "\""
        content=""
        for(i=3;i<=NF;i++){
            content=content $i
            if(i<NF){
                content=content "] "
            }
            unclean=substr(content,length(content))
            if (unclean == "\n" || unclean == "\r"){
                content=substr(content,1,length(content)-1) 
            }
        }
        for (event in regexOfEvents) {
            if (content ~ regexOfEvents[event]){
                eventid ="\"" event "\""
                eventtemplate="\"" events[event] "\""
                break
            }
        }
        content="\"" content "\""
        print lineno,time,level,content,event,eventtemplate >> "log.csv"
    }' $file
fi