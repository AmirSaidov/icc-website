"""Удаление description: данные перенесены в content / excerpt (0007)."""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cooperation', '0007_presentation_description_to_content'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='presentation',
            name='description',
        ),
        migrations.RemoveField(
            model_name='presentation',
            name='description_en',
        ),
        migrations.RemoveField(
            model_name='presentation',
            name='description_ru',
        ),
        migrations.RemoveField(
            model_name='presentation',
            name='description_zh',
        ),
    ]
