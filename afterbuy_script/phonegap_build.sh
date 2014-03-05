#!/bin/sh
# Script to create phonegap app

cd afterbuy_script
phonegap create afterbuy -n afterbuy -i com.gladminds.afterbuy
cp -r new/* afterbuy/www 
python parse_afterbuy.py $1 $2 
cd afterbuy 
#add a command to work with
cd ../
zip -r afterbuy afterbuy
pip install requests
pip install json
python publish_adobe.py
cd ../
exit 0
