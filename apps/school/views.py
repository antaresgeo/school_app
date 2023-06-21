from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet

from .models import Student, Teacher, Course, Grade
from .serializers import StudentSerializer, TeacherSerializer, CourseSerializer, GradeSerializer
from .tasks import run_scrapper


class StudentViewSet(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class TeacherViewSet(ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class GradeViewSet(ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer


def scrapper_view(request):
    courses = Course.objects.all()

    context = {
        'courses': courses
    }
    return render(request, 'scrapper.html', context)

def run_scrapper_view(request):
    run_scrapper.delay(request.user.id)

    return HttpResponse("Asynchronous task started. An email will be sent when the task is complete.")