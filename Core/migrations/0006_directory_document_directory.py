# Generated by Django 4.2.4 on 2023-08-30 14:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("Core", "0005_alter_user_register_date"),
    ]

    operations = [
        migrations.CreateModel(
            name="Directory",
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
                ("dir_name", models.CharField(max_length=100)),
                ("dir_path", models.CharField(max_length=100)),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                ("expiration_date", models.DateTimeField()),
                (
                    "creater",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="dir_creater",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "last_editor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="dir_last_editor",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "task",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="directories",
                        to="Core.task",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="document",
            name="directory",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="documents",
                to="Core.directory",
            ),
        ),
    ]
