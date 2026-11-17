"""Gera garimpo/logo-padrao.jpg (usado nos apps cuja receita não tem ícone). Rodar uma vez com o Pillow."""
import os

from PIL import Image, ImageDraw

T = 512
img = Image.new("RGB", (T, T), (255, 255, 255))
d = ImageDraw.Draw(img)
# fundo em degradê âmbar com cantos arredondados
fundo = Image.new("RGB", (T, T))
fd = ImageDraw.Draw(fundo)
for y in range(T):
    t = y / T
    fd.line([(0, y), (T, y)], fill=(int(255 - 40 * t), int(183 - 60 * t), int(77 - 40 * t)))
mascara = Image.new("L", (T, T), 0)
ImageDraw.Draw(mascara).rounded_rectangle([0, 0, T - 1, T - 1], radius=112, fill=255)
img.paste(fundo, (0, 0), mascara)
# pedra lapidada
c, topo, meio, base = T // 2, 150, 225, 390
esq, dir_, e2, d2 = 120, 392, 185, 327
facetas = [
    ([(e2, topo), (c, topo), (c - 35, meio)], (255, 255, 255)),
    ([(c, topo), (d2, topo), (c + 35, meio)], (240, 248, 255)),
    ([(esq, meio), (e2, topo), (c - 35, meio)], (225, 238, 250)),
    ([(dir_, meio), (d2, topo), (c + 35, meio)], (205, 225, 245)),
    ([(c - 35, meio), (c, topo), (c + 35, meio)], (250, 252, 255)),
    ([(esq, meio), (c - 35, meio), (c, base)], (215, 232, 248)),
    ([(c - 35, meio), (c + 35, meio), (c, base)], (235, 244, 252)),
    ([(c + 35, meio), (dir_, meio), (c, base)], (190, 215, 240)),
]
for pts, cor in facetas:
    d.polygon(pts, fill=cor, outline=(150, 95, 30))
destino = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo-padrao.jpg")
img.resize((256, 256), Image.LANCZOS).save(destino, "JPEG", quality=90)
print("gravado", destino)
