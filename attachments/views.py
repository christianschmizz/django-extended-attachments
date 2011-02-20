from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.db.models.loading import get_model
from django.db.models import F
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext, ugettext_lazy as _
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_protect
from attachments.models import Attachment, Thumbnail
from attachments.utils import serve_file
from attachments.forms import AttachmentForm, AttachmentUpdateForm
from attachments.settings import DEFAULT_ATTACHMENTS_PERM_CALLBACKS as PERMS


def add_url_for_obj(obj):
    return reverse('attachments:add', kwargs={
                        'app_label': obj._meta.app_label,
                        'module_name': obj._meta.module_name,
                        'pk': obj.pk
                    })


@csrf_protect
def add(request, app_label, module_name, pk,
        template_name='attachments/add_form.html',
        perm_callback=PERMS['add']):

    # TODO: check for proper applabel/modelname
    model = get_model(app_label, module_name)
    obj = get_object_or_404(model, pk=pk)

    # TODO: check for valid next attribute
    next = request.REQUEST.get('next') or '/'

    if not perm_callback(request, obj):
        return HttpResponseForbidden('Did\'t allowed upload attachments for this item')

    if request.method == 'POST':
        form = AttachmentForm(request.POST, request.FILES)
    else:
        form = AttachmentForm()

    if form.is_valid():
        form.save(request, obj)
        request.user.message_set.create(message=ugettext('Your attachment was uploaded.'))
        return HttpResponseRedirect(next)
    else:
        return render_to_response(template_name, {
                'form': form,
                'form_url': add_url_for_obj(obj),
                'next': next,
            },
            RequestContext(request))


@csrf_protect
def delete(request, pk,
           template_name='attachments/delete_form.html',
           perm_callback=PERMS['delete']):
    attachment = get_object_or_404(Attachment, pk=pk)
    next = request.REQUEST.get('next') or '/'

    if not perm_callback(request, attachment):
        return HttpResponseForbidden('Delete not allowed.')

    if request.method == 'POST':
        attachment.delete()
        request.user.message_set.create(message=ugettext('Your attachment was deleted.'))
        return HttpResponseRedirect(next)
    else:
        return render_to_response(template_name, {
            'form_url': reverse('attachments:delete', kwargs={'pk': pk}),
            'next': next},
            RequestContext(request))


@csrf_protect
def update(request, pk,
           template_name='attachments/update_form.html',
           perm_callback=PERMS['update']):

    attachment = get_object_or_404(Attachment, pk=pk)
    next = request.REQUEST.get('next') or '/'

    if request.method == 'POST':
        form = AttachmentUpdateForm(request.POST, request.FILE, instance=attachment)
    else:
        form = AttachmentUpdateForm(instance=attachment)

    if not perm_callback(request, attachment):
        return HttpResponseForbidden('Update not allowed.')

    if form.is_valid():
        form.save()
        request.user.message_set.create(message=ugettext('Your attachment was updated.'))
        return HttpResponseRedirect(next)
    else:
        return render_to_response(template_name, {
            'form': form,
            'form_url': reverse('attachments:update', kwargs={'pk': pk}),
            'next': next},
            RequestContext(request))


def download(request, pk,
             perm_callback=PERMS['download']):
    attachment = get_object_or_404(Attachment, pk=pk)

    if not perm_callback(request, attachment):
        return HttpResponseForbidden('Forbidden attachment.')

    attachment.download_count = F('download_count') + 1
    attachment.save()
    return serve_file(request, attachment.file,
                      attachment.name, attachment.mime_type)


def thumbnail(request, attachment_pk, width, height,
              perm_callback=PERMS['download']):
    attachment = get_object_or_404(Attachment, pk=attachment_pk)

    if not perm_callback(request, attachment):
        return HttpResponseForbidden('Forbidden attachment.')

    thumb = Thumbnail.objects.get_or_create(attachment, width, height)
    if thumb is None:
        raise Http404('Thumbnail can not be created')
    return serve_file(request, thumb.file, None, thumb.mime_type)
