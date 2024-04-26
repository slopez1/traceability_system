# Generated by Django 5.0.4 on 2024-04-23 09:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('host', models.CharField(max_length=1000)),
                ('path_to_tls_ca_cert', models.CharField(max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name='OrdererNode',
            fields=[
                ('node_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='fabric.node')),
                ('tls_host_override', models.CharField(max_length=1000)),
            ],
            bases=('fabric.node',),
        ),
        migrations.CreateModel(
            name='PeerNode',
            fields=[
                ('node_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='fabric.node')),
            ],
            bases=('fabric.node',),
        ),
    ]
