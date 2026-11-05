"""Gera os presets .kwgt do Radar Diário (KWGT / Kustom Widget).

Estrutura baseada em presets reais (preset.json versão 15 + fonts/ + thumbs).
Dados: feed RSS em GitHub Pages, lido com wg(url, rss, índice, campo).
Motion: fórmulas com df(s) (segundos) — o KWGT redesenha a cada segundo com a tela ligada.
"""
import json, time, uuid, zipfile, sys
from pathlib import Path

OUT = Path(__file__).parent / "out"
OUT.mkdir(exist_ok=True)
FONTS = Path(__file__).parent / "fonts"
FEED = "https://danielfbottega.github.io/radar-diario/feed.xml"

F = lambda name: f"kfile://org.kustom.provider/fonts/{name}"
FA = "kfile://org.kustom.provider/icons/fontawesome.ttf"
F_HEAD, F_BOLD, F_REG, F_SERIF = F("ArchivoBlack-Regular.ttf"), F("Lato-Bold.ttf"), F("Lato-Regular.ttf"), F("DMSerifDisplay-Regular.ttf")

ACC = {0: "#FF34D1BF", 1: "#FF9DA8FF", 2: "#FFC9A2FF"}
ICON = {0: "newspaper-o", 1: "book", 2: "music"}
TXT, MUTED, DIM = "#FFF2F4F8", "#B3C3CAD6", "#2EFFFFFF"
W, H = 520, 250


# ---------- helpers de módulos ----------
def mod(t, **kw):
    formulas = kw.pop("formulas", None) or {}
    d = {"internal_type": t}
    d.update({k: v for k, v in kw.items() if v is not None})
    if formulas:
        d["internal_toggles"] = {k: 10 for k in formulas}
        d["internal_formulas"] = formulas
    return d

def text(expr, size, font, color, width=None, lines=None, align=None, title=None, formulas=None, **pos):
    return mod("TextModule", internal_title=title, text_expression=expr, text_family=font, text_size=float(size),
               paint_color=color, text_size_type="FIXED_WIDTH" if width else None,
               text_width=float(width) if width else None, text_lines=float(lines) if lines else None,
               text_align=align, formulas=formulas, **pos)

def shape(kind, w, h, color, title=None, corners=None, stroke=None, angle=None, formulas=None, **extra):
    d = mod("ShapeModule", internal_title=title, shape_type=kind, shape_width=float(w), shape_height=float(h),
            paint_color=color, shape_corners=float(corners) if corners is not None else None,
            shape_angle=float(angle) if angle is not None else None, formulas=formulas, **extra)
    if stroke:
        d["paint_style"] = "STROKE"; d["paint_stroke"] = float(stroke)
    return d

def icon(name, size, color, formulas=None, **pos):
    return mod("FontIconModule", icon_set=FA, icon_icon=name, icon_size=float(size), paint_color=color, formulas=formulas, **pos)

def stack(items, stacking=None, margin=None, title=None, **pos):
    d = mod("StackLayerModule", internal_title=title, config_stacking=stacking,
            config_margin=float(margin) if margin is not None else None, **pos)
    d["viewgroup_items"] = items
    return d

def overlap(items, title=None, **pos):
    d = mod("OverlapLayerModule", internal_title=title, **pos)
    d["viewgroup_items"] = items
    return d


# ---------- peças compartilhadas ----------
def rss(field, idx="gv(sl)"):
    return f'wg(gv(feed), rss, {idx}, {field})'

def background(link_formula):
    return mod("ShapeModule", internal_title="Fundo (toque abre a página)", shape_type="RECT",
               shape_width=float(W), shape_height=float(H), shape_corners=30.0, paint_color="#FF0D1015",
               fx_gradient="VERTICAL", fx_gradient_color="#FF1A2030", fx_gradient_width=100, fx_gradient_offset=0,
               formulas={"shape_width": "$si(rwidth)$", "shape_height": "$si(rheight)$"},
               internal_events=[{"type": "SINGLE_TAP", "action": "OPEN_LINK", "url": link_formula}])

def glow():
    # brilho que "respira" atrás do visual (ciclo de 4 s)
    return shape("CIRCLE", 190, 190, "#2034D1BF", title="Brilho", position_anchor="CENTERLEFT",
                 position_padding_left=4.0,
                 formulas={"shape_width": "$170 + if(df(s)%4<2, df(s)%4, 4-df(s)%4)*14$",
                           "paint_color": "$ce(gv(acc), alpha, 12)$"})

