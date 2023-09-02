# Generated by Django 4.2.4 on 2023-09-02 11:48

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("Chatroom", "0002_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="chatgroup",
            name="members",
            field=models.ManyToManyField(
                blank=True,
                related_name="chat_groups",
                through="Chatroom.ChatGroupMembership",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
