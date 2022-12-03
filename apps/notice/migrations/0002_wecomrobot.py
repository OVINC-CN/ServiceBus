# Generated by Django 4.1.3 on 2022-12-02 17:18

from django.db import migrations, models

import core.models
import core.utils


class Migration(migrations.Migration):

    dependencies = [
        ("notice", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="WecomRobot",
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
                ("webhook", models.CharField(max_length=255, verbose_name="Webhook")),
                ("name", models.CharField(max_length=32, verbose_name="Name")),
            ],
            options={
                "verbose_name": "Wecom Robot",
                "verbose_name_plural": "Wecom Robot",
                "ordering": ["id"],
            },
        ),
    ]