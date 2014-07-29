import argparse

from mpyq_print import (print_headers, print_hash_table,
                        print_block_table, print_files)

from mpyq_extract import extract_to_disk


description = "mpyq reads and extracts MPQ archives."
parser = argparse.ArgumentParser(description=description)
parser.add_argument("file", action="store", help="path to the archive")
parser.add_argument("-I", "--headers", action="store_true", dest="headers",
                    help="print header information from the archive")
parser.add_argument("-H", "--hash-table", action="store_true",
                    dest="hash_table", help="print hash table"),
parser.add_argument("-b", "--block-table", action="store_true",
                    dest="block_table", help="print block table"),
parser.add_argument("-s", "--skip-listfile", action="store_true",
                    dest="skip_listfile", help="skip reading (listfile)"),
parser.add_argument("-t", "--list-files", action="store_true", dest="list",
                    help="list files inside the archive")
parser.add_argument("-x", "--extract", action="store_true", dest="extract",
                    help="extract files from the archive")
args = parser.parse_args()

if args.file:
    if not args.skip_listfile:
        archive = MPQArchive(args.file)
    else:
        archive = MPQArchive(args.file, listfile=False)
    if args.headers:
        print_headers(archive)
    if args.hash_table:
        print_hash_table(archive)
    if args.block_table:
        print_block_table(archive)
    if args.list:
        print_files(archive)
    if args.extract:
        extract_to_disk(archive)
