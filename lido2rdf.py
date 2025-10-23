#!/usr/bin/env python

"""Converts LIDO file to RDF """

import re
import argparse
from sys import stdin, stderr, exit
from io import BytesIO
from urllib.error import HTTPError, URLError
from pathlib import Path
from LidoRDFConverter import LidoRDFConverter

VERSION = "0.1.0"

SUFFIX_FORMAT_MAP = {'ttl': 'turtle', 'nt': 'nt', 'json': 'json-ld', 'xml': 'xml'}
'''Maps file suffixes to formats'''


def error(msg):
    '''Prints an error message and exits'''
    print(msg, file=stderr)
    exit(1)


def getValidFormat(format_str, file_name) -> str:
    '''Returns a valid format string'''
    suffix = format_str or Path(file_name).suffix.strip('.')
    return SUFFIX_FORMAT_MAP.get(suffix, 'nt')


def lido2rdf(input, mapping_file, **kw) -> LidoRDFConverter.Graph | None:
    '''Applies a x3ml mapping to a LIDO file'''
    converter = LidoRDFConverter(mapping_file)
    isRessource = lambda s: re.compile("^(https?|file):").match(s)
    if isRessource(input):
        return converter.process_url(input, **kw)
    else:
        if input == "-":
            input = BytesIO()
            input.write(stdin.buffer.read())
            input.seek(0)
        return converter.parse_file(input)[0]


def cli_convert():
    def apFormatter(prog):
        return argparse.HelpFormatter(prog, max_help_position=50)

    parser = argparse.ArgumentParser(
        prog="lido2rdf", description=f"Convert LIDO to RDF using X3ML mapping (version={VERSION})", formatter_class=apFormatter)

    formats = ",".join(SUFFIX_FORMAT_MAP.keys())
    parser.add_argument("-o", '--output', metavar="NAME", dest="target",
                        default='/dev/stdout', help="RDF output file (default: -)")
    parser.add_argument("-t", '--to', dest="format",
                        help=f"RDF output format ({formats})")
    parser.add_argument('-m', '--mapping', dest="mapping", default='defaultMapping.x3ml',
                        help="X3ML mapping file (default: defaultMapping.x3ml)")
    parser.add_argument('source', metavar='LIDO-XML', nargs="?",
                        default="-", help='LIDO file or URL (default: -)')
    parser.add_argument('--rdf-folder', metavar="NAME", dest="rdf_folder",
                        default='rdfData', help="RDF output folder for OAI-PMH processing (default: rdfData)")

    args = parser.parse_args()
    if args.source == "-" and stdin.isatty():
        parser.print_help()
    else:
        try:
            format = getValidFormat(args.format, args.target)
            if graph := lido2rdf(args.source, args.mapping, suffix=args.format, format=format, rdf_folder=args.rdf_folder):
                graph.serialize(destination=args.target, format=format, encoding='utf-8')
        except (HTTPError, URLError) as exception:
            error(exception)


if __name__ == "__main__":
    cli_convert()
