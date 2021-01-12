# BOT PARA ELEGIR SERIES AL AZAR

tiene que implementar las siguientes tareas:
* agregar una serie chequeando que:
  - no haya sido propuesta (duplicación)
  - quien la proponga no tenga otra asignada.
* tirar un dado para elegir la serie
* fijarse si un usuario esta conectado (el que eligio la serie que salio)
* eliminar una serie (manual y automaticamente)
* adoptar series?

## DB
La db de series propuestas debe tomar la forma de:

| ID (PK) | user  | serie        | cantidad tickets | visto    |
| ------- | ----- | ------------ | ---------------- | -------- |
| 1       | Patas | Boku No Pico | 3                | True     |

Cada vez que no sale una serie se le deberia sumar un ticket hasta un maximo de 5 tickets, cada ticket aumenta la chance de que salga una serie.

La ddbbb de series vistas debe tomar la forma de:

| serie        | fecha visto |
| ------------ | ----------- |
| Boku No Pico | 23/1/2021   |

## ROLL

La serie a ver se determina:

1. Se suma la cantidad de tkts totales
2. Se resta la cantidad de tkts del usuario con ID 1.
3. Si el resultado es menor a 0: se loopea el paso 2 con el ID+1. Si es mayor a 0: es la serie a ver.

## INSTALACION DEL ENTORNO DE DESARROLLO

Esto corre en python3, yo estoy usando 3.7.3 pero deberia correr en cualquier cosa.

Hay que instalar python-dotenv, discord.py y estas.

El .env contiene la llave del bot, ES CRUCIAL NO PASARSELA A NADIE.

