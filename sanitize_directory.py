#!/usr/bin/env python3

import argparse
import os
import sys

from sanitize import sanitize

def main():
    parser = argparse.ArgumentParser(
        description='Sanitize filenames in a directory for a specific filesystem.')
    parser.add_argument('directory', metavar='directory', type=str,
                        help='directory to sanitize')
    parser.add_argument('filesystem', metavar='filesystem', type=str,
                        help='target filesystem for which to sanitize')
    parser.add_argument('--match', metavar='match', type=str,
                        help='optional regex against which to match filenames')
    args = parser.parse_args()

    if not args.filesystem in sanitize.FILE_SYSTEMS:
        sys.stdout.write('Invalid file system.\n')
        return 1

    for os_tup in os.walk(args.directory):
        (os_dir, os_dirs, os_files) = os_tup
        for os_file in os_files:
            sanitized = sanitize.sanitize_filename(os_file, args.filesystem)
            sys.stdout.write('+--------------------------------------\n')
            sys.stdout.write('| original:  {0}\n'.format(os_file))
            sys.stdout.write('| sanitized: {0}\n'.format(sanitized))

if __name__ == '__main__':
    main()
