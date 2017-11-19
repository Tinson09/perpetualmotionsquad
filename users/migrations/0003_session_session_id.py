# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_appointment_appointment_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='session_id',
            field=models.IntegerField(default=12345),
            preserve_default=False,
        ),
    ]
