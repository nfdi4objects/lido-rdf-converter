#!.venv/bin/python

"""Converts LIDO file to RDF """
from LidoRDFConverter import LidoRDFConverter
from sys import stdin, stdout, stderr, exit
import re
import argparse
from io import BytesIO
from urllib.error import HTTPError, URLError

urlPattern = re.compile("^(https?|file):")

formatNames = {'ttl': 'turtle', 'nt': 'nt', 'json': 'json-ld', 'xml': 'xml'}


def error(msg):
    print(msg, file=stderr)
    exit(1)


def lido2rdf(source, target, mapping, format=None):
    '''Applies x3ml mapping to a LIDO file and writes result'''

    if format:
        if format in formatNames:
            format = formatNames[format]
        else:
            error(f"RDF serialization format not supported: {format}!")
    else:
        suffix = target.split('.')[-1]
        format = formatNames.get(suffix, 'turtle')

    converter = LidoRDFConverter(mapping)
    if urlPattern.match(source):
        graph = converter.processURL(source)
    else:
        if source == "-":
            source = BytesIO(stdin.buffer.read())
        graph = converter.processXML(source)

    if target == "-":
        print(graph.serialize(format=format))
    else:
        graph.serialize(destination=target, format=format)


def main():
    formatter = lambda prog: argparse.HelpFormatter(prog,max_help_position=50)
    parser = argparse.ArgumentParser(description="Convert LIDO to RDF using X3ML mapping", formatter_class=formatter)

    parser.add_argument("-o", '--output', metavar="NAME", dest="target",  default='-', help="RDF output file (default: -)")
    formats = ",".join(formatNames.keys())
    parser.add_argument("-t", '--to', dest="format", help=f"RDF output serialization ({formats})")
    parser.add_argument('-m', '--mapping', dest="mapping",  default='lido2rdf.x3ml', help="X3ML mapping file (default: lido2rdf.x3ml)")
    parser.add_argument('source', metavar='LIDO-XML', nargs="?", default="-", help='LIDO file or URL (default: -)')

    args = parser.parse_args()
    if args.source == "-" and stdin.isatty():
        parser.print_help()
    else:
        try:
            lido2rdf(args.source, args.target, args.mapping, args.format)
        except (HTTPError, URLError) as exception:
            error(exception)


if __name__ == "__main__":
    main()
