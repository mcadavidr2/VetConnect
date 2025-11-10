import csv
from vet.models import UserVet

with open('vet_veterinario.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        UserVet.objects.create_user(
            username=row['nombre'],
            email=row['email'],
            direccion=row['direccion'],
            telefono=row['telefono'],
            latitud=row['latitud'],
            longitud=row['longitud'],
            password=row.get('password', 'default123'),  # fallback password
            cedula=row['cedula'],
            especializacion=row['especializacion']
        )