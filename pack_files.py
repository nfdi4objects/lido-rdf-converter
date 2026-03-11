import os
import zipfile
import argparse
from pathlib import Path

def partition(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i : i+size]

def main():
    parser = argparse.ArgumentParser(description='Pack files from directory into N ZIP files')
    parser.add_argument('dir', help='Directory to pack files from')
    parser.add_argument('-n','--num', type=int, default=5, help='Number of ZIP files')
    parser.add_argument('-a','--archname', default='archive', help='Basename of ZIP files')
    args = parser.parse_args()

    directory = Path(args.dir)
    if not directory.is_dir():
        print("Directory does not exist")
        return

    num_zips = args.num
    if num_zips <= 0:
        print("#Zips must be positive")
        return
 
    # Get sorted files
    files = sorted(directory.iterdir())
    zip_size = 1 + len(files)//num_zips
    # Make partitions and zip them
    for i, part in enumerate(partition(files,zip_size),start=1):
        if not part:
            continue
        zip_name = f'{args.archname}_{i}.zip'
        with zipfile.ZipFile(zip_name, 'w') as zip_f:
            for file in part:
                zip_f.write(file)
        print(f'Created {zip_name}')

if __name__ == '__main__':
    main()