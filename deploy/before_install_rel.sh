#!/bin/bash

#Get source code from git
sudo rm -rf /home/ec2-user/git/ikary
cd /home/ec2-user/git
eval `ssh-agent`
sudo chmod 400 /home/ec2-user/.ssh/id_rsa
ssh-add /home/ec2-user/.ssh/id_rsa
git clone git@bitbucket.org:c2sg_ibs/ikary.git -b release --depth 1

#Clear project source code
sudo rm -rf /home/ec2-user/deploy/ikary

