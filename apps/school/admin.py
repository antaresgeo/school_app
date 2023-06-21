from django.contrib import admin
from django.contrib.admin import widgets
from .models import Student, Teacher, Course, Grade


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'age']
    list_filter = ['age']
    search_fields = ['first_name', 'last_name', 'email']


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'age', 'specialization']
    list_filter = ['age', 'specialization']
    search_fields = ['first_name', 'last_name', 'email', 'specialization']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'teacher', 'description']
    list_filter = ['teacher']
    search_fields = ['name', 'teacher__first_name', 'teacher__last_name', 'students__first_name', 'students__last_name']

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        kwargs['widget'] = widgets.FilteredSelectMultiple(
            db_field.verbose_name,
            db_field.name in self.filter_vertical
        )

        return super(admin.ModelAdmin, self).formfield_for_manytomany(
            db_field, request=request, **kwargs)


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'grade']
    list_filter = ['student', 'course']
    search_fields = ['student__first_name', 'student__last_name', 'course__name']

