from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from attachments.models import Attachment


class AttachmentForm(forms.ModelForm):
    file = forms.FileField()
    description = forms.CharField(required=False, widget=forms.Textarea)

    class Meta:
        model = Attachment
        fields = ('file', 'description')

    def save(self, request, obj, *args, **kwargs):
        self.instance.user = request.user
        self.instance.content_object = obj
        self.instance.set_file(self.cleaned_data['file'])
        super(AttachmentForm, self).save(*args, **kwargs)


class AttachmentUpdateForm(forms.ModelForm):
    description = forms.CharField(required=False, widget=forms.Textarea)

    class Meta:
        model = Attachment
        fields = ('description', )

