from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vet', '0004_uservet_profile_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='uservet',
            name='cantidad_valoraciones',
            field=models.PositiveIntegerField(default=0, help_text='Número de valoraciones registradas.'),
        ),
        migrations.AddField(
            model_name='uservet',
            name='promedio_puntuacion',
            field=models.FloatField(blank=True, help_text='Promedio de calificación (cache).', null=True),
        ),
        migrations.CreateModel(
            name='ValoracionVeterinario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('puntuacion', models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])),
                ('comentario', models.TextField(blank=True)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('usuario', models.ForeignKey(on_delete=models.CASCADE, related_name='valoraciones_veterinario', to=settings.AUTH_USER_MODEL)),
                ('veterinario', models.ForeignKey(on_delete=models.CASCADE, related_name='valoraciones', to='vet.uservet')),
            ],
            options={
                'verbose_name': 'Valoración de Veterinario',
                'verbose_name_plural': 'Valoraciones de Veterinarios',
            },
        ),
        migrations.AddConstraint(
            model_name='valoracionveterinario',
            constraint=models.UniqueConstraint(fields=('veterinario', 'usuario'), name='unique_valoracion_por_usuario'),
        ),
    ]
