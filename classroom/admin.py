# Register your models here.
from django.contrib import admin
from .models import *

admin.site.register(MyUser)
# admin.site.register(Section)
admin.site.register(Semester)
admin.site.register(Subject)
admin.site.register(TeacherTeaches)
admin.site.register(Task)
admin.site.register(Attendance)
admin.site.register(ExamResults)
admin.site.register(Submission)
admin.site.register(Remark)
