file=$1
lineno=0

declare -A events
events["E1"]="jk2_init() Found child <*> in scoreboard slot <*>"
events["E2"]="workerEnv.init() ok <*>"
events["E3"]="mod_jk child workerEnv in error state <*>"
events["E4"]="[client <*>] Directory index forbidden by rule: <*>"
events["E5"]="jk2_init() Can't find child <*> in scoreboard"
events["E6"]="mod_jk child init <*> <*>"
declare -A regexOfEvents
regexOfEvents["E1"]="jk2_init\(\) Found child .* in scoreboard slot.*"
regexOfEvents["E2"]="workerEnv\.init\(\) ok.*"
regexOfEvents["E3"]="mod_jk child workerEnv in error state.*"
regexOfEvents["E4"]="\[client .*\] Directory index forbidden by rule:.*"
regexOfEvents["E5"]="jk2_init\(\) Can't find child .* in scoreboard"
regexOfEvents["E6"]="mod_jk child init.*"

echo '"LineId","Time","Level","Content","EventId","EventTemplate"' > log.csv

if [[ "$file" == *.log ]]; then
    while read -r line; do
        if [[ "$line" =~ \[[A-Za-z]{3}\ [A-Za-z]{3}\ [0-9]{2}\ [0-9]{2}:[0-9]{2}:[0-9]{2}\ [0-9]{4}\]\ \[(notice|error)\]\ .* ]]; then
            (( lineno++ )) 
            #echo "yes"
            #echo $lineno
            time=$(echo $line | cut -d ']' -f 1 | cut -d '[' -f 2)
            level=$(echo $line | cut -d ']' -f 2 | cut -d '[' -f 2)
            #content=$(echo $line | cut -d ']' -f 3- | cut -d ' ' -f 1 --complement )
            content=$(echo "$line" | cut -d ']' -f3- | sed 's/^ //')
            cleanContent=$(echo "$content" | sed 's/[\r\n]//g')

            for eventno in "${!events[@]}"; do
                if [[ "$cleanContent" =~ ${regexOfEvents[$eventno]} ]]; then
                    echo "$lineno,\"$time\",\"$level\",\"$cleanContent\",\"$eventno\",\"${events[$eventno]}\"" >>log.csv    
                fi
            done 
        else
            echo "Not a Apache log file"
            break
        fi
    done < $file
fi

