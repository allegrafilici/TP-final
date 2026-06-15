from PIL import Image
from pathlib import Path
import shutil

def fondo_oscuro_a_transparente(ruta_imagen, tolerancia=45):
    imagen = Image.open(ruta_imagen).convert("RGBA")
    pixeles = imagen.load()

    ancho, alto = imagen.size
    visitados = set()
    pendientes = []

    # Agarramos los bordes de la imagen.
    # La idea es borrar SOLO el fondo oscuro conectado al borde,
    # no los ojos ni detalles negros internos del fantasma.
    for x in range(ancho):
        pendientes.append((x, 0))
        pendientes.append((x, alto - 1))

    for y in range(alto):
        pendientes.append((0, y))
        pendientes.append((ancho - 1, y))

    while pendientes:
        x, y = pendientes.pop()

        if (x, y) in visitados:
            continue

        if x < 0 or x >= ancho or y < 0 or y >= alto:
            continue

        visitados.add((x, y))

        r, g, b, a = pixeles[x, y]

        # Detecta fondo oscuro
        if r <= tolerancia and g <= tolerancia and b <= tolerancia:
            pixeles[x, y] = (r, g, b, 0)

            pendientes.append((x + 1, y))
            pendientes.append((x - 1, y))
            pendientes.append((x, y + 1))
            pendientes.append((x, y - 1))

    imagen.save(ruta_imagen)


# Hace backup antes de modificar
carpeta_assets = Path("assets")
backup = Path("backup_assets_png")

if not backup.exists():
    shutil.copytree(carpeta_assets, backup)

# Procesa todos los png dentro de assets y subcarpetas
for archivo in carpeta_assets.rglob("*.png"):
    fondo_oscuro_a_transparente(archivo)
    print("Fondo quitado:", archivo)

print("Listo. Los fondos oscuros ahora son transparentes.")