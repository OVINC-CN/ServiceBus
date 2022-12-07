# Generated by Django 4.1.3 on 2022-12-05 22:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("application", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="application",
            name="app_logo",
            field=models.URLField(blank=True, null=True, verbose_name="App Logo"),
        ),
        migrations.AddField(
            model_name="application",
            name="app_url",
            field=models.URLField(blank=True, null=True, verbose_name="App Url"),
        ),
    ]
