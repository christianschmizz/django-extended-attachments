# -*- coding: utf-8 -*-

import os
import sys
from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError
from attachments.models import Attachment


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--out', '-o', default=None, help='output file'),
    )
    help = 'Generate sha1sum list for attachments'
    args = ''

    def handle(self, *args, **options):
        oflname = options['out']
        if oflname:
            ofd = open(oflname, 'w')
        else:
            ofd = sys.stdout

        for att in Attachment.objects.all():
            if not att.checksum or att.checksum == '!':
                att.make_checksum()
                att.save()

            ofd.write(att.checksum)
            ofd.write('  ')
            ofd.write(att.file.path)
            ofd.write('\n')
            att.file.close()
