#!/usr/bin/env python3

import argparse
import os
import sys

from sanitize import sanitize

def main():
    parser = argparse.ArgumentParser(
        description='Sanitize filenames in a directory for a specific filesystem.'
    )
    parser.add_argument(
        'directory', metavar='directory', type=str,
        help='directory to sanitize'
    )
    parser.add_argument(
        'filesystem', metavar='filesystem', type=str,
        help='target filesystem for which to sanitize'
    )
    parser.add_argument(
        '--testdir', metavar='testdir', type=str,
        help='directory to place output (empty files), for testing'
    )
    parser.add_argument(
        '--match', metavar='match', type=str,
        help='optional regex against which to match filenames'
    )
    parser.add_argument(
        '-v', dest='verbose', action='store_true',
        help='more descriptive output'
    )
    args = parser.parse_args()

    # check filesystem
    if not args.filesystem in sanitize.FILE_SYSTEMS:
        sys.stdout.write('Invalid file system.\n')
        return 1

    for os_tup in os.walk(args.directory):
        (os_dir, os_dirs, os_files) = os_tup
        in_dir = os.path.basename(os_dir)
        san_dir = sanitize.sanitize_filename(in_dir, args.filesystem)
        out_dir = os.path.join(os.path.dirname(os_dir), san_dir)
        if args.verbose:
            sys.stdout.write('+--------------------------------------\n')
            sys.stdout.write('| original:  {0}\n'.format(os_dir))
            sys.stdout.write('| sanitized: {0}\n'.format(out_dir))
        for os_file in os_files:
            in_file = os.path.join(out_dir, os_file)
            sanitized = sanitize.sanitize_filename(os_file, args.filesystem)
            out_file = os.path.join(out_dir, sanitized)
            if args.verbose:
                sys.stdout.write('+--------------------------------------\n')
                sys.stdout.write('| original:  {0}\n'.format(in_file))
                sys.stdout.write('| sanitized: {0}\n'.format(out_file))
    sys.stdout.write('+--------------------------------------\n')

if __name__ == '__main__':
    main()
