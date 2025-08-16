#! /bin/bash

cp -a en.bak.txt en.txt
sed -ie "s/[^[:print:]]/ /g" en.txt
sed -ie "s/, */, /g" en.txt
sed -ie "s/\n/ /g" en.txt
exit
sed -ie "s/\. /\./g" en.txt
sed -ie "s/ - //g" en.txt
sed -ie "s/Dr\.\n/Dr. /g" en.txt
sed -ie "s/PhD/PhD/g" en.txt
