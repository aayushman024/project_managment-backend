# Generated by Django 4.2.16 on 2025-01-30 15:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pm_api', '0012_alter_feedback_assigned_to'),
    ]

    operations = [
        migrations.AddField(
            model_name='addproject',
            name='is_added_feedback_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='addproject',
            name='total_feedback_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