def text_block(title_font=F_HEAD, title_size=21, with_date=True):
    label = f'$tc(up, tc(split, {rss("title")}, " | ", 0))$'
    if with_date:
        label += '  ·  $tc(up, wg(gv(feed), rss, desc))$'
    return stack([
        text(label, 12, F_BOLD, "#FF34D1BF", width=300, lines=1, title="Rótulo",
             formulas={"paint_color": "$gv(acc)$"}),
        text(f'$tc(split, {rss("title")}, " | ", 1)$', title_size, title_font, TXT, width=300, lines=2, title="Manchete"),
        text(f'${rss("desc")}$', 14, F_REG, MUTED, width=300, lines=2, title="Resumo"),
    ], margin=7, title="Textos", position_anchor="CENTERLEFT", position_padding_left=190.0, position_padding_bottom=8.0)

def live_dot(label="AO VIVO"):
    return stack([
        shape("CIRCLE", 9, 9, "#FF34D1BF", title="Pulso",
              formulas={"shape_width": "$if(df(s)%2=0, 10, 6)$", "paint_color": "$gv(acc)$"}),
        text(label, 10, F_BOLD, MUTED),
    ], stacking="HORIZONTAL_CENTER", margin=6, title="Indicador", position_anchor="TOPRIGHT",
       position_padding_right=22.0, position_padding_top=18.0)

def orbit(icon_formula=None, icon_name="newspaper-o"):
    ic = icon(icon_name, 36, "#FF34D1BF", formulas={"paint_color": "$gv(acc)$", **({"icon_icon": icon_formula} if icon_formula else {})})
    return overlap([
        shape("CIRCLE", 134, 134, "#1AFFFFFF", title="Trilho", stroke=2),
        shape("ARC", 134, 6, "#FF34D1BF", title="Órbita rápida", angle=95, shape_rotate_mode="MANUAL",
              formulas={"shape_rotate_offset": "$df(s)*24$", "paint_color": "$gv(acc)$"}),
        shape("ARC", 106, 3, "#9934D1BF", title="Órbita lenta", angle=60, shape_rotate_mode="MANUAL",
              formulas={"shape_rotate_offset": "$360-df(s)*36$", "paint_color": "$ce(gv(acc), alpha, 60)$"}),
        shape("CIRCLE", 80, 80, "#2634D1BF", title="Miolo", formulas={"paint_color": "$ce(gv(acc), alpha, 16)$"}),
        ic,
    ], title="Visual", position_anchor="CENTERLEFT", position_padding_left=28.0)

def breathing_rings():
    rings = []
    for i, base in enumerate((140, 112, 84)):
        rings.append(shape("CIRCLE", base, base, "#559DA8FF", title=f"Anel {i+1}", stroke=2,
                           formulas={"shape_width": f"${base} + if((df(s)+{i})%4<2, (df(s)+{i})%4, 4-(df(s)+{i})%4)*6$",
                                     "paint_color": f"$ce(gv(acc), alpha, {70 - i*18})$"}))
    rings.append(shape("CIRCLE", 70, 70, "#269DA8FF", title="Miolo", formulas={"paint_color": "$ce(gv(acc), alpha, 16)$"}))
    rings.append(icon("book", 32, "#FF9DA8FF", formulas={"paint_color": "$gv(acc)$"}))
    return overlap(rings, title="Visual", position_anchor="CENTERLEFT", position_padding_left=22.0)

def keyboard():
    bars = [shape("RECT", 10, 20, "#FFC9A2FF", title=f"Barra {i+1}", corners=3,
                  formulas={"shape_height": f"$10 + mu(abs, mu(sin, df(s)*47 + {i*71}))*34$",
                            "paint_color": f"$ce(gv(acc), alpha, {100 - abs(2-i)*15})$"}) for i in range(5)]
    keys = [shape("RECT", 17, 64, "#E6F2F4F8", title=f"Tecla {i+1}", corners=3,
                  formulas={"paint_color": f"$if(df(s)%7={i}, gv(acc), \"#E6F2F4F8\")$"}) for i in range(7)]
    return stack([
        stack(bars, stacking="HORIZONTAL_BOTTOM", margin=6, title="Equalizador"),
        stack(keys, stacking="HORIZONTAL_CENTER", margin=3, title="Teclado"),
    ], margin=10, title="Visual", position_anchor="CENTERLEFT", position_padding_left=26.0)

