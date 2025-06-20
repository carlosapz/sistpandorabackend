# Generated by Django 5.1.2 on 2025-06-14 21:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prediccion', '0007_cotizacion_contingencia_cotizacion_gastos_generales_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Proforma',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cliente', models.CharField(max_length=255)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('total_estimado', models.DecimalField(decimal_places=2, max_digits=15)),
                ('items_adicionales', models.ManyToManyField(to='prediccion.itemadicional')),
                ('productos', models.ManyToManyField(to='prediccion.producto')),
            ],
        ),
    ]
