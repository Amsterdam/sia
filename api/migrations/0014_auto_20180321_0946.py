# Generated by Django 2.0.3 on 2018-03-21 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_auto_20180321_0943'),
    ]

    operations = [
        migrations.AlterField(
            model_name='signal',
            name='stadsdeel',
            field=models.CharField(blank=True, default='', max_length=500),
        ),
        migrations.AlterField(
            model_name='signal',
            name='text',
            field=models.CharField(default='', max_length=500),
        ),
        migrations.AlterField(
            model_name='signal',
            name='text_extra',
            field=models.CharField(blank=True, default='', max_length=500),
        ),
        migrations.AlterField(
            model_name='signal',
            name='waternet_rederij',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='status',
            name='text',
            field=models.CharField(default='', max_length=500),
        ),
    ]
