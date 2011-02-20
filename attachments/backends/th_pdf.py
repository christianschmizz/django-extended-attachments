# -*- coding: utf-8 -*-

import os
import subprocess
from attachments.backends import ThumbnailerBase


class Thumbnailer(ThumbnailerBase):
    mime_types = (
        'application/pdf',
        'application/x-pdf',
    )

    def thumbnail(self, src_path, dst_path, width, heigth, mime_type):
        args = [
            'gm',
            'convert',
            '-quality', '85',
            '-colorspace', 'rgb',
            '-colors', '256',
            '-antialias',
            '-resize', '{w}x{h}'.format(w=width, h=heigth),
            'PDF:{src}[0]'.format(src=src_path),
            'PNG:{dst}'.format(dst=dst_path),
        ]

        proc = subprocess.Popen(args,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                env={'LANG': 'C'},
                               )
        out = proc.communicate()

        if out[0]:
            return (False, 'Convert error:'+out[1])

        if not os.path.isfile(dst_path):
            return (False, 'failed')

        return (True, 'image/png')

