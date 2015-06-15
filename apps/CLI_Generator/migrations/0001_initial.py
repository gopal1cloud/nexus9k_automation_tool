# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NexusCLI_Config_Management',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=1000)),
                ('csv_file', models.FileField(upload_to=b'', null=True, verbose_name=b'CSV File', blank=True)),
                ('cli_generator_file', models.FileField(upload_to=b'', null=True, verbose_name=b'CLI Config Generator File', blank=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('is_removed', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Nexus CLI Config Management',
                'verbose_name_plural': 'Nexus CLI Config Management',
            },
            bases=(models.Model,),
        ),
    ]
