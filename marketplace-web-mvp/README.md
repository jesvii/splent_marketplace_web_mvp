# Marketplace Web MVP

Mini proyecto frontend para ver paquetes de SPLENT y sus dependencias.

## Que hace

- Muestra una lista de paquetes.
- Puedes buscar por nombre, descripcion o tags.
- Al seleccionar uno, ves:
	- version
	- descripcion
	- dependencias
	- paquetes que lo usan
	- relaciones tipo `A -> B`
- Tiene boton para copiar el comando de instalacion.

## Como ejecutarlo

Desde esta carpeta:

```bash
python3 -m http.server 8080
```

Luego abre en el navegador:

```text
http://localhost:8080
```

## Como se usa

1. En la columna izquierda tienes los paquetes.
2. Usa el buscador para filtrar.
3. Haz clic en un paquete para ver el detalle.
4. Si quieres, pulsa `Copiar` para llevarte el comando.

Ejemplo de comando:

```bash
splent install splent_feature_public
```

## Datos

Los datos salen del archivo:

`data/packages.json`
