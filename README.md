# Marketplace Web MVP

Aplicacion web pequena para explorar paquetes de SPLENT y sus dependencias, ahora servida con Flask.

## Que Hace

- Muestra un listado de paquetes.
- Permite buscar por nombre, descripcion o tags.
- Al seleccionar un paquete, muestra:
  - version
  - descripcion
  - dependencias
  - paquetes que lo usan
  - relaciones tipo `A -> B`
- Incluye un boton para copiar el comando de instalacion.
- Expone una API JSON en `/api/packages`.

## Como Arrancarlo

Instala dependencias:

```bash
python3 -m pip install -r requirements.txt
```

Lanza el servidor:

```bash
python3 app.py
```

Abre despues:

```text
http://localhost:8080
```

## Estructura

- `app.py`: entrada Flask
- `marketplace-web-mvp/templates/index.html`: plantilla principal
- `marketplace-web-mvp/static/`: frontend estatico
- `marketplace-web-mvp/data/packages.json`: datos de paquetes
