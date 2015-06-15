# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CLI_Generator', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nexuscli_config_management',
            name='cli_generator_file',
            field=models.FileField(upload_to=b'Nexus_CLI_Config_Files', null=True, verbose_name=b'CLI Config Generator File', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='nexuscli_config_management',
            name='csv_file',
            field=models.FileField(upload_to=b'Nexus_CLI_Config_Files', null=True, verbose_name=b'CSV File', blank=True),
            preserve_default=True,
        ),
    ]
