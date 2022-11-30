# Generated by Django 4.1.3 on 2022-11-30 15:53

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import core.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Application",
            fields=[
                (
                    "is_deleted",
                    models.BooleanField(db_index=True, default=False, verbose_name="Soft Delete"),
                ),
                ("app_name", models.CharField(max_length=32, verbose_name="App Name")),
                (
                    "app_code",
                    models.CharField(
                        max_length=32,
                        primary_key=True,
                        serialize=False,
                        verbose_name="App Code",
                    ),
                ),
                (
                    "app_secret",
                    models.TextField(blank=True, null=True, verbose_name="App Secret (Encoded)"),
                ),
            ],
            options={
                "verbose_name": "Application",
                "verbose_name_plural": "Application",
                "ordering": ["app_code"],
            },
        ),
        migrations.CreateModel(
            name="ApplicationManager",
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
                    "application",
                    core.models.ForeignKey(
                        db_constraint=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="application.application",
                        verbose_name="Application",
                    ),
                ),
                (
                    "manager",
                    core.models.ForeignKey(
                        db_constraint=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Manager",
                    ),
                ),
            ],
            options={
                "verbose_name": "Application Manager",
                "verbose_name_plural": "Application Manager",
                "ordering": ["-id"],
                "unique_together": {("application", "manager")},
            },
        ),
    ]