import os
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Import
from .tasks import start_import


# @receiver(post_save, sender=Document)
# def check_document(sender, instance, created, **kwargs):
#     if created:
#         Model = instance.__class__
#
#         metadata = Model._meta
#
#         fields = metadata.get_fields()
#
#         for field in fields:
#             if field.is_relation:
#                 print(field.name, field.related_model)
#                 print(field.related_model._meta.get_fields())


@receiver(post_save, sender=Import)
def on_import_create(sender, instance, created, **kwargs):
    if created:
        result = start_import.delay(instance.id, next_step=True)
        instance.task_id = result.task_id
        instance.save()



@receiver(post_delete, sender=Import)
def on_import_delete(sender, instance, **kwargs):
    if instance.document:
        file_path = instance.document.path

        if file_path and os.path.exists(file_path):
            os.remove(file_path)
