# -*- coding: utf-8 -*-
import os
import tempfile
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import CreationDateTimeField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.hashcompat import sha_constructor, md5_constructor
from django.conf import settings
from django.core.files.images import ImageFile
from django.utils.encoding import smart_str
from django.contrib.auth.models import User
from attachments.utils import antivirus, detect_mime, create_thumbnail, humanize_filesize


FILE_STANDING = 0
FILE_VIRUS_NOT_FOUND = 1
FILE_VIRUS_FOUND = 2

FILE_STATUS_CHOICES = (
        (FILE_STANDING,        _('Standing')),
        (FILE_VIRUS_NOT_FOUND, _('Virus not found')),
        (FILE_VIRUS_FOUND,     _('Virus found')),
)


class AttachmentManager(models.Manager):
    def attachments_for_object(self, obj):
        object_type = ContentType.objects.get_for_model(obj)
        return self.filter(content_type__pk=object_type.id,
                           object_id=obj.id)


class Attachment(models.Model):
    """
    Attachment model
    """
    def file_upload_to(instance, filename):
        if not instance.hash:
            instance.make_hash()
        return 'attachments/{hash_byte[0]}/{hash_byte[1]}/{hash_byte[2]}/{user_id}_{hash}'.format(
            hash=instance.hash,
            hash_byte=instance.get_hash_3(),
            user_id=instance.user.id,
        )

    objects = AttachmentManager()

    content_type = models.ForeignKey(ContentType, verbose_name=_('Content Type'), help_text=_('relation to model wich instance is own this attachment'))
    object_id = models.PositiveIntegerField(_('Object ID'), help_text=_('ID of object row'))
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    hash = models.CharField(_('search hash'), max_length=40, unique=True, db_index=True)
    user = models.ForeignKey(User, related_name='attachments', verbose_name=_('user'))
    name = models.CharField(_('real file name'), max_length=255)
    description = models.TextField(_('description'), blank=True, help_text=_('attachment description'))
    mime_type = models.CharField(_('MIME type'), max_length=128, default='application/octet-stream')
    file = models.FileField(_('attachment'), upload_to=file_upload_to)
    size = models.PositiveIntegerField(_('file size'), blank=True, default=0)
    download_count = models.PositiveIntegerField(_('download count'), default=0)
    created = CreationDateTimeField(_('Created'), editable=True)

    av_state = models.PositiveIntegerField(_('avntivirus state'), default=FILE_STANDING, choices=FILE_STATUS_CHOICES)
    av_result = models.TextField(_('antivirus report'), blank=True)

    checksum = models.CharField(_('checksum'), max_length=40, blank=True, help_text=_('SHA1 checksum'))
    thumbnail = models.BooleanField(_('can generate thumbnails'), default=True)

    class Meta:
        ordering = ['-created']
        verbose_name = _('attachment')
        verbose_name_plural = _('attachments')
        permissions = (
            ('delete_foreign_attachment', 'Can delete foreign attachment'),
            ('change_foreign_attachment', 'Can change foreign attachment'),
            ('download_attachment', 'Can download attachment'),
        )


    class ChecksumDoesNotExist(Exception):
        pass


    def __unicode__(self):
        return u'{self.name} uloaded by {self.user.username}'.format(self=self)

    def save(self, *args, **kvargs):
        if not self.id:
            self.set_file(self.file)
        super(Attachment, self).save(*args, **kvargs)

    @models.permalink
    def get_absolute_url(self):
        return ('attachments:download', [self.id])

    def make_hash(self):
        self.hash = md5_constructor(smart_str(self.name) +
                                    smart_str(self.created.strftime('%s')) +
                                    smart_str(self.user.username)).hexdigest()

    def get_hash_3(self):
        """return tuple of first three bytes of search hash"""
        return self.hash[0:2], self.hash[2:4], self.hash[4:6]

    def set_file(self, fl):
        self.name = os.path.basename(fl.name)
        self.size = fl.size
        self.file = fl
        self.make_hash()

    def make_checksum(self):
        self.checksum = sha_constructor(self.file.read()).hexdigest()

    def check_file(self):
        if self.checksum:
            csum = sha_constructor(self.file.read()).hexdigest()
            return self.checksum == csum
        else:
            raise self.ChecksumDoesNotExist('for row {self.id} file {self.file}'.format(self=self))

    def make_check_av(self):
        res, val = antivirus.scan_file(self.file.path)
        if res:
            self.av_state = FILE_VIRUS_FOUND
            self.av_result = val
        else:
            self.av_state = FILE_VIRUS_NOT_FOUND
        return res

    def detect_mime(self):
        """detect mime using system `file` program"""
        return detect_mime(self.file.path)

    def get_size_display(self):
        return humanize_filesize(self.size)


class ThumbnailManager(models.Manager):
    def get_or_create(self, attachment, width, height):
        try:
            th = self.get(attachment=attachment, width=width, height=height)
        except self.model.DoesNotExist:
            th = self.create_for_attachment(attachment, width, height)
        return th


    def create_for_attachment(self, attachment, width, height):
        """
        Create Thumbnail object and save it if thumbnailer backend can generate thumbnail for this file.
        If not — return None.
        """
        if not attachment.thumbnail:
            return None

        th = self.model(attachment=attachment, width=width, height=height)
        with tempfile.NamedTemporaryFile(suffix='.thumb') as tfd:
            tfd.file.close()
            status, mime_type = create_thumbnail(attachment.file.path,
                                                 tfd.name,
                                                 width, height,
                                                 attachment.mime_type)
            if status:
                th.mime_type = mime_type
                th.file = ImageFile(open(tfd.name))
                th.save()
            else:
                attachment.thumbnail = False
                attachment.save()
                return None

        return th


class Thumbnail(models.Model):
    def file_upload_to(instance, filename):
        return 'attachments/thumb/{hash_byte[0]}/{hash_byte[1]}/{hash_byte[2]}/{user_id}_{width}x{height}_{hash}'.format(
            hash=instance.attachment.hash,
            hash_byte=instance.attachment.get_hash_3(),
            user_id=instance.attachment.user.id,
            width=instance.width,
            height=instance.height,
        )

    objects = ThumbnailManager()

    created = CreationDateTimeField(_('created'), blank=True, editable=True)
    attachment = models.ForeignKey(Attachment, related_name='thumbnails', verbose_name=_('attachment'), help_text=_('thumbnail for this attachment'))
    width = models.PositiveIntegerField(_('width'), db_index=True)
    height = models.PositiveIntegerField(_('height'), db_index=True)
    file = models.ImageField(_('thumbnail'), upload_to=file_upload_to)
    mime_type = models.CharField(_('MIME type'), max_length=128, default='image/jpeg')

    class Meta:
        ordering = ('-created', 'attachment__id')
        verbose_name = _('thumbnail')
        verbose_name_plural = _('thumbnails')
        unique_together = ('attachment', 'width', 'height')

    def __unicode__(self):
        return u'for {self.attachment.name} {self.width}x{self.height}'.format(self=self)

    @models.permalink
    def get_absolute_url(self):
        return ('attachments:thumbnail', (self.attachment_id, self.width, self.height))


from attachments import signals

