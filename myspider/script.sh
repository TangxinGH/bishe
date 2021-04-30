#!/bin/bash 
# 启动脚本 insecure--ssl-insecure
# shellcheck disable=SC2164
cd /home/work/wo/
nohup  mitmdump --mode upstream:http://192.168.0.8:7890 --ssl-insecure   --upstream-auth yayi:x56nj2s3i73b -s addons.py  > /dev/null 2>&1  &
# nohup mitmdump --listen-port=8085  --mode upstream:http://192.168.0.8:7890 --ssl-insecure   --upstream-auth yayi:x56nj2s3i73b -s plugin.py < jobinfo.confg  > jobinfo.log 2>&1  &
#nohup mitmdump --mode upstream:http://192.168.0.8:7890 --ssl-insecure --upstream-auth yayi:x56nj2s3i73b -s addons.py  < type.config  > type.log 2>&1  &
#Then you can check it's working with a simple curl:
#curl -x http://localhost:8080 -k https://api.ipify.org/
#使用-u参数，使得python不启用缓冲。
#
#所以改正命令，就可以正常使用了
#
#$ nohup python -u test.py > out.log 2>&1 & # u