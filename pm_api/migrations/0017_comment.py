# Generated by Django 5.1.4 on 2025-02-04 06:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pm_api', '0016_feedback_reported_by'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('content', models.TextField()),
                ('content_id', models.AutoField(primary_key=True, serialize=False)),
                ('posted_by', models.CharField(max_length=200)),
                ('posting_time', models.DateTimeField(auto_now_add=True)),
                ('feedback', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='pm_api.feedback')),
            ],
        ),
    ]
