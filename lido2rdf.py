#!/usr/bin/env python

"""Converts LIDO file to RDF """

import re
import argparse
from sys import stdin, stderr, exit
from io import BytesIO
from urllib.error import HTTPError, URLError
from pathlib import Path
from LidoRDFConverter import LidoRDFConverter

SCHEMA_RE = re.compile("^(https?|file):")

SUFFIX_FORMAT_MAP = {'ttl': 'turtle',
                     'nt': 'nt', 'json': 'json-ld', 'xml': 'xml'}
'''Maps file suffixes to formats'''


def error(msg):
    '''Prints an error message and exits'''
    print(msg, file=stderr)
    exit(1)


def getValidFormat(formatStr, fileName):
    '''Returns a valid format string'''
    suffix = formatStr or Path(fileName).suffix.strip('.')
    return SUFFIX_FORMAT_MAP.get(suffix, 'nt')


def lido2rdf(source, mapping):
    '''Applies a x3ml mapping to a LIDO file'''
    converter = LidoRDFConverter(mapping)
    if SCHEMA_RE.match(source):
        return converter.process_url(source, rdf_folder='rdfData')
    else:
        if source == "-":
            source = BytesIO()
            source.write(stdin.buffer.read())
            source.seek(0)
        g, _ = converter.parse_file(source)
        return g


VERSION = "0.1.0"


def main():
    def apFormatter(prog):
        return argparse.HelpFormatter(prog, max_help_position=50)

    parser = argparse.ArgumentParser(
        prog="lido2rdf", description=f"Convert LIDO to RDF using X3ML mapping (version={VERSION})", formatter_class=apFormatter)

    formats = ",".join(SUFFIX_FORMAT_MAP.keys())
    parser.add_argument("-o", '--output', metavar="NAME", dest="target",
                        default='-', help="RDF output file (default: -)")
    parser.add_argument("-t", '--to', dest="format",
                        help=f"RDF output format ({formats})")
    parser.add_argument('-m', '--mapping', dest="mapping", default='defaultMapping.x3ml',
                        help="X3ML mapping file (default: defaultMapping.x3ml)")
    parser.add_argument('source', metavar='LIDO-XML', nargs="?",
                        default="-", help='LIDO file or URL (default: -)')

    args = parser.parse_args()
    if args.source == "-" and stdin.isatty():
        parser.print_help()
    else:
        try:
            if graph := lido2rdf(args.source, args.mapping):
                formatStr = getValidFormat(args.format, args.target)
                # Process result graph
                if args.target == "-":
                    print(graph.serialize(format=formatStr))
                else:
                    graph.serialize(destination=args.target,
                                    format=formatStr, encoding='utf-8')
        except (HTTPError, URLError) as exception:
            error(exception)


if __name__ == "__main__":
    main()
