"""Create RDF LIDO XML files"""
from LidoHarvesterRDF import LidoHarvesterRDF
from lido2cidoc import getMapping
import argparse


ArgParser = argparse.ArgumentParser
ArgType = argparse.Namespace

def makeParser() -> ArgParser:
    ''' Makes an CLI argument parser'''
    parser = ArgParser()
    parser.add_argument("-u", '--url', dest="url", help="LIDO XML URL")
    parser.add_argument("-o", '--outfile', dest="outfile",  default='lido_out.ttl', help="RDF output file")
    parser.add_argument('-c', '--collection', dest="collection",  default='unknown', help="Gives a collection name")
    parser.add_argument('-m', '--mapping', dest="mappingFile",  default='lido_1.0_to_CIDOC_6.0.x3ml', help="X3ML mapping file")
    return parser


def main():

    def printv(*x):
        if progArgs.verbose:
            print(*x)

    parser = makeParser()
    progArgs = parser.parse_args()
    if progArgs:
        if progArgs.url is None:
            parser.print_help()
            parser.error("a repository url and output file are required")
        mappings = getMapping(progArgs.mappingFile)
        harvester = LidoHarvesterRDF(mappings, progArgs.collection)
        harvester.run(progArgs.url)
        harvester.store(progArgs.outfile)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
