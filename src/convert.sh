#!/bin/bash
# Code is modelled based on https://askubuntu.com/questions/62492/how-can-i-change-the-date-modified-created-of-a-file

for file in *.HEIC; do 
  echo "Converting $file to ${file%%.HEIC}.jpg"
  heif-convert "$file" "${file%%.HEIC}.jpg"

  echo "reading original creation date"
  date=$(stat -c %y -t "$file"| cut -d "." -f 1)

  echo "writing original creation date as modification and creation date"
  touch -am --date="$date" "${file%%.HEIC}.jpg"
done
