#!/bin/bash

projStr="ikari."
for file in $(find /Users/smzakaria/dev/ikari/ikary/src/ikari/ikari -maxdepth 1 -name "settings.py")
do
    fileName=$(basename -- "$file")
    fileNameWithoutExt="${fileName%.*}"
    settingName="$projStr$fileNameWithoutExt"
    echo "$settingName"
    /Users/smzakaria/.pyenv/versions/@ikary/bin/python /Users/smzakaria/dev/ikari/ikary/src/ikari/manage.py recurring --settings=$settingName
done