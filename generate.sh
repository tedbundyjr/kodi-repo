#!/bin/sh
# rm -rf _repo
./get.sh
rsync -av --exclude=.git --exclude=packages --exclude=repository.boogie --exclude=repository.vms ~/Library/Application\ Support/Kodi/addons/ .
cd _tools 
python generate_repo.py
cd -
