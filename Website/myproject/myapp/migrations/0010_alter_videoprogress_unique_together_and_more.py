# Generated by Django 5.1.4 on 2025-06-25 08:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0009_megavideo_thumbnail'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='videoprogress',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='videoprogress',
            name='duration',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='videoprogress',
            name='mega_video',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='progress_records', to='myapp.megavideo'),
        ),
        migrations.AlterField(
            model_name='videoprogress',
            name='video',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='progress_records', to='myapp.video'),
        ),
        migrations.AddConstraint(
            model_name='videoprogress',
            constraint=models.CheckConstraint(condition=models.Q(models.Q(('mega_video__isnull', True), ('video__isnull', False)), models.Q(('mega_video__isnull', False), ('video__isnull', True)), _connector='OR'), name='myapp_videoprogress_only_one_video_type'),
        ),
    ]
