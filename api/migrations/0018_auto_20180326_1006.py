# Generated by Django 2.0.3 on 2018-03-26 08:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0017_auto_20180321_1043'),
    ]

    operations = [
        migrations.AlterField(
            model_name='status',
            name='status',
            field=models.CharField(blank=True, choices=[('m', 'Gemeld'), ('i', 'In afwachting van behandeling'), ('o', 'Afgehandeld')], default='m', help_text='Melding status', max_length=1),
        ),
    ]
