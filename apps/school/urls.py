from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import StudentViewSet, TeacherViewSet, CourseViewSet, GradeViewSet


router = DefaultRouter()

router.register(r'students', StudentViewSet)
router.register(r'teachers', TeacherViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'grades', GradeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]