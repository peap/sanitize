import unicodedata as ud

FILE_SYSTEMS = (
   'btrfs',
   'ext',
   'ext2',
   'ext3',
   'ext3cow',
   'ext4',
   'exfat',
   'fat32',
   'hfs+',
   'ntfs_win32',
   'reiser4',
   'reiserfs',
   'xfs',
   'zfs',
)


def sanitize_filename(filename, filesystem):

    sanitized_fragment = ud.normalize('NFC', filename)

    illegal_characters = {
        'btrfs': {'\0', '/'},
        'ext': {'\0', '/'},
        'ext2': {'\0', '/'},
        'ext3': {'\0', '/'},
        'ext3cow': {'\0', '/', '@'},
        'ext4': {'\0', '/'},
        'exfat': {
            '\00', '\01', '\02', '\03', '\04', '\05', '\06', '\07',
            '\10', '\11', '\12', '\13', '\14', '\15', '\16', '\17',
            '\20', '\21', '\22', '\23', '\24', '\25', '\26', '\27',
            '\30', '\31', '\32', '\33', '\34', '\35', '\36', '\37',
            '/', '\\', ':', '*', '?', '"', '<', '>', '|',
        },
        # TODO: Confirm this list; current list is just a wild guess,
        # assuming UTF-16 encoding.
        'fat32': {
            '\00', '\01', '\02', '\03', '\04', '\05', '\06', '\07',
            '\10', '\11', '\12', '\13', '\14', '\15', '\16', '\17',
            '\20', '\21', '\22', '\23', '\24', '\25', '\26', '\27',
            '\30', '\31', '\32', '\33', '\34', '\35', '\36', '\37',
            '/', '\\', ':', '*', '?', '"', '<', '>', '|',
        },
        # In theory, all Unicode characters, including NUL, are usable
        # (HFS+ is awesome in this way); so this is just a sane set for
        # legacy compatibility
        'hfs+': {'\0', '/', ':'},
        # NTFS Win32 namespace (which is stricter)
        'ntfs_win32': {'\0', '/', '\\', ':', '*', '?', '"', '<', '>', '|'},
        # NTFS POSIX namespace (which allows more characters)
        'ntfs_posix': {'\0', '/'},
        'reiser4': {'\0', '/'},
        'reiserfs': {'\0', '/'},
        'xfs': {'\0', '/'},
        'zfs': {'\0', '/'},
    }

    # Replace illegal characters with an underscore
    for character in illegal_characters[filesystem]:
        sanitized_fragment = sanitized_fragment.replace(character, '_')

    # Truncate if the resulting string is too long
    max_lengths = {
        # For the entries of file systems commonly found with Linux,
        # the length, 'utf-8', and 'NFC' are only assumptions that
        # apply to mostly vanilla kernels with default build
        # parameters.
        # Seriously, this is 2013. The fact that the Linux community
        # does not move to a file system with an enforced Unicode
        # filename encoding is as bad as Windows 95's codepage madness,
        # some 18 years ago.
        # If you add more file systems, see if it is affected by
        # Unicode Normal Forms, like HFS+; You may have to take extra
        # care in editing the actual sanitization routine below.
        'btrfs': (255, 'bytes', 'utf-8', 'NFC'),
        'ext': (255, 'bytes', 'utf-8', 'NFC'),
        'ext2': (255, 'bytes', 'utf-8', 'NFC'),
        'ext3': (255, 'bytes', 'utf-8', 'NFC'),
        'ext3cow': (255, 'bytes', 'utf-8', 'NFC'),
        'ext4': (255, 'bytes', 'utf-8', 'NFC'),
        'exfat': (255, 'characters', 'utf-16', 'NFC'),
        # 'utf-16' is not entirely true. FAT32 used to be used with
        # codepages; but since Windows XP, the default seems to be
        # UTF-16.
        'fat32': (255, 'characters', 'utf-16', 'NFC'),
        # FIXME: improve HFS+ handling, because it does not use the
        # standard NFD. It's close, but it's not exactly the same
        # thing.
        'hfs+': (255, 'characters', 'utf-16', 'NFD'),
        'ntfs_win32': (255, 'characters', 'utf-16', 'NFC'),
        'ntfs_posix': (255, 'characters', 'utf-16', 'NFC'),
        # I don't care if Linux can't support >255 bytes. The adoption
        # of filenames longer than 255 bytes is long overdue.
        'reiser4': (3976, 'bytes', 'utf-8', 'NFC'),
        'reiserfs': (4032, 'bytes', 'utf-8', 'NFC'), # Same here.
        'xfs': (255, 'bytes', 'utf-8', 'NFC'),
        'zfs': (255, 'bytes', 'utf-8', 'NFC'),
    }

    if max_lengths[filesystem][1] == 'bytes':
        temp_fragment_bytes = bytearray()
        for character in sanitized_fragment:
            normalized_bytes = ud.normalize(max_lengths[filesystem][3], character)
            encoded_bytes = normalized_bytes.encode(max_lengths[filesystem][2])
            if len(temp_fragment_bytes + encoded_bytes) <= max_lengths[filesystem][0]:
                temp_fragment_bytes.extend(encoded_bytes)
            else:
                break
        sanitized_fragment = ud.normalize(
            'NFC',
            temp_fragment_bytes.decode(max_lengths[filesystem][2])
        )
    # Assume 'characters'
    else:
        temp_fragment = ''
        if filesystem == 'hfs+':
            normalize = ud.ucd_3_2_0.normalize
        else:
            normalize = ud.normalize
        for character in sanitized_fragment:
            normalized_character = normalize(max_lengths[filesystem][3], character)
            if len(temp_fragment + normalized_character) <= max_lengths[filesystem][0]:
                temp_fragment += normalized_character
            else:
                break
        sanitized_fragment = ud.normalize('NFC', temp_fragment)

    return sanitized_fragment
