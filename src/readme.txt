sudo apt-get install python3-pip

python3 -m pip install --upgrade setuptools
sudo pip3 install --upgrade pip setuptools wheel
sudo apt-get install python3.6-dev libmysqlclient-dev
git clone --recursive https://github.com/ethanhs/pynanosvg.git
cd pynanosvg
python3 -m pip install --user .
