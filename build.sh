#!/bin/bash

echo "Clear old distribution files"
rm dist/*

echo "Build new distribution files"
python3 -m build 


echo "Build done."
echo "If everything went fine, do you want to push it to PyPi PROD?"
echo "Think twice, now is good time to Ctrl+C this..."
read -n1 -s -r -p $'Press any key to continue...\n' key
python3 -m twine upload dist/*