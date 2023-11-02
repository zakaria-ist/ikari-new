#!/bin/bash

#Copy source code to project folder
# sudo rsync -avz --exclude '.git' /home/ec2-user/git/ikari/ /home/ec2-user/projects/ikari
sudo rsync -avzC /home/ec2-user/git/ikary/ /home/ec2-user/projects/ikari --exclude="log" --exclude="log/*" --exclude="media/*" --exclude="media"

# Creating Virtual Environment
sudo virtualenv --python /usr/bin/python3.4 /home/ec2-user/projects/ikari/venv
sudo chmod -R 777 /home/ec2-user/projects/ikari/venv

#Run migrate
/home/ec2-user/projects/ikari/venv/bin/pip install -r /home/ec2-user/projects/ikari/src/ikari/requirements.txt

