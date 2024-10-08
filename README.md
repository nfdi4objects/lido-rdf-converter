# Lido to RDF converter

This repository contains Python code to convert LIDO XML files to RDF using a X3ML mapping.

## Installation

Requires Python >=3.5 and a POSIX compliant operating system. Clone the repository:

```sh
git clone https://github.com/nfdi4objects/lido-rdf-converter.git
cd lido-rdf-converter
```

Then install dependencies with `make deps` or 

```sh
python3 -m venv .venv
. .venv/bin/activate
pip3 install -r requirements.txt
```

## Usage

Call `./lido2rdf.py` without any arguments or with `--help` for help:

~~~
usage: lido2rdf.py [-h] [-o NAME] [-t FORMAT] [-m MAPPING] [LIDO-XML]

Convert LIDO to RDF using X3ML mapping

positional arguments:
  LIDO-XML                       LIDO file or URL (default: -)

options:
  -h, --help                     show this help message and exit
  -o NAME, --output NAME         RDF output file (default: -)
  -t FORMAT, --to FORMAT         RDF output serialization (ttl,nt,json,xml)
  -m MAPPING, --mapping MAPPING  X3ML mapping file (default: lido2rdf.x3ml)
~~~
 
For instance this will convert `example1.xml` to `example1.ttl`:

~~~sh
./lido2rdf.py example1.xml -o examle1.ttl
~~~

To inspect how an X3ML mapping file is used internally:

~~~sh
./x3ml.py lido2rdf.x3ml
~~~

## See Also

- <https://github.com/nfdi4objects/lido-examples> contains sample LIDO files to be used as test cases
- <https://github.com/nfdi4objects/lido-schema> contains schema files and validation script to check whether an XML file is valid LIDO

## License

MIT License
