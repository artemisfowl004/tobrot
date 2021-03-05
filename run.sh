#!/bin/sh
mkdir .a && cd .a
#git clone --quiet https://github.com/artemisfowl004/tobrot && cd tobrot
#python3 -m tobrot & cd ~
git clone --quiet https://github.com/artemisfowl004/tobrot && cd tobrot
python3 -m tobrot & ls
