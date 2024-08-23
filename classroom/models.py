from django.db import models

# Create your models here.
from django.db import models
from datetime import datetime
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
from django.db import IntegrityError
from django.utils.text import slugify


class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError("Users must have an email address")
        user = self.model(
            email=self.normalize_email(email),
            **kwargs,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **kwargs):
        user = self.create_user(
            email,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


# user table
class MyUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ("student", "Student"),
        ("teacher", "Teacher"),
        ("admin", "Admin"),
    ]

    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )

    full_name = models.CharField(max_length=200, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True, unique=True)
    role = models.CharField(choices=ROLE_CHOICES, max_length=10, default="student")
    roll_number = models.CharField(max_length=20, blank=True, null=True)

    profile_image = models.ImageField(
        upload_to="profile", blank=True, null=True, default="profile/default-user.jpg"
    )

    semester = models.ForeignKey(
        "Semester",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="students",
    )
    section = models.ForeignKey(
        "Section",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="students",
    )
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    objects = MyUserManager()

    USERNAME_FIELD = "email"

    def __str__(self):
        return f"{self.full_name} :: {self.role.capitalize()} "

    class Meta:
        db_table = "user"
        verbose_name_plural = "Users"


# Semester table
class Semester(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "semester"
        ordering = ["id"]


# Section table
class Section(models.Model):
    name = models.CharField(max_length=20, unique=True)
    semester = models.ForeignKey(
        Semester, on_delete=models.CASCADE, related_name="sections"
    )

    def __str__(self):
        return f"{self.semester.name} :: {self.name}"

    class Meta:
        db_table = "section"


# subject table
class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    semester = models.ForeignKey(
        Semester, on_delete=models.CASCADE, related_name="subjects"
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    class Meta:
        db_table = "subject"


# teacher teaches table
class TeacherTeaches(models.Model):
    teacher = models.ForeignKey(
        MyUser, on_delete=models.CASCADE, related_name="teacher_subjects"
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="teacher_subjects"
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name="teacher_subjects",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.teacher.full_name} :: {self.subject.name} :: {self.subject.semester.name} "

    def save(self, *args, **kwargs):
        if TeacherTeaches.objects.filter(
            subject=self.subject, section=self.section
        ).exists():
            return IntegrityError(
                "Another teacher already teaches the subject in the section."
            )
        return super().save(*args, **kwargs)

    class Meta:
        db_table = "teacher_teaches"
        unique_together = ("teacher", "subject", "section")
        verbose_name_plural = "Teacher Teaches"


# task table
class Task(models.Model):

    TASK_TYPE = [
        ("assignment", "Assignment"),
        ("lab report", "Lab Report"),
        ("presentation", "Presentation"),
        ("case study", "Case Study"),
    ]
    task_type = models.CharField(choices=TASK_TYPE, max_length=20)
    description = models.TextField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="tasks")
    attachment = models.FileField(upload_to="tasks", null=True, blank=True)
    duration = models.DateField(null=True, blank=True)
    can_submit_online = models.BooleanField(default=False)
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name="tasks",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.subject.name} Task at {self.created_at}"

    class Meta:
        ordering = ["-updated_at"]
        db_table = "tasks"


# attendance table
class Attendance(models.Model):
    date = models.DateField(default=datetime.now)
    is_present = models.BooleanField(default=False)
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="attendances"
    )
    student = models.ForeignKey(
        MyUser, on_delete=models.CASCADE, related_name="attendances"
    )

    def __str__(self):
        return f"{self.subject.semester.name} :: {self.student.full_name} :: {self.date} :: {self.is_present}"

    class Meta:
        db_table = "attendance"
        ordering = ["-date"]
        unique_together = ("date", "subject", "student")


# Exam result store table
class ExamResults(models.Model):
    student = models.ForeignKey(
        MyUser, on_delete=models.CASCADE, related_name="results"
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="results"
    )
    obtained_marks = models.PositiveIntegerField()
    full_marks = models.PositiveIntegerField()
    percentage = models.PositiveIntegerField(null=True, blank=True)
    mid_term = models.BooleanField(default=False)
    pre_board = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.percentage = round((self.obtained_marks / self.full_marks) * 100)
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.subject.semester.name} :: {self.student.full_name} :: "
            f"{self.subject.name} :: {self.obtained_marks}/{self.full_marks} "
            f"({self.percentage}%)"
        )

    class Meta:
        db_table = "exam_results"
        unique_together = ("student", "subject", "mid_term", "pre_board")


# Submission table
class Submission(models.Model):
    STATUS_CHOICES = [
        ("unchecked", "Unchecked"),
        ("checked", "Checked"),
        ("rejected", "Rejected"),
    ]
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(
        MyUser, on_delete=models.CASCADE, related_name="submissions"
    )
    status = models.CharField(
        choices=STATUS_CHOICES, max_length=10, default="unchecked"
    )
    attachment = models.FileField(upload_to="submissions", null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.task.subject.name} Submission at {self.submitted_at} by {self.student.full_name}"

    class Meta:
        db_table = "submission"
        ordering = ["-submitted_at"]
        unique_together = ("task", "student")


# remark table
class Remark(models.Model):
    submission = models.ForeignKey(
        Submission, on_delete=models.CASCADE, related_name="remarks"
    )
    score = models.PositiveIntegerField()
    score_percentage = models.PositiveIntegerField(null=True, blank=True)
    feedback = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.submission.task.subject.name} :: {self.submission.student.full_name}"

    def save(self, *args, **kwargs):
        score = int(self.score)
        self.score_percentage = round((score / 10) * 100)
        return super().save(*args, **kwargs)

    class Meta:
        db_table = "remark"
        ordering = ["-id"]
        unique_together = ("submission", "score", "feedback")
