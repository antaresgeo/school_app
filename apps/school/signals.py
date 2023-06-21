from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Course, Grade

@receiver(m2m_changed, sender=Course.students.through)
def create_grade_for_student(sender, instance, action, reverse, pk_set, **kwargs):
    if action == 'post_add':
        for student_id in pk_set:
            Grade.objects.create(student_id=student_id, course=instance)
