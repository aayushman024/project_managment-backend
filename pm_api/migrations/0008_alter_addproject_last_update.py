# Generated by Django 4.2.16 on 2025-01-22 04:53

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('pm_api', '0007_alter_addproject_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='addproject',
            name='last_update',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
