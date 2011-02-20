# -*- coding: utf-8 -*-

import os
import subprocess
from attachments.backends import ThumbnailerBase


class Thumbnailer(ThumbnailerBase):
    mime_types = (
        'image/*',
    )

    def thumbnail(self, src_path, dst_path, width, heigth, mime_type):
        _, src_format = mime_type.split('/', 1)
        if src_format == 'png':
            save_format = 'PNG'
            save_mime = 'image/png'
        elif src_format == 'gif':
            save_format = 'GIF'
            save_mime = 'image/gif'
        else:
            save_format = 'JPEG'
            save_mime = 'image/jpeg'

        args = [
            'gm',
            'convert',
            '-quality', '85',
            '-colorspace', 'rgb',
            '-colors', '256',
            '-antialias',
            '-resize', '{w}x{h}'.format(w=width, h=heigth),
            '{src}'.format(src=src_path),
            '{format}:{dst}'.format(format=save_format, dst=dst_path),
        ]

        proc = subprocess.Popen(args,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                env={'LANG': 'C'},
                               )
        out = proc.communicate()

        if out[0]:
            return (False, 'gm convert error:'+out[1])

        if not os.path.isfile(dst_path):
            return (False, 'failed')

        return (True, save_mime)

