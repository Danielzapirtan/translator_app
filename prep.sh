#! /bin/bash

cp -a en.txt en.bak.txt
sed -ie "s/[^[:print:]]//g" en.txt
sed -ie "s/\n/ /g" en.txt
sed -ie "s/\. /.\n/g" en.txt

