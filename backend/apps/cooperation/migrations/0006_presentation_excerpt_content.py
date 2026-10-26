"""Presentation: анонс (excerpt) и содержимое (content) вместо description — как у News."""
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cooperation', '0005_presentation_roles'),
    ]

    operations = [
        migrations.AddField(
            model_name='presentation',
            name='content',
            field=models.TextField(blank=True, verbose_name='содержимое'),
        ),
        migrations.AddField(
            model_name='presentation',
            name='content_en',
            field=models.TextField(blank=True, null=True, verbose_name='содержимое'),
        ),
        migrations.AddField(
            model_name='presentation',
            name='content_ru',
            field=models.TextField(blank=True, null=True, verbose_name='содержимое'),
        ),
        migrations.AddField(
            model_name='presentation',
            name='content_zh',
            field=models.TextField(blank=True, null=True, verbose_name='содержимое'),
        ),
        migrations.AddField(
            model_name='presentation',
            name='excerpt',
            field=models.TextField(blank=True, help_text='Короткий текст без оформления для карточки, до 300 символов.', max_length=300, validators=[django.core.validators.MaxLengthValidator(300)], verbose_name='анонс'),
        ),
        migrations.AddField(
            model_name='presentation',
            name='excerpt_en',
            field=models.TextField(blank=True, help_text='Короткий текст без оформления для карточки, до 300 символов.', max_length=300, null=True, validators=[django.core.validators.MaxLengthValidator(300)], verbose_name='анонс'),
        ),
        migrations.AddField(
            model_name='presentation',
            name='excerpt_ru',
            field=models.TextField(blank=True, help_text='Короткий текст без оформления для карточки, до 300 символов.', max_length=300, null=True, validators=[django.core.validators.MaxLengthValidator(300)], verbose_name='анонс'),
        ),
        migrations.AddField(
            model_name='presentation',
            name='excerpt_zh',
            field=models.TextField(blank=True, help_text='Короткий текст без оформления для карточки, до 300 символов.', max_length=300, null=True, validators=[django.core.validators.MaxLengthValidator(300)], verbose_name='анонс'),
        ),
    ]
