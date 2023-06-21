import pandas as pd
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import path, include
from django.views.generic import RedirectView
from .forms import ImportForm
from .models import Import


def generate_importer(model, name=None):
    @login_required
    def importer_view(request):
        """
        View function for the importer page.

        Handles the importing of data for a specific model.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            HttpResponse: The HTTP response object rendering the importer.html template.
        """
        if request.method == 'POST':
            form = ImportForm(request.POST, request.FILES)
            if form.is_valid():
                import_instance = form.save(commit=False)
                import_instance.model_name = model._meta.label
                import_instance.created_by = request.user
                import_instance.save()

                return HttpResponseRedirect(request.path_info)
        else:
            form = ImportForm()

        imports = Import.objects.filter(created_by=request.user, model_name=model._meta.label).order_by('id')

        return render(request, 'importer.html', {
            'form': form,
            'imports': imports,
            'model_name': model.__name__,
            'namespace': name
        })

    def import_view(request, import_id):
        """
        View function for the import detail page.

        Displays the imported data for a specific import instance.

        Args:
            request (HttpRequest): The HTTP request object.
            import_id (int): The ID of the Import object.

        Returns:
            HttpResponse: The HTTP response object rendering the import.html template.
        """
        import_instance = Import.objects.get(id=import_id)

        valids = []
        invalids = []
        file_error = ''
        creation_error = ''

        if import_instance.imported_data is not None:
            valids = import_instance.imported_data.get('valids', [])
            invalids = import_instance.imported_data.get('invalids', [])
            file_error = import_instance.imported_data.get('file_error', '')
            creation_error = import_instance.imported_data.get('creation_error', '')

        return render(request, 'import.html', {
            'instance': import_instance,
            'namespace': name,
            'valids': valids,
            'invalids': invalids,
            'file_error': file_error,
            'creation_error': creation_error
        })

    def check_import(request, import_id):
        """
        View function to check the status of an import.

        Returns the status and step of the import as a JSON response.

        Args:
            request (HttpRequest): The HTTP request object.
            import_id (int): The ID of the Import object.

        Returns:
            JsonResponse: The JSON response object containing the import status and step.
        """
        import_instance = Import.objects.get(id=import_id)

        data = {
            'status': import_instance.status,
            'step': import_instance.step
        }

        return JsonResponse(data)

    def export_fields_to_xls(request):
        """
        View function that exports the model's fields to an Excel file.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            HttpResponse: The HTTP response object containing the generated Excel file.
        """
        # Get the model's fields
        model_fields = [
            field.name
            for field in model._meta.fields
            if field.name != 'id' and not field.auto_created and not (
                    getattr(field, 'auto_now', False) or getattr(field, 'auto_now_add', False))
        ]

        # Create an empty DataFrame with the specified columns
        df = pd.DataFrame(columns=model_fields)

        # Check if fields_to_map attribute exists in the model
        if hasattr(model, 'fields_to_map') and isinstance(model.fields_to_map, dict):
            # Iterate over the fields_to_map dictionary
            for field_name, related_field in model.fields_to_map.items():
                if field_name in model_fields:
                    # Get the related field value using getattr
                    related_value = getattr(model, related_field)
                    # Assign the related field value to the DataFrame column
                    df[field_name] = related_value

        # # Assign the remaining model fields to the DataFrame
        # for field_name in model_fields:
        #     if field_name not in df.columns:
        #         df[field_name] = getattr(model, field_name)

        # Create an Excel writer using the HttpResponse object
        output = HttpResponse(content_type='application/vnd.ms-excel')
        output['Content-Disposition'] = 'attachment; filename=Import_{}.xls'.format(model.__name__)

        # Create an Excel writer using xlwt engine
        writer = pd.ExcelWriter(output)

        # Write the DataFrame to the Excel file
        df.to_excel(writer, index=False, sheet_name='Sheet1')

        # Close the writer without saving the Excel file
        writer.close()

        return output

    def export_fields_to_xls2(request):
        """
        View function that exports the model's fields to an Excel file.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            HttpResponse: The HTTP response object containing the generated Excel file.
        """
        # Get the model's fields
        model_fields = [
            field.name
            for field in model._meta.fields
            if field.name != 'id' and not field.auto_created and not (
                    getattr(field, 'auto_now', False) or getattr(field, 'auto_now_add', False))
        ]

        # Create an empty DataFrame
        df = pd.DataFrame(columns=model_fields)

        # Check if fields_to_map attribute exists in the model
        if hasattr(model, 'fields_to_map') and isinstance(model.fields_to_map, dict):
            # Iterate over the model instances
            instances = model.objects.all()
            for instance in instances:
                row = {}
                # Iterate over the fields_to_map dictionary
                for field_name, related_field in model.fields_to_map.items():
                    if field_name in model_fields:
                        field_value = getattr(instance, field_name)
                        # Get the related field value using getattr
                        related_value = getattr(field_value, related_field)

                        if callable(related_value):
                            related_value = related_value()

                        if not isinstance(related_value, str):
                            related_value = ''

                        # Assign the related field value to the row dictionary
                        row[field_name] = related_value

                # Assign the remaining model fields to the row dictionary
                for field_name in model_fields:
                    if field_name not in row and field_name != 'fields_to_map':
                        row[field_name] = getattr(instance, field_name)

                # Append the row dictionary to the DataFrame
                df = df.append(row, ignore_index=True)

        # Create an Excel writer using the HttpResponse object
        output = HttpResponse(content_type='application/vnd.ms-excel')
        output['Content-Disposition'] = 'attachment; filename=Import_{}.xls'.format(model.__name__)

        # Create an Excel writer using xlwt engine
        writer = pd.ExcelWriter(output)

        # Write the DataFrame to the Excel file
        df.to_excel(writer, index=False, sheet_name='Sheet1')

        # Close the writer without saving the Excel file
        writer.close()

        return output

    urlpatterns = [
        path("", RedirectView.as_view(url='importer/', permanent=False)),
        path("importer/", importer_view, name="importer"),
        path("import/<int:import_id>/", import_view, name="import"),
        path('import/<int:import_id>/status/', check_import, name='check_import'),
        path('importer/file', export_fields_to_xls2, name="importer_file"),
    ]

    return include((urlpatterns, name), namespace=name)
