from django.db import models
from datetime import date
from django.conf import settings as s
import os

from django.core.files.storage import FileSystemStorage
fs = FileSystemStorage(location=s.TEMP_MEDIA_ROOT)


class Report(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    is_category = models.BooleanField(default=False)
    category = models.ForeignKey('self', null=True, blank=True, related_name='report_category')
    create_date = models.DateField(default=date.today, null=True)
    update_date = models.DateField(default=date.today, null=True)
    update_by = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField(default=False)
    report_pdf = models.FileField(null=True, blank=True, storage=fs)

    def delete(self, *args, **kwargs):
        if os.path.isfile(self.report_pdf.path):
            os.remove(self.report_pdf.path)

        super(Report, self).delete(*args, **kwargs)
