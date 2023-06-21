"""
URL configuration for school_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from apps.importer.views import generate_importer
from apps.school import models
from apps.school import views
from school_app.views import HomeView
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('api/', include('apps.school.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include("django.contrib.auth.urls")),
    path('students/', generate_importer(models.Student, name="students")),
    path('teachers/', generate_importer(models.Teacher, name="teachers")),
    # path('courses/', generate_importer(models.Course, name="courses")),
    path('courses/', views.scrapper_view, name="courses"),
    path('run_scrapper/', views.run_scrapper_view, name="run_scrapper"),
    path('grades/', generate_importer(models.Grade, name="grades")),
]


handler404 = "school_app.views.page_not_found_view"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
