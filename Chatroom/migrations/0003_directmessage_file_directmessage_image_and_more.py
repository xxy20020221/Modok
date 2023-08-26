# Generated by Django 4.2.4 on 2023-08-26 07:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Chatroom', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='directmessage',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='chat/files/'),
        ),
        migrations.AddField(
            model_name='directmessage',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='chat/images/'),
        ),
        migrations.AddField(
            model_name='directmessage',
            name='message_type',
            field=models.CharField(choices=[('text', 'Text'), ('image', 'Image'), ('file', 'File')], default='text', max_length=5),
        ),
        migrations.AlterField(
            model_name='directmessage',
            name='content',
            field=models.TextField(blank=True, null=True),
        ),
    ]
