# BOT PARA ELEGIR SERIES AL AZAR

## Caracteristicas
- Agregar una serie, asociarlo a su ID de usuario y darle 1 ticket.
- Prohibir agregar una series ya propuesta.
- Prohibir al usuario agregar una serie si ya tiene una.
- Eliminar una serie propuesta.
- Tirar un numero random (que no sea mayor a la cantidad de tickets totales entregados) y determinar la serie a ver.
- Agregar un ticket a una serie que haya salido pero que no se vio porque su autor no estaba.
- Marcar una serie como vista.
- Mostrar las series con 5 tickets.
- Mostrar las series ya vistas.


## Requisitos

- Python 3.7.3 (pero deberia correr en versiones anteriores)
- discord.py
- SQLAlchemy
- python-dotenv
- tabulate

## Import CSV

El archivo csv tiene que estar en la carpeta raiz del bot y tiene que tener el siguiente formato (el delimitador puede ser otro)

```
Nombre Usuario Discord;Nombre Serie;Tickets;Fecha(DD-MM-YY)
```

Ejemplo

```
UnPerito;Kidou Senshi Gundam: Tekketsu no Orphans;5;
Petupi;Bobobo-bo Bo-bobo;1;08-02-21
Josi;Baccano!;3;08-02-21
```