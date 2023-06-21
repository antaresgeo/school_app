from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import User

STATUS_CHOICES = (
    ('created', 'Created'),
    ('in_progress', 'In progress'),
    ('success', 'Completed successfully'),
    ('error', 'Finished with error')
)

STEP_CHOICES = (
    ('start_import', 'Starting Import'),
    ('get_import_data', 'Getting data'),
    ('validate_import', 'Validating data'),
    ('create_records', 'Creating Records')
)


class Import(models.Model):
    model_name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    step = models.CharField(max_length=20, choices=STEP_CHOICES, null=True, blank=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    total_lines = models.IntegerField(null=True, blank=True)
    imported_lines = models.IntegerField(null=True, blank=True, default=0)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    imported_data = models.JSONField(null=True, blank=True)
    task_id = models.CharField(max_length=50, null=True, blank=True)
    document = models.FileField(
        upload_to='documents/',
        validators=[FileExtensionValidator(allowed_extensions=['csv', 'xls', 'xlsx'])],
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Import {self.model_name} - {self.get_status_display()}"
