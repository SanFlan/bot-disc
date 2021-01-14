# BOT PARA ELEGIR SERIES AL AZAR

Tiene que implementar las siguientes tareas:
- [x] Agregar una serie, asociarlo a su ID de usuario y darle 1 ticket.
- [x] Prohibir agregar una series ya propuesta.
- [x] Prohibir al usuario agregar una serie si ya tiene una.
- [] Eliminar una serie propuesta.
- [] Tirar un numero random (que no sea mayor a la cantidad de tickets totales entregados) y determinar la serie a ver.
- [] Avisar al usuario de que su serie salio - [A determinar con el staff] -
- [] Agregar un ticket a una serie que haya salido pero que no se vio porque su autor no estaba.
- [] Marcar una serie como vista.
- [] Mostrar las series con 5 tickets.
- [] Mostrar las series ya vistas.
- [] Permitir definir los roles con acceso a este bot.

## DB
La db de series propuestas debe tomar la forma de:

| ID (PK) | user  | serie        | cantidad tickets | fecha_visto |
| ------- | ----- | ------------ | ---------------- | ------------|
| 1       | Patas | Boku No Pico | 3                | 25/01/2021  |

## ROLL

La serie a ver se determina:

1. Se suma la cantidad de tkts totales
2. Se resta la cantidad de tkts del usuario con ID 1.
3. Si el resultado es menor a 0: se loopea el paso 2 con el ID+1. Si es mayor a 0: es la serie a ver.

## INSTALACION DEL ENTORNO DE DESARROLLO

Esto corre en python3, yo estoy usando 3.7.3 pero deberia correr en cualquier cosa.

Hay que instalar python-dotenv, discord.py y SQLAlchemy.

El .env contiene la llave del bot, ES CRUCIAL NO PASARSELA A NADIE.

