from classroom.models import Subject


def get_subjects(request):
    if not request.user.is_authenticated:
        return {}
    if request.user.role == "teacher":
        subjects = Subject.objects.filter(teacher_subjects__teacher=request.user)
    else:
        subjects = Subject.objects.filter(semester=request.user.semester)
    return {"view_subjects": subjects}
