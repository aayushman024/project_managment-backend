# Generated by Django 4.2.16 on 2025-01-29 04:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pm_api', '0011_feedback_is_bug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedback',
            name='assigned_to',
            field=models.CharField(blank=True, default='', max_length=200, null=True),
        ),
    ]
