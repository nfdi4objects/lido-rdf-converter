import os
import zipfile
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='Pack files from directory into N ZIP files')
    parser.add_argument('-d', '--dir', default='rdfData', help='Directory to pack files from')
    parser.add_argument('-n','--num', type=int, default=5, help='Number of ZIP files')
    parser.add_argument('-a','--archname', default='archive', help='Basename of ZIP files')
    args = parser.parse_args()

    if not os.path.isdir(args.dir):
        print("Directory does not exist")
        return

    if args.num <= 0:
        print("N must be positive")
        return

    files = []
    for root, dirs, filenames in os.walk(args.dir):
        for filename in filenames:
            files.append(os.path.join(root, filename))

    if not files:
        print("No files found")
        return

    # Split in N groups
    groups = [[] for _ in range(args.num)]
    for i, file in enumerate(files):
        groups[i % args.num].append(file)

    for i, group in enumerate(groups):
        if not group:
            continue
        zip_name = f'{args.archname}_{i+1}.zip'
        with zipfile.ZipFile(zip_name, 'w') as zipf:
            for file in group:
                #arcname = os.path.relpath(file, args.dir) # as archive fname
                zipf.write(file)
        print(f'Created {zip_name}')

if __name__ == '__main__':
    main()