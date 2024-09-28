from django.urls import path
from . import views as v

urlpatterns = [
    path("", v.index, name="index"),
    path("home/", v.home, name="home"),
    path("error/", v.error, name="error"),
    # ========================================================================================
    # ! Authentication routes
    path("login/", v.login, name="login"),
    path("student-register/", v.student_register, name="student-register"),
    path("teacher-register/", v.teacher_register, name="teacher-register"),
    # 🔽 This is route for logout but it does not have separate page
    path("logout/", v.logout, name="logout"),
    # ========================================================================================
    # ! Attendance routes
    path("attendance/<str:pk>/", v.attendance, name="attendance"),
    path(
        "attendance/<str:pk>/<str:date>/", v.single_attendance, name="single-attendance"
    ),
    # ========================================================================================
    # ! Task routes
    path("task/<str:pk>/", v.task, name="task"),
    path("task/<str:pk>/<int:taskId>/", v.single_task, name="single-task"),
    # 🔽 This is route for delete but it does not have separate page
    path("delete-task/<str:pk>/<int:taskId>/", v.delete_task, name="delete-task"),
    # 🔽 This is route for update but it does not have separate page
    path("update-task/<str:pk>/<int:taskId>/", v.update_task, name="update-task"),
    # ========================================================================================
    # ! Submission routes
    path("submission/<int:pk>", v.single_submission, name="submission"),
    path("submission/delete/<int:pk>", v.delete_submission, name="delete-submission"),
    # ========================================================================================
    # ! Message routes
    path("message/", v.message, name="message"),
    # ========================================================================================
    # ! Record marks routes
    path("record-marks/<str:pk>/", v.record_marks, name="record-marks"),
    path("record-marks/<str:pk>/<str:exam_type>", v.single_marks, name="single-marks"),
    # ========================================================================================
    # prediction
    path("prediction/<str:pk>", v.prediction, name="prediction"),
    # ========================================================================================
    # !=======================================================================================
    # !=======================================================================================
    # !=======================================================================================
    # ! Admin routes
    path("admin-panel/", v.admin_panel, name="admin-panel"),
    path("admin-panel/students/", v.students, name="students"),
    path("admin-panel/teachers/", v.teachers, name="teachers"),
    path("admin-panel/semesters/", v.semesters, name="semesters"),
    path("admin-panel/assign-teachers/", v.assign_teachers, name="assign-teachers"),
    # verify
    path("verify/<int:pk>", v.verify_user, name="verify-user"),
    
       # dis approve user
    path("reject/<int:pk>", v.reject_user, name="reject-user"),

    # semester subjects
    path("admin-panel/semester-subjects/<str:name>", v.semester_subjects, name="semester-subjects"),

    # delete semester
    path("admin-panel/delete-semester/<int:pk>", v.delete_semester, name="delete-semester"),

    # delete subject
    path("admin-panel/delete-subject/<int:pk>", v.delete_subject, name="delete-subject"),

    # delete teacher teaches
    path(
        "admin-panel/delete-teacher-teaches/<int:pk>",
        v.delete_teacher_teaches,
        name="delete-teacher-teaches",
    ),
    # delete user
    path("delete/<int:pk>", v.delete_user, name="delete-user"),
    # Edit Teacher by admin
    path("admin-panel/edit-teacher/<int:pk>", v.edit_teacher, name="edit-teacher"),
    # Edit student by admin
    path("admin-panel/edit-student/<int:pk>", v.edit_student, name="edit-student"),
    
    # ========================================================================================

]
