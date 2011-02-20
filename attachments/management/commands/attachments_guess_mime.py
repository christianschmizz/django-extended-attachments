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
        make_option('--all', '-a', default=False, help='all attachments'),
    )
    help = 'Try to guess attachments mime types'
    args = ''

    def handle(self, *args, **options):
        all_rows = options['all']

        if all_rows:
            query = Attachment.objects.all()
        else:
            query = Attachment.objects.filter(mime_type='application/octet-stream')

        for att in query:
            att.mime_type = att.detect_mime()
            att.save()
            att.file.close()
