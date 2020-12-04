# Generated by Django 3.1.4 on 2020-12-03 12:11

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=250)),
                ('description', models.TextField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'collection',
                'unique_together': {('user', 'title')},
            },
        ),
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=250)),
                ('description', models.TextField(blank=True, null=True)),
                ('genres', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=150), size=None)),
                ('collection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='movies.collection')),
            ],
            options={
                'db_table': 'movie',
                'unique_together': {('collection', 'title')},
            },
        ),
    ]