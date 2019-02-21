#!/bin/bash
yum install epel-release -y
yum install https://centos7.iuscommunity.org/ius-release.rpm -y
yum install python36u -y
yum install python36u-pip -y
ln -s /usr/bin/python3.6 /usr/bin/python3
ln -s /usr/bin/pip3.6 /usr/bin/pip3
pip3 install bs4 requests pickleshare

program_path=`pwd`
app_name=${program_path##*/}
/usr/bin/crontab -l | egrep -v "${program_path}|##${app_name}##" > /tmp/crontab.bak
crontab=(
"##${app_name}##"
"*/20 * * * * cd ${program_path}/ && export LC_ALL=en_US.UTF-8; python3 spider.py > ./log/spider.log 2>&1"
)
for ((i = 0; i < ${#crontab[@]}; i++))
do
    echo "${crontab[$i]}" >> /tmp/crontab.bak
done
/usr/bin/crontab /tmp/crontab.bak
crontab -l| grep ${app_name}
