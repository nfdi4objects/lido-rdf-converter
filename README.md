# Lido to RDF converter
This repository contains python code to convert LIDO files tor RDF files.


## Installation
Requires python3 >=3.5, pip3 and python-venv 
```
git clone https://github.com/nfdi4objects/lido-rdf-converter.git
cd lido-rdf-converter
python3 -m venv .venv
. .venv/bin/activate
pip3 install -r requirement.txt
python3 xml2rdf.py -u file:./Example1.xml -o "./example1.ttl" 
python3 xml2rdf.py -u file:./Example20.xml -o "./example20.ttl" 
```
The last commands create output file example1.ttl and example20.ttl 
For help use:
```
python3 xml2rdf.py
```
The suffix of the output file defines the RDF format. 
Supported formats are given in this dictionary (suffix:format):
```
{'xml': 'xml', 'ttl': 'turtle', 'json': 'json-ld','n3': 'n3', 'trig': 'trig', 'trix': 'trix', 'nquads': 'nquads', 'turtle': 'turtle'}
``` 

