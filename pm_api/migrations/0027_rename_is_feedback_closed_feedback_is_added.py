# Generated by Django 5.1.4 on 2025-02-18 08:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pm_api', '0026_remove_feedback_is_added_feedback_is_feedback_closed'),
    ]

    operations = [
        migrations.RenameField(
            model_name='feedback',
            old_name='is_feedback_closed',
            new_name='is_added',
        ),
    ]
