# Lido to RDF converter

[![License](https://img.shields.io/github/license/nfdi4objects/lido-rdf-converter.svg)](https://github.com/nfdi4objects/lido-rdf-converter/blob/master/LICENSE)
[![Test](https://github.com/nfdi4objects/lido-rdf-converter/actions/workflows/test.yml/badge.svg)](https://github.com/nfdi4objects/lido-rdf-converter/actions/workflows/test.yml)
[![Docker](https://img.shields.io/badge/Docker-ghcr.io%2Fnfdi4objects%2Fnlido--rdf--converter-informational)](https://github.com/nfdi4objects/lido-rdf-converter/pkgs/container/lido-rdf-converter)

This repository contains a Python library, command line script, and web application to convert LIDO XML files to RDF using X3ML mappings

## Installation

The application can be installed with Docker (recommended) or from sources (for development).

### With Docker

Pull the [current image](https://github.com/orgs/nfdi4objects/packages/container/package/lido-rdf-converter)

~~~sh
docker pull ghcr.io/nfdi4objects/lido-rdf-converter:main
~~~

and start a container with `docker`, or with `docker compose` and a `docker-compose.yml` like [the one in this repository](docker-compose.yml):

~~~sh
docker run --rm -p 5000:5000 ghcr.io/nfdi4objects/lido-rdf-converter:main
~~~

or

~~~sh
docker compose up --force-recreate
~~~

### From sources

Requires Python >=3.5 and a POSIX compliant operating system. Clone the repository, including its submodules:

```sh
git clone --recursive https://github.com/nfdi4objects/lido-rdf-converter.git
cd lido-rdf-converter
```

Then install dependencies and missing submodules, and enable virtual Python environment:

```sh
make deps
. .venv/bin/activate
```

## Usage

### Command line client

With Docker the command line client can be called like this:

~~~sh
cat example1.xml | docker run --rm -i ghcr.io/nfdi4objects/lido-rdf-converter:main lido2rdf
~~~

Alternatively mount a volume to read and write files:

~~~sh
docker run --rm -v .:/data ghcr.io/nfdi4objects/lido-rdf-converter:main lido2rdf /data/example1.xml
~~~

If installed from sources, call `./lido2rdf` without any arguments or with `--help` for help:

~~~
usage: lido2rdf [-h] [-o NAME] [-t FORMAT] [-m MAPPING] [LIDO-XML]

Convert LIDO to RDF using X3ML mapping

positional arguments:
  LIDO-XML                       LIDO file or URL (default: -)

options:
  -h, --help                     show this help message and exit
  -o NAME, --output NAME         RDF output file (default: -)
  -t FORMAT, --to FORMAT         RDF output serialization (ttl,nt,json,xml)
  -m MAPPING, --mapping MAPPING  X3ML mapping file (default: defaultMapping.x3ml)
~~~
 
For instance this will convert `example1.xml` to `example1.ttl`:

~~~sh
./lido2rdf.py example1.xml -o examle1.ttl
~~~

To inspect how an X3ML mapping file is used internally:

~~~sh
./x3ml.py defaultMapping.x3ml
~~~

### Web application

The web application is made available at <http://localhost:5000> by default, if installed via Docker. 

Usage if installed from sources is only recommended for development and testing.

If you want to run the web application by script, you have to install some JS scripts first.
Therefore, you can use these shell commands:

~~~sh
cd ./lidoapp_bp/static
npm ci
cd ../..
~~~

Then start `app.py` (optionally with argument `--port`):

~~~sh
python app.py
~~~

### API

The API has not fully been specified yet an may change.

#### POST /convert

Convert LIDO/XML with default mapping. Returns RDF in Turtle serialization on success.

LIDO data can be send either via HTTP POST payload or as `multipart/form-data` file upload:

~~~sh
curl http://127.0.0.1:5000/convert --data-binary @lido.xml --silent
curl http://127.0.0.1:5000/convert -F file=@example.xml --silent
~~~

## Build and test

To locally build a Docker image for testing:

~~~sh
docker compose build
~~~

## See Also

- <https://github.com/nfdi4objects/lido-schema> contains schema files and validation script to check whether an XML file is valid LIDO (included as submodule into directory `lido-schema`)
- <https://github.com/nfdi4objects/lido-examples> contains sample LIDO files to be used as test cases

## License

MIT License
