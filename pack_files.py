import zipfile
import argparse
import math
from pathlib import Path


def partition_list(lst: list, part_size: int):
    '''Partition of a list to list of list of size n'''
    for i in range(0, len(lst), part_size):
        yield lst[i: i+part_size]


def zip_in_partitions(source_dir: str, num_parts: int, **options):
    '''Zips files in a directory to multiple zip files (partitions)'''
    logger = options.get('logger', None)
    parts_name = options.get('archive', 'archive')

    directory = Path(source_dir)
    if not directory.is_dir():
        raise FileNotFoundError(f"Directory '{source_dir}' does not exist")

    if num_parts <= 0:
        raise ValueError("Number of ZIPs must be positive")

    # Get sorted files (only files, not directories)
    files_sorted = sorted([f for f in directory.iterdir() if f.is_file()])
    part_size = math.ceil(len(files_sorted) / num_parts)
    files_parted = partition_list(files_sorted, part_size)
    # Zip patitions
    for i, part in enumerate(files_parted, start=1):
            zip_name = f'{parts_name}_{i:06d}.zip'
            if logger:
                logger(f'Creating {zip_name}')
            with zipfile.ZipFile(zip_name, 'w') as zip_f:
                for file in part:
                    zip_f.write(file, arcname=file.name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Pack files from directory into N ZIP files')
    parser.add_argument('dir', help='Directory to pack files from')
    parser.add_argument('-n', '--num', type=int, default=5, help='Number of ZIP files')
    parser.add_argument('-a', '--archname', default='archive', help='Basename of ZIP files')

    args = parser.parse_args()
    print(f'Creating {args.num} Zip file(s) from {args.dir}:')
    try:
        zip_in_partitions(args.dir, args.num, archive=args.archname, logger=print)
    except Exception as inst:
        print(f'Error: {inst}')
