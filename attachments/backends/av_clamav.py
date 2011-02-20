# -*- coding: utf-8 -*-

from attachments.backends import AntivirusBase
import pyclamav


class Antivirus(AntivirusBase):
    def scan_file(self, filepath):
        found, virus = pyclamav.scanfile(filepath)
        return found, virus

