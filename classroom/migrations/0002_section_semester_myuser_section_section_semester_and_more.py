# Generated by Django 5.0.1 on 2024-08-10 17:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("classroom", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Section",
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
                ("name", models.CharField(max_length=20, unique=True)),
            ],
            options={
                "db_table": "section",
            },
        ),
        migrations.CreateModel(
            name="Semester",
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
                ("name", models.CharField(max_length=20, unique=True)),
            ],
            options={
                "db_table": "semester",
                "ordering": ["id"],
            },
        ),
        migrations.AddField(
            model_name="myuser",
            name="section",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="students",
                to="classroom.section",
            ),
        ),
        migrations.AddField(
            model_name="section",
            name="semester",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="sections",
                to="classroom.semester",
            ),
        ),
        migrations.AddField(
            model_name="myuser",
            name="semester",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="students",
                to="classroom.semester",
            ),
        ),
    ]
