# Generated by Django 2.0.3 on 2018-03-21 09:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0016_auto_20180321_1042'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='signal',
            options={'get_latest_by': 'datetime', 'ordering': ['datetime'], 'verbose_name_plural': 'Signalen'},
        ),
    ]
