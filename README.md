# TechGear · Catálogo y pedidos

Aplicación web híbrida para una tienda en línea de tecnología:

- **API (FastAPI + MongoDB):** administra productos, usuarios y pedidos.
- **Portal web (Django, patrón MVT):** consume la API por HTTP y muestra el catálogo, el login, las compras y la gestión de productos.

## Despliegues

| Servicio | URL |
|---|---|
| Portal web (Django en Vercel) | https://proyecto2-fast-api-one.vercel.app/ |
| API (FastAPI) | `https://TU-API.onrender.com` ← reemplaza por la URL de tu API |
| Documentación Swagger | `https://TU-API.onrender.com/docs` |

> Si la API está en el plan gratuito de Render, se "duerme" tras 15 minutos sin uso y la primera petición puede tardar cerca de un minuto. Para una demo, abre primero `/docs`.

## Tecnologías

- Python 3, FastAPI, Pydantic, Uvicorn
- MongoDB (PyMongo)
- Autenticación: JWT en el login (usuarios) y API key para las rutas de administración
- Django (plantillas, sesiones) y Requests
- Despliegue: Vercel (web) y Render (API)

## Estructura del repositorio

```
.
├── techgear_api/            # Código de FastAPI
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── security.py      # API key y JWT
│   │   ├── utils.py
│   │   ├── models/          # Esquemas Pydantic (producto, pedido, usuarios)
│   │   └── routers/         # productos, pedidos, usuarios
│   ├── requirements.txt
│   └── .env
├── techgear_web/            # Proyecto Django
│   ├── manage.py
│   ├── app.py               # Punto de entrada para Vercel
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── store/               # Vistas, urls, cliente de la API, decoradores
│   ├── templates/           # Plantillas HTML (base, catálogo, login, registro, pedidos...)
│   ├── requirements.txt
│   └── .env
└── README.md
```

## Roles

| Rol | Qué puede hacer |
|---|---|
| **Cliente** | Ver el catálogo, comprar productos indicando cantidad y dirección de envío, y consultar su historial en "Mis pedidos". |
| **Administrador** | Ver el panel de administración, crear, editar y eliminar productos. No realiza compras. |

El rol se guarda en la colección `usuarios` de MongoDB. Todos los registros nuevos son **cliente**. Para crear un administrador, regístrate normalmente y, en la base de datos (colección `usuarios`), cambia el campo `rol` a `administrador`.

En el login se elige "Cliente" o "Administrador", pero el sistema compara esa opción con el rol real guardado en la base de datos.

## Endpoints de la API

| Método | Ruta | Acceso | Descripción |
|---|---|---|---|
| GET | `/productos/` | Público | Lista productos (`?categoria=`, `skip`, `limit`) |
| GET | `/productos/{id}` | Público | Detalle de un producto |
| POST | `/productos/` | API key | Crea un producto |
| PUT | `/productos/{id}` | API key | Actualiza un producto |
| DELETE | `/productos/{id}` | API key | Elimina un producto |
| POST | `/usuarios/registro` | Público | Registra un cliente |
| POST | `/usuarios/login` | Público | Devuelve el token JWT y los datos del usuario |
| POST | `/pedidos/` | Público* | Crea un pedido y descuenta el stock |
| GET | `/pedidos/?usuario_id=` | Público* | Historial de pedidos de un cliente (`usuario_id` obligatorio) |
| GET | `/pedidos/{id}` | Público* | Detalle de un pedido |
| GET | `/pedidos/admin/todos` | API key | Todos los pedidos |
| PATCH | `/pedidos/{id}/estado` | API key | Cambia el estado de un pedido (`pendiente`, `enviado`, `entregado`, `cancelado`) |

