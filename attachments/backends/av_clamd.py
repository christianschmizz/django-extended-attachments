# -*- coding: utf-8 -*-

from attachments.backends import AntivirusBase
from attachments.settings import ANTIVIRUS_CLAMD_HOST, \
        ANTIVIRUS_CLAMD_PORT, ANTIVIRUS_CLAMD_UNIX_SOCK
import pyclamd


class Antivirus(AntivirusBase):
    def __init__(self):
        if ANTIVIRUS_CLAMD_UNIX_SOCK:
            pyclamd.init_unix_socket(ANTIVIRUS_CLAMD_UNIX_SOCK)
        else:
            pyclamd.init_network_socket(ANTIVIRUS_CLAMD_HOST,
                                        ANTIVIRUS_CLAMD_PORT)

    def scan_file(self, filepath):
        found = pyclamd.scan_file(filepath)
        virus = found and '\n'.join(found.values()) or ''
        return found, virus