def pills():
    items = [shape("RECT", 8, 6, DIM, title=f"Página {i+1}", corners=3,
                   formulas={"shape_width": f"$if(gv(sl)={i}, 14 + gv(el)*2.4, 8)$",
                             "paint_color": f"$if(gv(sl)={i}, gv(acc), \"#33FFFFFF\")$"}) for i in range(3)]
    return stack(items, stacking="HORIZONTAL_CENTER", margin=6, title="Paginação",
                 position_anchor="BOTTOMLEFT", position_padding_left=192.0, position_padding_bottom=22.0)

def hint(label):
    return text(label + "  →", 11, F_BOLD, MUTED, title="Dica", position_anchor="BOTTOMRIGHT",
                position_padding_right=24.0, position_padding_bottom=18.0)


# ---------- presets ----------
def preset(title, desc, globals_, children):
    gl = {}
    for i, (k, v) in enumerate(globals_.items(), start=1):
        g = {"index": i, "title": k}
        g.update(v)
        gl[k] = g
    root = {"internal_events": [{"action": "KUSTOM_ACTION"}], "internal_type": "RootLayerModule",
            "globals_list": gl, "config_scale_value": 100.0, "viewgroup_items": children}
    info = {"archive": "", "author": "Radar Diário", "description": desc, "email": "", "features": "",
            "pflags": 0, "hash": None, "height": H, "id": str(uuid.uuid4()), "locked": False,
            "release": 381530915, "ts": int(time.time() * 1000), "title": title, "version": 15,
            "width": W, "xscreens": 0, "yscreens": 0}
    return {"preset_info": info, "preset_root": root}

def g_text(v): return {"type": "TEXT", "value": v}
def g_color(default, formula=None):
    d = {"type": "COLOR", "value": default}
    if formula: d.update({"toggles": 10, "global_formula": formula})
    return d

def carousel():
    acc_f = f'$if(gv(sl)=0, "{ACC[0]}", if(gv(sl)=1, "{ACC[1]}", "{ACC[2]}"))$'
    icon_f = f'$if(gv(sl)=0, "{ICON[0]}", if(gv(sl)=1, "{ICON[1]}", "{ICON[2]}"))$'
    return preset("Radar Diário · Carrossel", "Tech IA, Estudo Bíblico e Teclado se alternando a cada 20 s.",
        {"feed": g_text(FEED), "sl": g_text("$mu(floor, df(s)/20)$"), "el": g_text("$df(s)%20$"),
         "acc": g_color(ACC[0], acc_f)},
        [background(f'${rss("link")}$'), glow(), orbit(icon_formula=icon_f), text_block(), live_dot("RADAR"), pills()])

def single(idx, name, desc, visual, title_font=F_HEAD, badge="AO VIVO", hint_label="ABRIR"):
    return preset(name, desc,
        {"feed": g_text(FEED), "sl": g_text(str(idx)), "acc": g_color(ACC[idx])},
        [background(f'${rss("link")}$'), glow(), visual, text_block(title_font=title_font), live_dot(badge), hint(hint_label)])

WIDGETS = {
    "Radar_Diario_Carrossel": carousel(),
    "Radar_Tech_IA": single(0, "Radar · Tech IA", "Manchete do dia em tecnologia e IA.", orbit(icon_name=ICON[0])),
    "Radar_Estudo_Biblico": single(1, "Radar · Estudo Bíblico", "Trecho do dia, livro por livro.", breathing_rings(),
                                   title_font=F_SERIF, badge="HOJE", hint_label="ESTUDAR"),
    "Radar_Desafio_Teclado": single(2, "Radar · Teclado", "Desafio diário de inversões e rearranjo.", keyboard(),
                                    badge="DESAFIO", hint_label="PRATICAR"),
}

def fonts_used(obj, acc):
    if isinstance(obj, dict):
        for v in obj.values(): fonts_used(v, acc)
    elif isinstance(obj, list):
        for v in obj: fonts_used(v, acc)
    elif isinstance(obj, str) and obj.startswith("kfile://org.kustom.provider/fonts/"):
        acc.add(obj.rsplit("/", 1)[1])
    return acc

if __name__ == "__main__":
    thumbs = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    for key, p in WIDGETS.items():
        path = OUT / f"{key}.kwgt"
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("preset.json", json.dumps(p, ensure_ascii=False, indent=2))
            if thumbs:
                z.write(thumbs / f"{key}.jpg", "preset_thumb_portrait.jpg")
                z.write(thumbs / f"{key}.jpg", "preset_thumb_landscape.jpg")
            for fnt in sorted(fonts_used(p, set())):
                z.write(FONTS / fnt, f"fonts/{fnt}")
        print(path.name, path.stat().st_size, "bytes")
