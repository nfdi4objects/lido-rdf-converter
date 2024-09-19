"""Converts LIDO file to RDF """
from LidoHarvesterRDF import LidoHarvesterRDF
from lido2cidoc import getMapping
import argparse

''' Some Type aliases'''
ArgParser = argparse.ArgumentParser
ArgType = argparse.Namespace

_suffix2Format = {'xml': 'xml', 'ttl': 'turtle', 'json': 'json-ld',
                  'n3': 'n3', 'trig': 'trig', 'trix': 'trix',
                  'nquads': 'nquads', 'turtle': 'turtle'}

def getFmt(fname):
    suff = fname.split('.')[-1]
    return _suffix2Format.get(suff, 'turtle')


def makeParser() -> ArgParser:
    ''' Makes an CLI argument parser'''
    parser = ArgParser()
    parser.add_argument("-u", '--url', dest="url", help="LIDO XML URL")
    parser.add_argument("-o", '--outfile', dest="outfile",  default='-', help="RDF output file")
    parser.add_argument("-t", '--to', dest="to", help="RDF output serialization")
    parser.add_argument('-c', '--collection', dest="collection",  default='unknown', help="Gives a collection name")
    parser.add_argument('-m', '--mapping', dest="mappingFile",  default='lido_1.0_to_CIDOC_6.0.x3ml', help="X3ML mapping file")
    return parser

def main():
    ''' Applies x3ml mapping to a Lido file'''
    parser = makeParser()
    progArgs = parser.parse_args()
    if progArgs:
        if progArgs.url is None:
            parser.print_help()
            parser.error("a repository file url is required")
        mappings = getMapping(progArgs.mappingFile)
        harvester = LidoHarvesterRDF(mappings)
        harvester.processURL(progArgs.url)
        outfile = progArgs.outfile
        fmt = progArgs.to or getFmt(outfile)
        graph = harvester.result()
        graph.serialize(destination=outfile, format=fmt)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
