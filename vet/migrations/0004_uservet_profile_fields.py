from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vet', '0003_uservet_años_experiencia'),
    ]

    operations = [
        migrations.RenameField(
            model_name='uservet',
            old_name='años_experiencia',
            new_name='anios_experiencia',
        ),
        migrations.AddField(
            model_name='uservet',
            name='especialidades_adicionales',
            field=models.TextField(blank=True, help_text='Lista de subespecialidades', null=True),
        ),
        migrations.AddField(
            model_name='uservet',
            name='formacion_academica',
            field=models.TextField(blank=True, help_text='Resumen de títulos y universidades', null=True),
        ),
        migrations.AddField(
            model_name='uservet',
            name='horario_atencion',
            field=models.TextField(blank=True, help_text='Franja de atención semanal', null=True),
        ),
        migrations.AddField(
            model_name='uservet',
            name='idiomas',
            field=models.CharField(blank=True, help_text='Idiomas en los que atiende', max_length=120, null=True),
        ),
        migrations.AddField(
            model_name='uservet',
            name='modalidad_atencion',
            field=models.CharField(blank=True, help_text='Modalidad de atención ofrecida', max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='uservet',
            name='nombre_profesional',
            field=models.CharField(blank=True, help_text='Nombre de la persona responsable', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='uservet',
            name='numero_licencia',
            field=models.CharField(blank=True, help_text='Número de tarjeta profesional o licencia', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='uservet',
            name='servicios_destacados',
            field=models.TextField(blank=True, help_text='Procedimientos y servicios más comunes', null=True),
        ),
        migrations.AddField(
            model_name='uservet',
            name='tipo_profesional',
            field=models.CharField(blank=True, help_text='Ej: Médico Veterinario, MVZ, Zootecnista', max_length=120, null=True),
        ),
    ]
