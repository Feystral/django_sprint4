# Generated by Django 3.2.16 on 2024-12-11 05:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('blog', '0009_auto_20241210_2304'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'verbose_name': 'комментарий', 'verbose_name_plural': 'Комментарии'},
        ),
        migrations.RemoveField(
            model_name='comment',
            name='updated_at',
        ),
        migrations.AlterField(
            model_name='comment',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Автор'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='blog.post', verbose_name='Публикация'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='text',
            field=models.TextField(help_text='Максимум 500 символов', max_length=500, verbose_name='Текст комментария'),
        ),
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='posts/', verbose_name='Изображение'),
        ),
    ]
