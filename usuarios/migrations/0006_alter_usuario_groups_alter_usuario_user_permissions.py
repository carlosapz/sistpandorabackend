# Generated by Django 5.1.2 on 2025-06-01 05:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('usuarios', '0005_historialactividad'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='Grupos a los que pertenece este usuario.', related_name='custom_user_groups', to='auth.group', verbose_name='groups'),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Permisos específicos para este usuario.', related_name='custom_user_permissions', to='auth.permission', verbose_name='user permissions'),
        ),
    ]
