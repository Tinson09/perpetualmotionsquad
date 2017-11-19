# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_session_session_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='approx_time',
            field=models.DurationField(default=datetime.timedelta(0, 1200)),
        ),
    ]
