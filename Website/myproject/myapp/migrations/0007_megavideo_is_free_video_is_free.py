# Generated by Django 4.2.20 on 2025-04-15 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0006_megavideo_views_alter_megavideo_mega_file_link_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='megavideo',
            name='is_free',
            field=models.BooleanField(default=False, help_text='Mark as free video for public viewing'),
        ),
        migrations.AddField(
            model_name='video',
            name='is_free',
            field=models.BooleanField(default=False, help_text='Mark as free video for public viewing'),
        ),
    ]
