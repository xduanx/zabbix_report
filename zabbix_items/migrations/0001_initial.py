# Generated by Django 2.2.5 on 2020-01-16 09:18

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ZabbixTablespace',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tablespace_name', models.CharField(max_length=200)),
                ('total_space', models.CharField(max_length=200)),
                ('free_space', models.CharField(max_length=200)),
                ('used_percentage', models.CharField(max_length=200)),
                ('ip', models.CharField(max_length=200)),
                ('hostname', models.CharField(max_length=200)),
                ('project', models.CharField(max_length=200)),
                ('time', models.CharField(max_length=200)),
            ],
        ),
    ]
