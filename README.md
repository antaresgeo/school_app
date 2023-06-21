# School App

Esta es una aplicación Django llamada School App, la cual permite administrar información relacionada con estudiantes, profesores, cursos y notas. A continuación, se detallan los pasos para iniciar y utilizar la aplicación.

## Requisitos previos

- Docker instalado en tu sistema. Puedes encontrar instrucciones de instalación en [https://www.docker.com/get-started](https://www.docker.com/get-started).

## Instrucciones

1. Clona el repositorio de la aplicación desde GitHub:

```bash
git clone <URL_DEL_REPOSITORIO>
```

2. Navega al directorio raíz de la aplicación:

```bash
cd school-app
```

3. Construye y levanta los contenedores Docker ejecutando el siguiente comando:

```bash
docker-compose up --build
```

Ten paciencia Esto podría tardar un rato.


Esto creará y levantará los contenedores Docker necesarios para la aplicación.

4. Una vez que los contenedores estén en funcionamiento, puedes acceder a la aplicación en tu navegador web utilizando la siguiente URL:

```
http://localhost:8000
```


## Uso de la aplicación

Una vez que la aplicación esté en funcionamiento, puedes acceder a ella utilizando las siguientes credenciales de usuario de prueba:

- **Usuario**: demo
- **Contraseña**: demo

Estas credenciales te permitirán iniciar sesión y explorar las funcionalidades de la aplicación.

Una vez dentro de la aplicación, podrás utilizar las siguientes características:

- **Importadores**: La aplicación cuenta con importadores para estudiantes, profesores y notas. Estos importadores te permitirán cargar datos desde archivos CSV u otras fuentes de datos para poblar la base de datos de la aplicación. Asegúrate de seguir las instrucciones proporcionadas en la sección correspondiente de la interfaz de usuario para utilizar los importadores de manera correcta. Ten en cuenta que para utilizar el importador de notas, es necesario haber importado previamente los cursos y haber asignado profesores y estudiantes a los mismos.

- **Scraping de cursos**: La aplicación también incluye un scraper de cursos. Esta funcionalidad te permite obtener información actualizada sobre los cursos disponibles. Puedes ejecutar el scraper desde la interfaz de usuario siguiendo las instrucciones proporcionadas. Recuerda que el scraping de cursos puede depender de fuentes externas y está sujeto a cambios en la estructura o disponibilidad de los datos.

- **Notas**: Para utilizar el importador de notas, asegúrate de haber importado previamente los cursos y haber asignado profesores y estudiantes a los mismos. Una vez realizadas estas asignaciones, podrás descargar el archivo de importación de notas que incluirá todos los cursos y estudiantes para asignar sus respectivas notas. Completa el archivo de importación con las notas correspondientes y utilízalo con el importador para cargar y asignar las notas a los estudiantes.

- **Correo**: Para recibir los correos generados por la aplicación, es necesario configurar una cuenta de correo válida en el administrador. Asegúrate de actualizar la dirección de correo electrónico del usuario "demo" en su perfil o crear un nuevo usuario en el panel de administración con una dirección de correo válida y utilizar esa cuenta para iniciar sesión y recibir los correos generados.

XD esto fue un poco complicado asi que espero que esta dmostracion cumpla los requerimientos jajajaja 
