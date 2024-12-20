# Generated by Django 5.0.1 on 2024-08-10 17:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("classroom", "0007_submission"),
    ]

    operations = [
        migrations.CreateModel(
            name="Remark",
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
                ("score", models.PositiveIntegerField()),
                (
                    "score_percentage",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                ("feedback", models.CharField(max_length=255)),
                (
                    "submission",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="remarks",
                        to="classroom.submission",
                    ),
                ),
            ],
            options={
                "db_table": "remark",
                "ordering": ["-id"],
                "unique_together": {("submission", "score", "feedback")},
            },
        ),
    ]
