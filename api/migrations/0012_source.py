# Generated by Django 2.0.3 on 2018-03-15 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_auto_20180315_1257'),
    ]

    operations = [
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('naam', models.CharField(max_length=500)),
            ],
            options={
                'verbose_name_plural': 'Bronnen',
            },
        ),
    ]
