from django.contrib import admin
from .models import Import


@admin.register(Import)
class ImportAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'model_name',
        'status',
        'step',
        'imported_lines',
        'total_lines',
        'start_date',
        'end_date'
    ]
