# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext_lazy as _
from models import Attachment, Thumbnail
from django import forms


class AttachmentInlines(generic.GenericStackedInline):
    model = Attachment
    extra = 1


class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created', 'mime_type', 'size', 'av_state')
    list_filter = ('av_state', 'mime_type')
    search_fields = ('name', 'user', 'mime_type')
    readonly_fields = ('hash', 'size', 'checksum')
    fieldsets = (
        (None, {
            'fields': ('user', 'created'),
        }),
        (_('Relations'), {
            'fields': ('content_type', 'object_id'),
        }),
        (_('Attachment'), {
            'fields': ('hash', 'name', 'description', 'file', 'size', 'mime_type'),
        }),
        (_('Antivirus'), {
            'fields': ('av_state', 'av_result'),
        }),
        (_('Statistics'), {
            'fields': ('download_count', ),
        }),
        (_('Extra'), {
            'fields': ('checksum', 'thumbnail')
        }),
    )


class ThumbnailAdmin(admin.ModelAdmin):
    list_display = ('attachment', 'width', 'height')

admin.site.register(Attachment, AttachmentAdmin)
admin.site.register(Thumbnail, ThumbnailAdmin)
