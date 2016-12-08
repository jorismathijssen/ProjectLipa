#!/bin/bash
#update.sh - simple logging + git pull script
#Copyright 2016, Guus Beckett reupload.nl
#Licensed under the GPL 2.

date >> restart.log
git pull
