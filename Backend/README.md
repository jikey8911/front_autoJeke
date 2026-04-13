# Backend de Automata Platform

Este proyecto implementa el backend de la plataforma Automata utilizando FastAPI. Se encarga de recibir peticiones a través de endpoints y solicitar información al gateway de OpenClaw.

## Estructura del Proyecto

```
Backend/
├── Dockerfile
├── docker-compose.yml
├── main.py
└── requirements.txt
```

## Requisitos

- Docker
- Docker Compose

## Configuración y Ejecución

1.  **Asegúrate de que la red externa exista:**
    El `docker-compose.yml` de este proyecto espera una red externa llamada `automataopenclaw_automata_net`. Si no existe, puedes crearla o asegurarte de que el proyecto `automataopenclaw` ya la haya creado.
    
    Además, para permitir la comunicación con el gateway de OpenClaw que se ejecuta en el host, se ha configurado `extra_hosts` en `docker-compose.yml` para mapear `host.docker.internal` a la IP del host.

2.  **Construir y levantar los servicios con Docker Compose:**
    Navega hasta el directorio `Backend` y ejecuta el siguiente comando:

    ```bash
    cd E:\antigravity\autom_platform\Backend
    docker-compose up --build -d
    ```

    Esto construirá la imagen de Docker para el backend y levantará el servicio en segundo plano.

3.  **Acceder a la API:**
    La API estará disponible en el puerto `5000`.
    Puedes acceder a la documentación interactiva de Swagger UI en `http://localhost:5000/docs`.

## Endpoints Disponibles

Todos los endpoints se comunican con el gateway de OpenClaw para obtener la información solicitada. El gateway debe esperar un payload con `data_needed` y `format_expected`.

| Endpoint           | Método | Descripción                                       |
| :----------------- | :----- | :------------------------------------------------ |
| `/agents`          | `GET`  | Obtiene la lista de agentes y sus características. |
| `/opportunities`   | `GET`  | Obtiene la lista de oportunidades encontradas.     |
| `/running_tasks`   | `GET`  | Obtiene las tareas que se están ejecutando y por qué agentes. |
| `/balance`         | `GET`  | Obtiene el balance del broker.                     |
| `/status`          | `GET`  | Obtiene el estado global del sistema.             |
| `/mitosis`         | `GET`  | Obtiene cuántos grupos se han duplicado.          |
| `/kill`            | `GET`  | Obtiene cuántos grupos han muerto.                |

## Variables de Entorno

- `OPENCLAW_GATEWAY_URL`: URL del gateway de OpenClaw. Por defecto es `http://host.docker.internal:10424`, permitiendo la comunicación con el gateway que se ejecuta en el host.
