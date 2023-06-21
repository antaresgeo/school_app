import os
import json
import pandas as pd
from django.db import models
from django.apps import apps
from django.utils import timezone
from django.core.mail import send_mail
from celery import shared_task, result
from .models import Import
from .validators import ModelValidator
from django.conf import settings

def run_next_step(step, import_instance, next_step=False):
    """
    Helper function to run the next step in the import process asynchronously.
    """
    if run_next_step:
        step_result = step.delay(import_instance.id, next_step)

        # while True:
        #     task_result = result.AsyncResult(step_result.task_id)
        #     if task_result.ready():
        #         break
        #
        #     time.sleep(1)


@shared_task
def start_import(import_id, next_step=False):
    """
    Task to start the import process.
    """
    import_instance = Import.objects.get(id=import_id)
    import_instance.status = 'in_progress'
    import_instance.step = 'start_import'
    import_instance.start_date = timezone.now()
    import_instance.save()

    run_next_step(get_import_data, import_instance, next_step)


@shared_task
def get_import_data(import_id, next_step=False):
    """
    Task to get the import data from the file.
    """
    import_instance = Import.objects.get(id=import_id)
    import_instance.step = 'get_import_data'
    import_instance.save()

    # File analysis
    file_url = import_instance.document.path

    if file_url and os.path.exists(file_url):
        file_name, file_type = os.path.splitext(file_url)

        # Import CSV file
        if file_type == '.csv':
            df = pd.read_csv(file_url)

        # Import XLS or XLSX file
        elif file_type == '.xls' or file_type == '.xlsx':
            df = pd.read_excel(file_url)

        else:
            error_msg = 'Invalid file type. Accepted file types are .csv, .xls, or .xlsx.'

            import_instance.imported_data = {'file_error': error_msg}
            import_instance.total_lines = 0
            import_instance.save()

            run_next_step(send_error_email, import_instance, next_step=True)

            return

        if any(item.startswith('Unnamed') for item in list(df.columns)):
            error_msg = """
Invalid file format detected. The file must meet the following requirements:

- The data should start from row 1 and column A.
- All columns with data must have their respective column names in row 1.

Please ensure that the file format is correct and meets the specified criteria. Unable to process the file.
"""
            import_instance.imported_data = {'file_error': error_msg}
            import_instance.total_lines = 0
            import_instance.save()

            run_next_step(send_error_email, import_instance, next_step=True)

            return

        # Getting file data
        json_str = df.to_json(orient='records')
        data = json.loads(json_str)

        import_instance.imported_data = {
            'headers': list(df.columns),
            'data': data,
        }
        import_instance.total_lines = len(data)
        import_instance.save()

        run_next_step(validate_import, import_instance, next_step)
    else:
        error_msg = 'A document was not found when trying to get the data.'

        import_instance.imported_data = {'file_error': error_msg}
        import_instance.total_lines = 0
        import_instance.save()

        run_next_step(send_error_email, import_instance, next_step=True)


@shared_task
def validate_import(import_id, next_step=False):
    """
    Task to validate the imported data.
    """
    import_instance = Import.objects.get(id=import_id)
    import_instance.step = 'validate_import'
    import_instance.save()

    model = apps.get_model(import_instance.model_name)
    validator = ModelValidator(model)

    imported_data = import_instance.imported_data

    validated_data = validator.validate_array(imported_data['data'])
    import_instance.imported_data = validated_data

    import_instance.save()

    if len(validated_data['invalids']) > 0:
        run_next_step(send_error_email, import_instance, next_step=True)
    else:
        run_next_step(create_records, import_instance, next_step)


@shared_task
def create_records(import_id, next_step=False):
    """
    Task to create records in the specified model using the valid imported data.
    """
    import_instance = Import.objects.get(id=import_id)
    import_instance.step = 'create_records'
    import_instance.save()

    model = apps.get_model(import_instance.model_name)

    # Check if imported_data is None
    imported_data = import_instance.imported_data
    if imported_data is None:
        run_next_step(send_error_email, import_instance, next_step=True)
        return

    # Get the valid imported data
    valid_data = imported_data.get('valids', [])

    # Create records in the model and increment imported_lines counter
    for item in valid_data:
        try:
            record_is_save = False
            record_data = {}
            for key, value in item["data"].items():
                field = model._meta.get_field(key)
                if field.is_relation:
                    related_model = field.related_model
                    record_data[key] = related_model.objects.get(id=value)
                else:
                    record_data[key] = value

            if model.fields_to_map:
                filtered_records = {}

                for key in model.fields_to_map.keys():
                    if key in record_data and isinstance(record_data[key], models.Model):
                        filtered_records[key] = record_data[key]

                # Check if a record with the same relations already exists
                existing_record = model.objects.filter(**filtered_records).first()

                if existing_record:
                    # Update the existing record
                    for key, value in record_data.items():
                        setattr(existing_record, key, value)

                    existing_record.save()

                    record_is_save = True

            if not record_is_save:
                # Create a new record
                record = model(**record_data)
                record.save()

            import_instance.imported_lines += 1
            import_instance.save()
        except Exception as e:
            # `Handle the error accordingly, for example, log it or send an error email`
            print(f"Error creating or updating record: {str(e)}")
            error_msg = 'f"Error creating or updating record: {str(e)}"'

            import_instance.imported_data = {**imported_data, 'creation_error': error_msg}
            import_instance.total_lines = 0
            import_instance.save()

            run_next_step(send_error_email, import_instance, next_step=True)

    import_instance.status = 'success'
    import_instance.end_date = timezone.now()
    import_instance.save()

    run_next_step(send_completion_email, import_instance, next_step)


@shared_task
def send_completion_email(import_id, next_step=False):
    """
    Task to send an email notification when the import process is completed successfully.
    """

    import_instance = Import.objects.get(id=import_id)

    subject = "Import Process Completed"
    message = f"The import process for Import ID {import_instance.id} ({import_instance.model_name}) has been completed successfully."
    from_email = settings.DEFAULT_FROM_EMAIL  # Use the default from email address from Django settings
    to_email = import_instance.created_by.email  # Use the email of the created_by user

    send_mail(subject, message, from_email, [to_email])


@shared_task
def send_error_email(import_id, next_step=False):

    """
    Task to send an email notification when the import process encounters an error.
    """
    import_instance = Import.objects.get(id=import_id)
    import_instance.status = "error"
    import_instance.end_date = timezone.now()
    import_instance.save()


    subject = "Import Error"
    message = f"An error occurred during the import process for Import ID {import_instance.id} ({import_instance.model_name}). Please review the details and take necessary actions."
    from_email = settings.DEFAULT_FROM_EMAIL  # Use the default from email address from Django settings
    to_email = import_instance.created_by.email  # Use the email of the created_by user

    send_mail(subject, message, from_email, [to_email])
