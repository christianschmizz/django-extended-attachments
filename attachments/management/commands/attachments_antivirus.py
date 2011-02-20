# -*- coding: utf-8 -*-

import os
import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError
from attachments.models import Attachment


class Command(BaseCommand):
    help = 'Recheck all attachments using antivirus'
    args = ''

    def handle(self, *args, **options):
        for att in Attachment.objects.all():
            if att.make_check_av():
                print u'{att.name} ({att.file.path}) infected!'.format(att=att)
            att.save()
