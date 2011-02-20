# -*- coding: utf-8 -*-

import os
import subprocess
from attachments.settings import ANTIVIRUS_BACKEND, \
        THUMBNAIL_BACKENDS, SERVE_FILE_BACKEND
from django.utils.importlib import import_module
from django.utils.translation import ugettext_lazy as _


antivirus = getattr(import_module(ANTIVIRUS_BACKEND), 'Antivirus')()
serve_file = getattr(import_module(SERVE_FILE_BACKEND), 'serve_file')


def detect_mime(filepath):
    """detect mime using system `file` program"""
    proc = subprocess.Popen(['file', '--mime-type', '-b', filepath],
                            stdout=subprocess.PIPE)
    out = proc.communicate()
    return out[0].strip()


def humanize_filesize(size):
    if size < 1024:
        return _('%d B') % (size, )
    elif size < 1024**2:
        return _('%d KiB') % (size/1024, )
    elif size < 1024**3:
        return _('%.2f MiB') % (size/(1024.0**2), )
    elif size < 1024**4:
        return _('%.2f GiB') % (size/(1024.0**3), )
    else:
        return _('%.2f TiB') % (size/(1024.0**4), )


class ThumbnailGenerator(object):
    _thumbnailers = {}

    class ThumbnailerDoesNotExist(Exception):
        pass

    def __init__(self, module_name_list):
        self.load(module_name_list)

    def load(self, module_name_list):
        self._thumbnailers = {}
        for th_module in module_name_list:
            th = getattr(import_module(th_module), 'Thumbnailer')()
            for mime_type in th.mime_types:
                if self._thumbnailers.has_key(mime_type):
                    self._thumbnailers[mime_type].append(th)
                else:
                    self._thumbnailers[mime_type] = [th]

    def get_list(self, mime_type):
        th_list = []
        file_class, format = mime_type.split('/', 1)
        if self._thumbnailers.has_key(mime_type):
            th_list += self._thumbnailers[mime_type]
        if _thumbnailers.has_key(klass+'/*'):
            th_list += _thumbnailers[klass+'/*']
        if not th_list:
            raise self.ThumbnailerDoesNotExist(mime_type)
        return th_list

    def __call__(self, src_path, dst_path, width, heigth, mime_type):
        try:
            th_list = self.get_list(mime_type)
        except self.ThumbnailerDoesNotExist, e:
            return (False, 'Thumbnailer for %s does not exist' % e)

        for th in th_list:
            status, mime = th.thumbnail(src_path, dst_path, width, heigth, mime_type)
            if status:
                return (status, mime)

        return (False, 'All thumbnailers return false')


create_thumbnail = ThumbnailGenerator(THUMBNAIL_BACKENDS)

