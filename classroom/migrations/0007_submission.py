# Generated by Django 5.0.1 on 2024-08-10 17:31

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("classroom", "0006_examresults"),
    ]

    operations = [
        migrations.CreateModel(
            name="Submission",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("unchecked", "Unchecked"),
                            ("checked", "Checked"),
                            ("rejected", "Rejected"),
                        ],
                        default="unchecked",
                        max_length=10,
                    ),
                ),
                (
                    "attachment",
                    models.FileField(blank=True, null=True, upload_to="submissions"),
                ),
                ("submitted_at", models.DateTimeField(auto_now_add=True)),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="submissions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "task",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="submissions",
                        to="classroom.task",
                    ),
                ),
            ],
            options={
                "db_table": "submission",
                "ordering": ["-submitted_at"],
                "unique_together": {("task", "student")},
            },
        ),
    ]
