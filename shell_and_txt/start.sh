#!/bin/sh
cur_path="$PWD"
cd $cur_path
if [ -e "in.pipe" ]; then
    rm in.pipe
fi
mkfifo in.pipe
(tail -f in.pipe | nohup ./SandBox.x86_64 &) > nohup.out
