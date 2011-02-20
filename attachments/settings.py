# -*- coding: utf-8 -*-

from django.conf import settings

#
# Antivirus
#

ANTIVIRUS_BACKEND = getattr(settings, 'ANTIVIRUS_BACKEND', 'attachments.backends.av_clamav')

ANTIVIRUS_CLAMD_UNIX_SOCK = getattr(settings, 'ANTIVIRUS_CLAMD_UNIX_SOCK', '/var/run/clamav/clamd.ctl')
ANTIVIRUS_CLAMD_HOST = getattr(settings, 'ANTIVIRUS_CLAMD_HOST', '127.0.0.1')
ANTIVIRUS_CLAMD_PORT = getattr(settings, 'ANTIVIRUS_CLAMD_PORT', 3310)

#
# Thumbnail
#

THUMBNAIL_BACKENDS = getattr(settings, 'THUMBNAIL_BACKENDS', ('attachments.backends.th_pil',))

#
# Serve file
#

SERVE_FILE_BACKEND = getattr(settings, 'SERVE_FILE_BACKEND', 'attachments.backends.dl_default')

#
# ACL callbacks
#

def check_perm_attach_factory(perm_mod, perm_user):
    """
    Generates checker function that
    check's attachment permission
    that it can be updated/deleted/downloaded

    `perm_mod` -- global permission key
    'perm_user` -- user permission key

    check_perm:
    `request` -- view request
    `attachment` -- attachment instance
    """

    if perm_mod is not None:
        def check_perm(request, attachment):
            return request.user.has_perm(perm_mod) or \
                    (request.user == attachment.user and request.user.has_perm(perm_user))
    else:
        def check_perm(request, attachment):
            return request.user.has_perm(perm_user)
    return check_perm

def check_perm_object(request, object_):
    """
    Check permission for `object_` that attachment can be added

    `request` -- view request
    `object_` -- object that handle new attachment
    """
    return request.user.has_perm('add_attachment')

DEFAULT_ATTACHMENTS_PERM_CALLBACKS = {
    'add': check_perm_object,
    'delete': check_perm_attach_factory('delete_foreign_attachment', 'delete_attachment'),
    'update': check_perm_attach_factory('change_foreign_attachment', 'change_attachment'),
    'download': check_perm_attach_factory(None, 'download_attachment'),
}

DEFAULT_ATTACHMENTS_PERM_CALLBACKS.update(getattr(settings, 'ATTACHMENTS_PERM_CALLBACKS', {}))

