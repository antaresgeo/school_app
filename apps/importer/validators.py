from django.core.exceptions import ValidationError
from decimal import Decimal

from django.db.models import Q


class ModelValidator:
    """
    A generic validator class for performing field validations on model objects.
    """

    def __init__(self, model, exclude_fields=None):
        if exclude_fields is None:
            exclude_fields = []
        self.model = model
        self.exclude_fields = exclude_fields

    def validate(self, data):
        """
        Validates the fields of a model object.

        Args:
            data (dict): Dictionary containing the field_name data.

        Returns:
            dict: Dictionary of validation errors, with field_name names as keys and error messages as values.
        """
        errors = {}

        self.validate_unique_fields(data, errors)

        for field_name in data:
            if not hasattr(self.model, field_name):
                errors[field_name] = self.ERROR_FIELD_NOT_EXIST.format(field=field_name,model_name=self.model._meta.label)
                continue

            data_value = data[field_name]
            field = self.model._meta.get_field(field_name)
            field_type = field.get_internal_type()

            # Validating field types
            if field_type in ('CharField', 'TextField'):
                self.validate_char_field(field_name, data_value, errors)
            elif field_type == 'IntegerField':
                self.validate_integer_field(field_name, data_value, errors)
            elif field_type == 'BooleanField':
                self.validate_boolean_field(field_name, data_value, errors)
            # elif field_type == 'DateField':
            #     self.validate_date_field(field_name, data_value, errors)
            # elif field_type in ('ForeignKey', 'OneToOneField'):
            #     self.validate_related_field(field_name, data_value, errors)

            # Add more field_name type checks as needed

            self.validate_choices(field_name, data_value, errors)


            if field.is_relation:
                related_model = field.related_model
                # Create a list of Q conditions for each field in the related model
                query = Q()
                for field in related_model._meta.fields:
                    if field.get_internal_type() in ['CharField', 'TextField']:
                        query |= Q(**{f'{field.name}__icontains': data_value})

                # Perform the filter query on the related model
                filtered_objects = related_model.objects.filter(query)

                # Check if no objects were found
                if not filtered_objects.exists():
                    # Construct the contextualized error message
                    errors[field_name] = self.ERROR_FIELD_RELATION.format(field=field_name)
                else:
                    data[field_name] = filtered_objects[0].id

            if not field_name in errors:
                for validator in field.validators:
                    try:
                        validator(data_value)
                    except ValidationError as e:
                        errors[field_name] = str(e)
                        break

        # Check for required fields
        for field in self.model._meta.fields:
            # Excluding fields that are autofilled
            has_auto_now = field.auto_now if hasattr(field, 'auto_now') else False
            has_auto_now_add = field.auto_now_add if hasattr(field, 'auto_now_add') else False
            if field.auto_created or has_auto_now_add or has_auto_now:
                continue

            is_valid = field.name in data and data[field.name]

            if not is_valid:
                errors[field.name] = self.ERROR_FIELD_REQUIRED.format(field=field.name)

        if errors:
            return errors
        else:
            return None

    def validate_array(self, objects_to_create):
        """
        Validates an array of model objects.

        Args:
            objects_to_create (list): List of model objects to validate.

        Returns:
            tuple: A tuple containing two lists - valid_objects and invalid_objects.
                - valid_objects: List of valid model objects.
                - invalid_objects: List of invalid model objects along with their errors.
        """
        valid_objects = []
        invalid_objects = []
        unique_fields = self.get_unique_field_names()

        seen_values = {}
        for index, obj_data in enumerate(objects_to_create):
            errors = self.validate(obj_data)
            if errors:
                invalid_object = {
                    'data': obj_data,
                    'errors': errors
                }
                invalid_objects.append({"order": index + 2, **invalid_object})
            else:
                unique_key = tuple((field, obj_data.get(field)) for field in unique_fields)
                if unique_key in seen_values:
                    errors = {
                        field_name: self.ERROR_FIELD_DUPLICATE_VALUES.format(field=field_name, value=field_value)
                        for field_name, field_value in unique_key
                    }
                    invalid_object = {
                        'data': obj_data,
                        'errors': errors
                    }
                    invalid_objects.append({"order": index + 2, **invalid_object})
                else:
                    seen_values[unique_key] = None
                    valid_objects.append({"order": index + 2, "data": obj_data})

        return {'valids': valid_objects, "invalids": invalid_objects}

    def validate_choices(self, field_name, value, errors):
        """
        Validates the choices for a field.

        Args:
            field_name (str): Name of the field being validated.
            value: Value of the field being validated.
            errors (dict): Dictionary of validation errors.

        Returns:
            None
        """
        if hasattr(self.model._meta.get_field(field_name), 'choices'):
            choices = self.model._meta.get_field(field_name).choices
            if choices:
                valid_choices = [choice[0] for choice in choices]
                if value not in valid_choices:
                    errors[field_name] = self.ERROR_FIELD_CHOICES.format(field=field_name, valid_choices=valid_choices)

    def validate_char_field(self, field_name, value, errors):
        """
        Validates a CharField or TextField.

        Args:
            field_name (str): Name of the field being validated.
            value: Value of the field being validated.
            errors (dict): Dictionary of validation errors.

        Returns:
            None
        """
        if not isinstance(value, str):
            errors[field_name] = self.ERROR_FIELD_WRONG_TYPE.format(field=field_name, expected_type='str')

    def validate_integer_field(self, field_name, value, errors):
        """
        Validates an IntegerField.

        Args:
            field_name (str): Name of the field being validated.
            value: Value of the field being validated.
            errors (dict): Dictionary of validation errors.

        Returns:
            None
        """
        if not isinstance(value, int):
            errors[field_name] = self.ERROR_FIELD_WRONG_TYPE.format(field=field_name, expected_type='int')

    def validate_boolean_field(self, field, value, errors):
        """
        Validates a BooleanField.

        Args:
            field (str): Name of the field being validated.
            value: Value of the field being validated.
            errors (dict): Dictionary of validation errors.

        Returns:
            None
        """
        if not isinstance(value, bool):
            errors[field] = self.ERROR_FIELD_WRONG_TYPE.format(field=field, expected_type='bool')

    def validate_date_field(self, field, value, errors):
        """
        Validates a DateField.

        Args:
            field (str): Name of the field being validated.
            value: Value of the field being validated.
            errors (dict): Dictionary of validation errors.

        Returns:
            None
        """
        if not isinstance(value, str):
            errors[field] = self.ERROR_FIELD_WRONG_TYPE.format(field=field, expected_type='str')
        else:
            try:
                self.model._meta.get_field(field).to_python(value)
            except (ValueError, TypeError):
                errors[field] = self.ERROR_FIELD_INVALID_DATE.format(field=field)

    def validate_related_field(self, field, value, errors):
        """
        Validates a ForeignKey or OneToOneField.

        Args:
            field (str): Name of the field being validated.
            value: Value of the field being validated.
            errors (dict): Dictionary of validation errors.

        Returns:
            None
        """
        related_model = self.model._meta.get_field(field).related_model
        if not isinstance(value, related_model):
            errors[field] = self.ERROR_FIELD_WRONG_TYPE.format(field=field, expected_type=related_model.__name__)

    def get_unique_field_names(self):
        uniques = []

        for field in self.model._meta.fields:
            has_auto_now = field.auto_now if hasattr(field, 'auto_now') else False
            has_auto_now_add = field.auto_now_add if hasattr(field, 'auto_now_add') else False
            if field.unique and not field.auto_created and not has_auto_now and not has_auto_now_add:
                uniques.append(field.name)
        return uniques

    def validate_unique_fields(self, data, errors):
        """
        Validates unique fields in the model and data.

        Args:
            data (dict): Dictionary containing the field_name data.
            errors (dict): Dictionary of validation errors.

        Returns:
            None
        """
        uniques = self.get_unique_field_names()

        for field_name in uniques:
            if field_name in data:
                field_value = data[field_name]
                if self.model.objects.filter(**{field_name: field_value}).exists():
                    errors[field_name] = self.ERROR_FIELD_UNIQUE.format(field=field_name)

    # Constant error messages
    ERROR_FIELD_NOT_EXIST = "The field '{field}' does not exist in the model '{model_name}'."
    ERROR_FIELD_WRONG_TYPE = "The field '{field}' must be of type '{expected_type}'."
    ERROR_FIELD_MAX_LENGTH = "The field '{field}' exceeds the maximum length of {max_length} characters."
    ERROR_FIELD_CHOICES = "The field '{field}' must be one of the valid choices: {valid_choices}."
    ERROR_FIELD_REQUIRED = "The field '{field}' is required."
    ERROR_FIELD_INVALID_DATE = "The field '{field}' must be a valid date."
    ERROR_FIELD_RELATION = "No matches found in the relation {field}."
    ERROR_FIELD_DUPLICATE_VALUES = "The unique field  '{field}' has a duplicate value: '{value}'."
    ERROR_FIELD_UNIQUE = "The field '{field}' must be unique."
