#!/bin/bash

projStr="ikari."
# loop to get all the settings files
for file in $(find /home/ec2-user/projects/ikari/src/ikari/ikari -maxdepth 1 -name "settings_rel*.py")
do
    fileName=$(basename -- "$file")
    fileNameWithoutExt="${fileName%.*}"
    settingName="$projStr$fileNameWithoutExt"
    /home/ec2-user/projects/ikari/venv/bin/python /home/ec2-user/projects/ikari/src/ikari/manage.py balanceForward --settings=$settingName
done