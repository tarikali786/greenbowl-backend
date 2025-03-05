# Generated by Django 4.2.15 on 2025-03-04 08:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salad', '0004_recipe'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ['-created_at']},
        ),
        migrations.AddField(
            model_name='order',
            name='name',
            field=models.CharField(blank=True, help_text='Recipe name', max_length=250, null=True),
        ),
    ]
