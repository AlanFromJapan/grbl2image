#!/bin/bash

RED='\033[0;31m'
NC='\033[0m' # No Color
CYAN='\033[0;36m'


echo "Clear old distribution files"
rm dist/*

echo "Build new distribution files"
python3 -m build 


echo "Build done."
echo -e "${CYAN}If everything went fine, do you want to push it to PyPi ${RED}PROD${CYAN}?"
echo -e "By the way, you remembered to update the version number before that right?"
echo -e "Think twice, now is good time to Ctrl+C this...$NC"
read -n1 -s -r -p $'Press any key to continue...\n' key


echo "You will be asked for a login password: it's not the pypi password, it's a token."
echo -e "Username: ${RED}__token__${NC}"
echo -e "Password: ${RED}Your token${NC}"
python3 -m twine upload dist/*