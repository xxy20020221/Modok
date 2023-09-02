# Generated by Django 4.2.4 on 2023-09-01 15:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("Chatroom", "0001_initial"),
        ("Core", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="message",
            name="group",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="Chatroom.chatgroup"
            ),
        ),
        migrations.AddField(
            model_name="message",
            name="sender",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="mention",
            name="message",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="Chatroom.message"
            ),
        ),
        migrations.AddField(
            model_name="mention",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="editmessage",
            name="document",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="Core.document",
            ),
        ),
        migrations.AddField(
            model_name="editmessage",
            name="editor",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="directmessage",
            name="receiver",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="received_direct_messages",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="directmessage",
            name="sender",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="sent_direct_messages",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="chatgroupmembership",
            name="chat_group",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="Chatroom.chatgroup"
            ),
        ),
        migrations.AddField(
            model_name="chatgroupmembership",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="chatgroup",
            name="group_manager",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="managed_groups",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="chatgroup",
            name="members",
            field=models.ManyToManyField(
                blank=True,
                null=True,
                related_name="chat_groups",
                through="Chatroom.ChatGroupMembership",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="chatgroup",
            name="team",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="Core.team"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="chatgroupmembership", unique_together={("user", "chat_group")},
        ),
    ]
