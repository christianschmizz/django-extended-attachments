# -*- coding: utf-8 -*-
"""
Attachments backends base classes
"""
from abc import abstractmethod


class AntivirusBase(object):
    @abstractmethod
    def scan_file(self, filename):
        """
        Scans file and return result tuple:
            - scan result: True -- infected, False -- not
            - antivirus report string
        """
        return (Fasle, '')


class ThumbnailerBase(object):
    """
    Thumbnailer base class.
    ``mime_types`` property describes what files can be processed.
    * -- means everything.
    """
    mime_types = (
        'image/jpeg',
        'image/png',
        'image/*',
    )

    @abstractmethod
    def thumbnail(self, src_path, dst_path, width, heigth, mime_type):
        """
        Generates thumbnail if it can and return result tuple:
            - status (True if success)
            - thumbnail mime type
        """
        return (False, 'image/jpeg')

