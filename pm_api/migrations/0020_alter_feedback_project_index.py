# Generated by Django 5.1.4 on 2025-02-06 12:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pm_api', '0019_alter_feedback_options_feedback_project_index'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedback',
            name='project_index',
            field=models.PositiveIntegerField(default=1, editable=False),
            preserve_default=False,
        ),
    ]
