import json
import csv
from argparse import ArgumentParser

def lt_csv2json(fname):
    '''Converts a LIDO terminology csv file to a json string'''
    result = {}
    get_data = lambda x: f"crm:{x.get('CRM-Class', '').replace(' ', '_')}"
    with open(fname, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if uri := row.get('URI'):
                result.update({uri: get_data(row)})
    return json.dumps(result,indent=3)
    
if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('source', help='Converta a Lido terminology csv into json')
    args = parser.parse_args()
    if args.source:
        print(lt_csv2json(args.source))
    else:
        parser.print_help()
