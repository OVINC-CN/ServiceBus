# Generated by Django 4.1.3 on 2022-12-04 12:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import core.models
import core.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="COSLog",
            fields=[
                (
                    "id",
                    core.models.UniqIDField(
                        default=core.utils.uniq_id_without_time,
                        max_length=32,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "file_name",
                    models.CharField(max_length=255, verbose_name="File Name"),
                ),
                (
                    "file_path",
                    models.CharField(max_length=255, unique=True, verbose_name="File Path"),
                ),
                (
                    "file_size",
                    models.IntegerField(default=int, verbose_name="File Size"),
                ),
                (
                    "extra_params",
                    models.TextField(blank=True, null=True, verbose_name="Extra Params"),
                ),
                (
                    "upload_result",
                    models.TextField(blank=True, null=True, verbose_name="Upload Result"),
                ),
                (
                    "upload_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Upload At"),
                ),
                (
                    "upload_by",
                    core.models.ForeignKey(
                        db_constraint=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="????????????",
                    ),
                ),
            ],
            options={
                "verbose_name": "COS Log",
                "verbose_name_plural": "COS Log",
                "ordering": ["-upload_at"],
            },
        ),
    ]
