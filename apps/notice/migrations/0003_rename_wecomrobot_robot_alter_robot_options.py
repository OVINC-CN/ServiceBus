# Generated by Django 4.1.3 on 2022-12-05 17:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("notice", "0002_wecomrobot"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="WecomRobot",
            new_name="Robot",
        ),
        migrations.AlterModelOptions(
            name="robot",
            options={
                "ordering": ["id"],
                "verbose_name": "Robot",
                "verbose_name_plural": "Robot",
            },
        ),
    ]