\* Estas rutas todavía no validan el token JWT; ver [Limitaciones y mejoras](#limitaciones-y-mejoras).

El cuerpo de `POST /pedidos/` incluye `usuario_id`, `usuario_email`, `usuario_nombre`, `items` (lista de `producto_id` y `cantidad`) y `direccion_envio`.

Códigos principales: `201` creado, `400` solicitud incompleta, `401`/`403` credenciales o permisos inválidos, `404` no encontrado, `409` stock insuficiente, `422` datos inválidos.

### Probar en Swagger

1. Abre `/docs`.
2. Para las rutas con candado (administración): pulsa **Authorize** y pega la API key en el campo del encabezado `X-API-Key`.

## Variables de entorno

Nunca subas archivos `.env` al repositorio.

### `techgear_api/.env`

| Variable | Descripción |
|---|---|
| `MONGODB_URI` | Cadena de conexión de MongoDB |
| `MONGODB_DB` | Nombre de la base de datos |
| `API_KEY` | Clave para las rutas de administración |
| `JWT_SECRET` | Clave para firmar los tokens JWT |
| `JWT_EXPIRE_MINUTES` | Duración del token en minutos |

### `techgear_web/.env`

| Variable | Descripción |
|---|---|
| `API_URL` | URL de la API (`http://127.0.0.1:8000` en local) |
| `API_KEY` | La **misma** clave configurada en la API |
| `SECRET_KEY` | Clave secreta de Django |
| `DEBUG` | `True` en desarrollo, `False` en producción |

Para generar una clave segura:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

## Ejecutar en local

Necesitas Python 3.12 o superior, una base de datos MongoDB y dos terminales.

### 1. API (puerto 8000)

```bash
cd techgear_api
python -m venv venv
venv\Scripts\activate            # Windows (PowerShell)
# source venv/bin/activate       # macOS / Linux
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Documentación en http://127.0.0.1:8000/docs

### 2. Portal web (puerto 8001)

```bash
cd techgear_web
python -m venv .venv
.venv\Scripts\activate           # Windows (PowerShell)
# source .venv/bin/activate      # macOS / Linux
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8001
```

Abre http://127.0.0.1:8001

Si cambias un archivo `.env`, reinicia el servidor correspondiente.

## Despliegue

### API (por ejemplo, en Render)

- **Root Directory:** `techgear_api`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Variables:** `MONGODB_URI`, `MONGODB_DB`, `API_KEY`, `JWT_SECRET`, `JWT_EXPIRE_MINUTES`
- Si usas MongoDB Atlas, en **Network Access** permite las IP del servicio donde despliegues.

### Web en Vercel

- **Root Directory:** `techgear_web`
- **Punto de entrada:** `app.py`, que expone la aplicación WSGI de Django como `app`.
- **Variables:** `API_URL` (URL pública de la API), `API_KEY`, `SECRET_KEY`, `DEBUG=False`
- `ALLOWED_HOSTS` debe incluir `.vercel.app`.
- Las sesiones se guardan en cookies firmadas, porque Vercel no tiene disco persistente para SQLite.
- `API_URL` no puede ser `127.0.0.1`: la API debe estar desplegada con una URL pública.

## Flujo de la aplicación

1. El visitante ve el catálogo. Al pulsar **Comprar**, si no tiene sesión, pasa al login y luego vuelve a la compra.
2. Al iniciar sesión, Django recibe el JWT y los datos del usuario desde la API y los guarda en la sesión.
3. El cliente confirma la compra indicando cantidad y dirección de envío. La API descuenta el stock de forma atómica, calcula el total y registra el pedido.
4. El cliente consulta sus compras en **Mis pedidos**.
5. El administrador crea productos desde el **Panel de administración** y los edita o elimina con los botones del catálogo. Django envía la `API_KEY` a la API desde el servidor, sin exponerla al navegador.

## Diseño y accesibilidad

- Tema oscuro responsive, con tipografía Space Grotesk y estilos incluidos en las plantillas.
- Mejoras de accesibilidad: contraste de color, enlace "Saltar al contenido", etiquetas en los campos, jerarquía de encabezados, nombres únicos en los botones y navegación por teclado con foco visible.
- Favicon incluido en la plantilla base, sin archivos estáticos adicionales.

## Limitaciones y mejoras

- Las rutas de pedidos todavía no validan el token JWT. Lo ideal es obtener el usuario desde el token en lugar de recibir `usuario_id` en la petición, para que un cliente no pueda ver ni crear pedidos a nombre de otro.
- Un pedido admite hoy un producto por compra desde la interfaz; la API ya acepta varios `items` en un mismo pedido, por lo que se puede ampliar con un carrito.
- El panel de administración no incluye todavía la gestión de estados de los pedidos (la API ya expone `PATCH /pedidos/{id}/estado`).

## Control de versiones

Todo el trabajo se realiza en la rama `main`, con commits descriptivos.