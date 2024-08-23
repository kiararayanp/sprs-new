from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MyUser


@receiver(post_save, sender=MyUser)
def update_roll_numbers(sender, instance, **kwargs):
    if instance.role == "student" and not hasattr(instance, "_skip_signal"):
        students_in_semester = MyUser.objects.filter(
            role="student", semester=instance.semester
        ).order_by("full_name")
        for index, student in enumerate(students_in_semester, start=1):
            if student.roll_number != f"{index}":
                student.roll_number = f"{index}"
                student._skip_signal = True
                student.save(update_fields=["roll_number"])
                del student._skip_signal
