# BOT PARA ELEGIR SERIES AL AZAR

tiene que implementar 4 tareas:
* agregar una serie
* tirar un dado para elegir la serie
* fijarse si un usuario esta conectado (el que eligio la serie que salio)
* eliminar una serie

La base de datos deberia tomar la forma de:

| --- | --- | --- |
| user | serie | ticket |
| --- | --- | --- |

Cada vez que no sale una serie se le deberia sumar un ticket hasta un maximo de 5 tickets, cada ticket aumenta la chance de que salga una serie.

# INSTALACION DEL ENTORNO DE DESARROLLO

Esto corre en python3, yo estoy usando 3.7.3 pero deberia correr en cualquier cosa.

Hay que instalar python-dotenv, discord.py y estas.

El .env contiene la llave del bot, ES CRUCIAL NO PASARSELA A NADIE.

