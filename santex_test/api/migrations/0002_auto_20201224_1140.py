# Generated by Django 3.1 on 2020-12-24 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="team",
            name="email",
            field=models.EmailField(max_length=254, null=True),
        ),
    ]