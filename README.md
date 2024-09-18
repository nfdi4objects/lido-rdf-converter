# Lido to RDF converter
This repository contains python code to convert LIDO files tor RDF files.


## Installation
Requires python3 >=3.5, pip3 and python-venv 
```
git clone https://github.com/nfdi4objects/lido-rdf-converter.git
cd lido-rdf-converter
. .venv/bin/activate
pip3 install -r requirement.txt
python3 xml2rdf.py -u file:./Example1.xml -o "./example1.ttl" 
python3 xml2rdf.py -u file:./Example20.xml -o "./example20.ttl" 
```
