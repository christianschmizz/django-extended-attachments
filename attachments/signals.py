# -*- coding: utf-8 -*-

import os
import models
from lib.helpers import signals

try:
    from dblogging import add_log
except ImportError:
    def add_log(*args, **kvargs): pass


@signals.post_save(sender=models.Attachment)
def attachment_saved(sender, instance, created, **kvargs):
    if created:
        instance.mime_type = instance.detect_mime()
        instance.make_checksum()
        instance.make_check_av()
        instance.save()

        # deduplication step
        dupfirst = models.Attachment.objects.filter(checksum=instance.checksum).order_by('id')[0]
        if dupfirst.id < instance.id:
            path=instance.file.path
            try:
                os.unlink(path)
                os.link(dupfirst.file.path, path)
                add_log('DEDUPLICATION',
                        item_id=instance.id,
                        first_id=dupfirst.id)
            except IOError, e:
                add_log('DEDUPLICATION_ERROR',
                        exception=e,
                        item_id=instance.id)
                with open(path, 'w') as fd:
                    fd.write(dupfirst.file.read())

