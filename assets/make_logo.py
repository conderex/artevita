#!/usr/bin/env python3
"""Genera el logo de Arte Vita (enso pincelado + hoja) para Instagram."""
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ---- paleta de marca (de la web) ----
CREMA    = (246, 239, 227)
CREMA2   = (239, 228, 208)
TERRACOTA= (184, 92, 56)
OCRE     = (212, 154, 74)
SALVIA   = (122, 139, 92)
CAFE     = (62, 42, 32)

S = 3            # supersampling
SIZE = 1080
W = SIZE * S
CX = CY = W // 2

def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i]-a[i])*t)) for i in range(3))

def font(path, px):
    return ImageFont.truetype(path, px)

SERIF      = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_IT   = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SERIF_REG  = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"


def soft_bg(draw, img):
    """Fondo crema con una mancha cálida ocre arriba a la derecha."""
    draw.rectangle([0, 0, W, W], fill=CREMA)
    blob = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    bd = ImageDraw.Draw(blob)
    r = int(W*0.42)
    bd.ellipse([int(W*0.62), int(-W*0.10), int(W*0.62)+r, int(-W*0.10)+r],
               fill=OCRE + (70,))
    r2 = int(W*0.38)
    bd.ellipse([int(-W*0.12), int(W*0.66), int(-W*0.12)+r2, int(W*0.66)+r2],
               fill=SALVIA + (45,))
    blob = blob.filter(ImageFilter.GaussianBlur(W//12))
    img.alpha_composite(blob)


def draw_enso(img):
    """Trazo de pincel en forma de círculo (enso) con punta afilada."""
    stroke = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stroke)
    R = W * 0.30
    a0 = math.radians(290)          # inicio (arriba-derecha)
    sweep = math.radians(320)       # casi cierra, abertura arriba
    wmax = W * 0.060
    N = 1400
    for i in range(N):
        t = i / (N - 1)
        ang = a0 + sweep * t
        # ancho: nace medio, engorda al centro, termina en punta fina
        taper = (0.45 + 0.55*math.sin(math.pi*t)) * (1.0 - 0.78*t) + 0.06
        wob = 1 + 0.05*math.sin(t*6.3) + 0.03*math.sin(t*13.0)
        rad = R * wob
        x = CX + rad*math.cos(ang)
        y = CY + rad*math.sin(ang)
        # terracota dominante, con un brillo ocre suave hacia el centro
        col = lerp(TERRACOTA, OCRE, 0.42*math.sin(t*math.pi))
        rr = max(1.0, wmax*taper)
        sd.ellipse([x-rr, y-rr, x+rr, y+rr], fill=col + (255,))
    stroke = stroke.filter(ImageFilter.GaussianBlur(S))  # bordes suaves
    img.alpha_composite(stroke)


def _leaf_shape(ld, base, length, width, theta, color):
    """Dibuja una hoja puntiaguda con su vena, partiendo de 'base'."""
    pts = []
    for k in range(41):
        u = k/40
        pts.append(((u-0.5)*length, math.sin(u*math.pi)*width*0.5))
    for k in range(41):
        u = 1-k/40
        pts.append(((u-0.5)*length, -math.sin(u*math.pi)*width*0.5))
    cx = base[0] + math.cos(theta)*length*0.5
    cy = base[1] + math.sin(theta)*length*0.5
    rot = []
    for (xx, yy) in pts:
        rot.append((cx + xx*math.cos(theta) - yy*math.sin(theta),
                    cy + xx*math.sin(theta) + yy*math.cos(theta)))
    ld.polygon(rot, fill=color+(255,))
    ld.line([(cx-math.cos(theta)*length*0.42, cy-math.sin(theta)*length*0.42),
             (cx+math.cos(theta)*length*0.42, cy+math.sin(theta)*length*0.42)],
            fill=CREMA+(150,), width=int(W*0.004))


def draw_leaf(img):
    """Brote de dos hojas de salvia naciendo de la abertura superior."""
    leaf = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    ld = ImageDraw.Draw(leaf)
    R = W * 0.30
    # abertura arriba (centro del hueco ~ -90° / 270°)
    bx = CX + R*math.cos(math.radians(270))
    by = CY + R*math.sin(math.radians(270))
    # tallo recto subiendo
    top = (bx, by - W*0.085)
    ld.line([(bx, by), top], fill=SALVIA+(255,), width=int(W*0.014))
    # dos hojas en V (brote de vida)
    _leaf_shape(ld, (bx, by - W*0.045), W*0.135, W*0.060,
                math.radians(-122), SALVIA)               # izquierda
    _leaf_shape(ld, (bx, by - W*0.045), W*0.135, W*0.060,
                math.radians(-58), SALVIA)                # derecha
    leaf = leaf.filter(ImageFilter.GaussianBlur(S))
    img.alpha_composite(leaf)


def centered_text(draw, cy, segments, gap_scale=1.0):
    """segments: lista de (texto, font, color). Centra horizontalmente."""
    widths = []
    h = 0
    for txt, f, _ in segments:
        bb = draw.textbbox((0, 0), txt, font=f)
        widths.append(bb[2]-bb[0])
        h = max(h, bb[3]-bb[1])
    total = sum(widths)
    x = CX - total/2
    for (txt, f, col), wseg in zip(segments, widths):
        bb = draw.textbbox((0, 0), txt, font=f)
        draw.text((x - bb[0], cy - bb[1] - h/2), txt, font=f, fill=col)
        x += wseg


def version_icon():
    """Avatar circular para la foto de perfil (solo emblema)."""
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    soft_bg(d, img)
    draw_enso(img)
    draw_leaf(img)
    # 'AV' dentro, discreto
    out = img.convert("RGB").resize((SIZE, SIZE), Image.LANCZOS)
    out.save("/home/user/artevita/assets/arte-vita-avatar.png")


def version_wordmark():
    """Versión con texto, para posts / portada / destacados."""
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    soft_bg(d, img)
    # emblema reducido y centrado arriba, dejando lugar al texto abajo
    emb = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    draw_enso(emb)
    draw_leaf(emb)
    scale = 0.70
    ew = int(W*scale)
    emb = emb.resize((ew, ew), Image.LANCZOS)
    img.alpha_composite(emb, (CX-ew//2, int(W*0.045)))
    d = ImageDraw.Draw(img)
    f_main = font(SERIF_REG, int(W*0.120))
    f_it   = font(SERIF_IT,  int(W*0.120))
    centered_text(d, int(W*0.825),
                  [("arte ", f_main, CAFE), ("vita", f_it, TERRACOTA)])
    f_sub = font(SERIF_REG, int(W*0.030))
    sub = "ARTETERAPIA · BIENESTAR EMOCIONAL"
    bb = d.textbbox((0,0), sub, font=f_sub)
    d.text((CX-(bb[2]-bb[0])/2, int(W*0.905)), sub, font=f_sub, fill=SALVIA)
    out = img.convert("RGB").resize((SIZE, SIZE), Image.LANCZOS)
    out.save("/home/user/artevita/assets/arte-vita-logo.png")


version_icon()
version_wordmark()
print("OK")
