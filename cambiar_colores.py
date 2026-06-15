from PIL import Image

def recolorear(ruta_entrada, ruta_salida, color_nuevo):
    imagen = Image.open(ruta_entrada).convert("RGBA")
    pixeles = imagen.load()

    for y in range(imagen.height):
        for x in range(imagen.width):
            r, g, b, a = pixeles[x, y]

            if a == 0:
                continue

            if r > 200 and g > 200 and b > 200:
                continue

            if r < 50 and g < 50 and b < 50:
                continue

            pixeles[x, y] = (color_nuevo[0], color_nuevo[1], color_nuevo[2], a)

    imagen.save(ruta_salida)


recolorear("assets/clyde.png", "assets/patan.png", (0, 200, 0))
recolorear("assets/pinki.png", "assets/negui.png", (170, 70, 220))

print("Listo: Patan y Negui ya tienen colores nuevos.")