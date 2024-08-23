# Create your views here.

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as login_user, logout as logout_user
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .validation import Validation as v
from .models import *
from datetime import datetime
from django.db.models import Avg, Q
from utils.regression import predict_final_exam_score as predict


def index(request):
    if request.user.is_authenticated:
        return redirect("home")
    return render(request, "index.html")


# home page
@login_required(login_url="login")
def home(request):
    return render(request, "home.html")


def error(request):
    return render(request, "error.html")


# User Login
def login(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if v.is_empty(email) or v.is_empty(password):
            messages.warning(request, "All fields are required.")
            return redirect("login")

        # TODO Check if user is verified before login
        current_user = MyUser.objects.filter(email=email).first()
        if current_user is not None and not current_user.is_verified:
            messages.warning(request, "User is not verified.")
            return redirect("login")

        user = authenticate(request, email=email, password=password)
        if user:
            login_user(request, user)

            if user.role == "admin":
                return redirect("admin-panel")

            return redirect("index")
        else:
            messages.error(request, "Invalid username or password")
            return redirect("login")
    return render(request, "auth/login.html")


# User Logout
def logout(request):
    logout_user(request)
    return redirect("login")


# Student Registration
def student_register(request):
    if request.user.is_authenticated:
        return redirect("index")
    semesters = Semester.objects.all()

    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        semester_id = request.POST.get("semester_id")
        profile_image = request.FILES.get("profile_image")

        try:
            MyUser.objects.create_user(
                full_name=full_name,
                email=email,
                password=password,
                semester=Semester.objects.get(id=semester_id),
                profile_image=profile_image,
            )
        except IntegrityError:
            messages.error(request, "Email already exists.")
            return redirect("student-register")

        messages.success(request, "Account created successfully.")
        return redirect("login")

    context = {
        "semesters": semesters,
    }
    return render(request, "auth/student_register.html", context)


# Teacher Registration
def teacher_register(request):
    if request.user.is_authenticated:
        return redirect("index")
    semesters = Semester.objects.all()

    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone_number")
        profile_image = request.FILES.get("profile_image")
        password = request.POST.get("password")

        existing_user = MyUser.objects.filter(email=email).first()
        if existing_user:
            messages.error(request, "Email already exists.")
            return redirect("teacher-register")

        try:
            MyUser.objects.create_user(
                full_name=full_name,
                email=email,
                password=password,
                phone_number=phone_number,
                profile_image=profile_image,
                role="teacher",
            )
        except IntegrityError:
            messages.error(request, "Phone Number is already taken.")
            return redirect("teacher-register")

        messages.success(request, "Account created successfully.")
        return redirect("login")

    context = {
        "semesters": semesters,
    }
    return render(request, "auth/teacher_register.html", context)


# attendance
@login_required(login_url="login")
def attendance(request, pk):
    if request.user.role != "teacher":
        return redirect("error")

    try:
        subject = Subject.objects.get(slug=pk)
        students = (
            MyUser.objects.filter(semester=subject.semester, role="student")
            .order_by("roll_number")
            .filter(is_verified=True)
        )

        # Get today's attendance and attendance history
        attendance_taken_for_today = Attendance.objects.filter(
            date=datetime.now().date(), subject=subject
        ).exists()
        # Distinct dates for the given subject
        distinct_dates = (
            Attendance.objects.filter(subject=subject)
            .values("date")
            .distinct()
            .order_by("-date")
        )

        if request.method == "POST":
            for student in students:
                is_present = request.POST.get(str(student.id)) == "on"
                Attendance.objects.update_or_create(
                    date=datetime.now().date(),
                    subject=subject,
                    student=student,
                    defaults={"is_present": is_present},
                )
            messages.success(request, "Attendance saved.")
            return redirect("attendance", pk=pk)

        context = {
            "subject": subject,
            "students": students,
            "attendance_taken_for_today": attendance_taken_for_today,
            "distinct_dates": distinct_dates,
        }
        return render(request, "attendance/attendance.html", context)

    except Subject.DoesNotExist:
        return redirect("error")


# single attendance
@login_required(login_url="login")
def single_attendance(request, pk, date):
    if request.user.role != "teacher":
        return redirect("error")
    try:
        subject = Subject.objects.get(slug=pk)
        attendances = Attendance.objects.filter(date=date, subject=subject).order_by(
            "student__roll_number"
        )

        if request.method == "POST":
            for atd in attendances:
                # Retrieve the student's attendance status from the form
                is_present = request.POST.get(str(atd.student.id)) == "on"
                # Update the attendance record
                atd.is_present = is_present
                atd.save()

            messages.success(request, "Attendance updated successfully.")
            return redirect("single-attendance", pk=pk, date=date)

        context = {
            "subject": subject,
            "attendances": attendances,
            "date": date,
        }
        return render(request, "attendance/single-attendance.html", context)

    except Subject.DoesNotExist:
        return redirect("error")


# task
@login_required(login_url="login")
def task(request, pk):
    try:
        subject = Subject.objects.get(slug=pk)
        tasks = Task.objects.filter(subject=subject)
        if request.method == "POST":
            if request.user.role != "teacher":
                return redirect("error")

            task_type = request.POST.get("task_type")
            description = request.POST.get("description")
            attachment = request.FILES.get("attachment")
            if not attachment.name.endswith(".pdf"):
                messages.error(request, "Only PDF files are allowed.")
                return redirect("task", pk=pk)
            can_submit_online = (
                True if request.POST.get("can_submit_online") == "true" else False
            )
            duration = request.POST.get("duration")
            Task.objects.create(
                subject=subject,
                task_type=task_type,
                description=description,
                attachment=attachment,
                can_submit_online=can_submit_online,
                duration=duration,
            )
            messages.success(request, "Task created successfully.")
            return redirect("task", pk=pk)

        context = {
            "subject": subject,
            "tasks": tasks,
        }
        return render(request, "task/task.html", context)
    except Subject.DoesNotExist:
        return redirect("error")


# single task
def single_task(request, pk, taskId):
    try:
        subject = Subject.objects.get(slug=pk)
        # check if this subject is taught by the teacher
        is_teacher = TeacherTeaches.objects.filter(
            teacher=request.user, subject=subject
        ).exists()

        if not is_teacher and request.user.role != "student":
            return redirect("error")

        task = Task.objects.get(id=taskId)

        if request.method == "POST":
            if request.user.role != "student":
                return redirect("error")
            attachment = request.FILES.get("attachment")
            if not attachment.name.endswith(".pdf"):
                messages.error(request, "Only PDF files are allowed.")
                return redirect("single-task", pk=pk, taskId=taskId)
            try:
                Submission.objects.create(
                    task=task,
                    student=request.user,
                    attachment=attachment,
                )
                messages.success(request, "Assignment submitted.")
            except IntegrityError:
                messages.error(request, "You have already submitted the assignment.")

        submission = Submission.objects.filter(task=task, student=request.user).first()
        all_submissions = Submission.objects.filter(task=task)
        remarks = Remark.objects.filter(submission=submission).first()
        context = {
            "subject": subject,
            "task": task,
            "submission": submission,
            "remarks": remarks,
            "all_submissions": all_submissions,
        }
        return render(request, "task/single-task.html", context)
    except Subject.DoesNotExist or Task.DoesNotExist:
        return redirect("error")


# update task
def update_task(request, pk, taskId):
    try:
        subject = Subject.objects.get(slug=pk)
        task = Task.objects.get(id=taskId)
        if request.method == "POST":
            if request.user.role != "teacher":
                return redirect("error")
            task_type = request.POST.get("task_type")
            description = request.POST.get("description")
            attachment = request.FILES.get("attachment")
            can_submit_online = (
                True if request.POST.get("can_submit_online") == "true" else False
            )
            duration = request.POST.get("duration")
            print(task_type, description, attachment, can_submit_online, duration)
            task.task_type = task_type
            task.description = description
            if attachment:
                task.attachment = attachment
            task.can_submit_online = can_submit_online
            if duration:
                task.duration = duration
            task.save()
            messages.success(request, "Task updated successfully.")
        context = {
            "subject": subject,
            "task": task,
        }
        return redirect("task", pk=pk)
    except Subject.DoesNotExist or Task.DoesNotExist:
        return redirect("error")


# delete task
def delete_task(request, pk, taskId):
    try:
        if request.user.role != "teacher":
            return redirect("error")
        task = Task.objects.get(id=taskId)
        if Submission.objects.filter(task=task).exists():
            messages.error(
                request,
                "Task can't be deleted as students have already submitted the assignment.",
            )
            return redirect("task", pk=pk)
        task.delete()
        messages.success(request, "Task deleted successfully.")
        return redirect("task", pk=pk)
    except Subject.DoesNotExist or Task.DoesNotExist:
        return redirect("error")


# submission
@login_required(login_url="login")
def single_submission(request, pk):
    try:
        user = request.user
        submission = Submission.objects.get(id=pk)

        is_teacher = TeacherTeaches.objects.filter(
            teacher=user, subject=submission.task.subject
        ).exists()

        if not is_teacher or user.role != "teacher":
            return redirect("error")

        existing_remark = Remark.objects.filter(submission=submission).first()

        if request.method == "POST":
            score = request.POST.get("score")
            status = request.POST.get("status")
            feedback = request.POST.get("feedback")

            if score and status and feedback:
                if existing_remark:
                    existing_remark.score = score
                    existing_remark.feedback = feedback
                    existing_remark.save()
                    submission.status = status
                    submission.save()
                    messages.success(request, "Feedback updated.")
                    return redirect(
                        "single-task",
                        pk=submission.task.subject.slug,
                        taskId=submission.task.id,
                    )
                else:
                    Remark.objects.create(
                        submission=submission,
                        score=score,
                        feedback=feedback,
                    )
                    submission.status = status
                    submission.save()
                    messages.success(request, "Feedback submitted & Score saved.")
                    return redirect(
                        "single-task",
                        pk=submission.task.subject.slug,
                        taskId=submission.task.id,
                    )
            else:
                messages.error(request, "Fill all the fields.")

        context = {"submission": submission, "existing_remark": existing_remark}
        return render(request, "submission/submission.html", context)
    except Submission.DoesNotExist:
        return redirect("error")


# delete submission
@login_required(login_url="login")
def delete_submission(request, pk):
    try:
        submission = Submission.objects.get(id=pk)
        if request.user.role != "student":
            return redirect("error")
        if submission.student != request.user:
            return redirect("error")
        submission.delete()
        messages.success(request, "Submission deleted successfully.")
        return redirect(
            "single-task",
            pk=submission.task.subject.slug,
            taskId=submission.task.id,
        )
    except Submission.DoesNotExist:
        return redirect("error")


# record marks
@login_required(login_url="login")
def record_marks(request, pk):
    try:
        subject = Subject.objects.get(slug=pk)
        students = (
            MyUser.objects.filter(semester=subject.semester, role="student")
            .order_by("roll_number")
            .filter(is_verified=True)
        )
        total_exams = (
            ExamResults.objects.values("mid_term", "pre_board")
            .distinct()
            .filter(subject=subject)
        )
        both_recorded = (
            ExamResults.objects.filter(
                student=students.first(), subject=subject
            ).count()
            == 2
        )

        if request.method == "POST":
            exam_type = request.POST.get("exam_type")
            full_marks = request.POST.get("full_marks")

            if exam_type and full_marks:
                mid_term = exam_type == "mid-term"
                pre_board = exam_type == "pre-board"

                for student in students:
                    obtained_marks = request.POST.get(f"marks_{student.id}")
                    if obtained_marks is not None:
                        try:
                            ExamResults.objects.create(
                                student=student,
                                subject=subject,
                                mid_term=mid_term,
                                pre_board=pre_board,
                                obtained_marks=int(obtained_marks),
                                full_marks=int(full_marks),
                            )
                        except IntegrityError:
                            messages.error(
                                request,
                                f"Marks already recorded for {exam_type.capitalize() if exam_type == 'mid-term' else 'Pre-Board'}.",
                            )
                            return redirect("record-marks", pk=pk)
                messages.success(
                    request,
                    f"{exam_type.capitalize() if exam_type == 'mid-term' else 'Pre-Board'} marks saved.",
                )
                return redirect("record-marks", pk=pk)
            else:
                messages.error(request, "Please select an exam and enter full marks.")

        context = {
            "subject": subject,
            "students": students,
            "total_exams": total_exams,
            "both_recorded": both_recorded,
        }
        return render(request, "marks/record-marks.html", context)
    except Subject.DoesNotExist:
        return redirect("error")


# single marks
@login_required(login_url="login")
def single_marks(request, pk, exam_type):
    try:
        subject = Subject.objects.get(slug=pk)
        results = ExamResults.objects.filter(
            subject=subject,
            mid_term=exam_type == "mid-term",
            pre_board=exam_type == "pre-board",
        ).order_by("student__roll_number")

        if request.method == "POST":
            full_marks = int(request.POST.get("full_marks"))
            form_exam_type = request.POST.get("exam_type")

            # Flag to check if any IntegrityError occurs
            integrity_error_occurred = False

            for res in results:
                marks = request.POST.get(f"marks_{res.student.id}")
                if marks:
                    res.obtained_marks = int(marks)
                    res.full_marks = full_marks
                    res.mid_term = form_exam_type == "mid-term"
                    res.pre_board = form_exam_type == "pre-board"

                    try:
                        res.save()
                    except IntegrityError:
                        # Set the flag to True if any IntegrityError occurs
                        integrity_error_occurred = True

            if integrity_error_occurred:
                messages.error(
                    request, f"Marks already recorded for {form_exam_type.capitalize()}"
                )
                return redirect("single-marks", pk=pk, exam_type=exam_type)
            else:
                messages.success(
                    request, f"{exam_type.capitalize()} marks updated successfully."
                )

            return redirect("single-marks", pk=pk, exam_type=exam_type)

        exam_type_display = "Mid Term" if exam_type == "mid-term" else "Pre Board"
        context = {
            "subject": subject,
            "results": results,
            "exam_type": exam_type_display,
            "full_marks": results.first().full_marks if results.exists() else 100,
        }
        return render(request, "marks/single-marks.html", context)

    except Subject.DoesNotExist:
        messages.error(request, "Subject does not exist.")
        return redirect("error")


# message
@login_required(login_url="login")
def message(request):
    return render(request, "message/message.html")


@login_required(login_url="login")
def prediction(request, pk):

    if request.user.role != "teacher":
        return redirect("error")

    try:
        subject = Subject.objects.get(slug=pk)
        students = (
            MyUser.objects.filter(semester=subject.semester, role="student")
            .order_by("roll_number")
            .filter(is_verified=True)
        )
        remarks = Remark.objects.filter(submission__task__subject=subject)
        attendances = Attendance.objects.filter(subject=subject)
        mid_term_results = ExamResults.objects.filter(subject=subject, mid_term=True)
        pre_board_results = ExamResults.objects.filter(subject=subject, pre_board=True)

        student_data = []

        is_data_available = False

        for student in students:
            # Average task completion score
            student_remarks = remarks.filter(submission__student=student)
            avg_score = (
                student_remarks.aggregate(Avg("score_percentage"))[
                    "score_percentage__avg"
                ]
                or 0
            )
            # Average attendance percentage
            total_attendance = attendances.filter(student=student).count()
            present_attendance = attendances.filter(
                student=student, is_present=True
            ).count()
            avg_attendance = (
                (present_attendance / total_attendance * 100)
                if total_attendance > 0
                else 0
            )

            # Mid-term score
            mid_term = mid_term_results.filter(student=student).first()
            mid_term_score = mid_term.percentage if mid_term else 0

            # Pre-board score
            pre_board = pre_board_results.filter(student=student).first()
            pre_board_score = pre_board.percentage if pre_board else 0

            if (
                avg_attendance is not None
                and avg_score is not None
                and mid_term_score is not None
                and pre_board_score is not None
            ):
                is_data_available = True
            else:
                is_data_available = False

            student_info = {
                "student_id": student.id,
                "student_roll": student.roll_number,
                "student_name": student.full_name,
                "avg_task_score": round(avg_score),
                "avg_attendance": round(avg_attendance),
                "mid_term_score": mid_term_score,
                "pre_board_score": pre_board_score,
                "predicted_score": (
                    round(
                        predict(
                            avg_attendance, avg_score, mid_term_score, pre_board_score
                        ),
                        2,
                    )
                ),
            }
            # print(student_info)

            student_data.append(student_info)

        context = {
            "subject": subject,
            "student_data": student_data,
            "is_data_available": is_data_available,
        }
        return render(request, "prediction/prediction.html", context)
    except Subject.DoesNotExist:
        return redirect("error")


# ! ==========================================================================================================================
# ! ================================================== ADMIN PANEL ===========================================================
# ! ==========================================================================================================================

# verify students and teachers
# assign semester to students and subjects to teachers
# add subject, semester, and add subject to semester
# admin can update students semester and teachers subjects


@login_required(login_url="login")
def admin_panel(request):
    if request.user.is_anonymous or request.user.role != "admin":
        return redirect("error")
    return render(request, "admin-panel/dashboard.html")


@login_required(login_url="login")
def semesters(request):
    if request.user.role != "admin" or request.user.is_anonymous:
        return redirect("error")
    semesters = Semester.objects.all()

    if request.method == "POST" and request.POST.get("add-semester") is not None:
        semester_name = request.POST.get("semester_name")
        if v.is_empty(semester_name):
            messages.error(request, "Semester name is required.")
            return redirect("semesters")
        if not v.is_valid_name(semester_name):
            messages.error(request, "Semester name is invalid.")
            return redirect("semesters")
        try:
            Semester.objects.create(name=semester_name)
            messages.success(request, "Semester added successfully.")
            return redirect("semesters")
        except IntegrityError:
            messages.error(request, "Semester already exists.")
            return redirect("semesters")

    context = {
        "semesters": semesters,
    }
    return render(request, "admin-panel/semesters.html", context)


@login_required(login_url="login")
def delete_semester(request, pk):
    if request.user.role != "admin" or request.user.is_anonymous:
        return redirect("error")
    semester = Semester.objects.get(id=pk)
    semester.delete()
    messages.success(request, "Semester deleted successfully.")
    return redirect("semesters")


@login_required(login_url="login")
def semester_subjects(request, name):
    if request.user.role != "admin" or request.user.is_anonymous:
        return redirect("error")
    semester = Semester.objects.get(name=name)
    subjects = Subject.objects.filter(semester=semester)

    if request.method == "POST" and request.POST.get("add-subject") is not None:
        subject_name = request.POST.get("subject_name")
        if v.is_empty(subject_name):
            messages.error(request, "Subject name is required.")
            return redirect("semester-subjects", name=name)
        if not v.is_valid_name(subject_name):
            messages.error(request, "Subject name is invalid.")
            return redirect("semester-subjects", name=name)
        try:
            Subject.objects.create(name=subject_name, semester=semester)
            messages.success(request, "Subject added successfully.")
            return redirect("semester-subjects", name=name)
        except IntegrityError:
            messages.error(request, "Subject already exists.")
            return redirect("semester-subjects", name=name)

    context = {
        "semester": semester,
        "subjects": subjects,
    }
    return render(request, "admin-panel/semester-subjects.html", context)


def delete_subject(request, pk):
    if request.user.role != "admin" or request.user.is_anonymous:
        return redirect("error")
    subject = Subject.objects.get(id=pk)
    subject.delete()
    messages.success(request, "Subject deleted successfully.")
    return redirect("semester-subjects", name=subject.semester.name)


@login_required(login_url="login")
def students(request):
    if request.user.role != "admin" or request.user.is_anonymous:
        return redirect("error")
    students = MyUser.objects.filter(role="student").order_by("is_verified")
    context = {
        "students": students,
    }
    return render(request, "admin-panel/students.html", context)


@login_required(login_url="login")
def teachers(request):
    if request.user.role != "admin":
        return redirect("error")

    teachers = MyUser.objects.filter(role="teacher").order_by("is_verified")
    context = {
        "teachers": teachers,
    }
    return render(request, "admin-panel/teachers.html", context)


@login_required(login_url="login")
def assign_teachers(request):
    if request.user.role != "admin" or request.user.is_anonymous:
        return redirect("error")
    teachers = MyUser.objects.filter(role="teacher")
    subjects = Subject.objects.all()

    if request.method == "POST":
        teacher_id = request.POST.get("teacher_id")
        subject_id = request.POST.get("subject_id")

        teacher = MyUser.objects.get(id=teacher_id)
        subject = Subject.objects.get(id=subject_id)

        TeacherTeaches.objects.create(teacher=teacher, subject=subject)
        messages.success(request, "Subject assigned to teacher successfully.")
        return redirect("assign-teachers")

    context = {
        "teachers": teachers,
        "subjects": subjects,
    }
    return render(request, "admin-panel/assign-teachers.html", context)


# Verify students and teachers
@login_required(login_url="login")
def verify_user(request, pk):
    if request.user.role != "admin":
        return redirect("error")
    user = MyUser.objects.get(id=pk)
    user.is_verified = True
    user.save()
    messages.success(request, "User verified successfully.")
    if user.role == "student":
        return redirect("students")
    return redirect("teachers")
