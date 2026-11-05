"""Gera feed.xml (RSS 2.0) a partir de widget.json para o widget KWGT.

Cada item do feed: title = "<rotulo> | <titulo>", description = resumo, link = página.
Ordem fixa: 0 = tech, 1 = biblia, 2 = piano.
Uso: python3 build_feed.py
"""
import json
from email.utils import format_datetime
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).parent
data = json.loads((ROOT / "widget.json").read_text(encoding="utf-8"))
ordem = {"tech": 0, "biblia": 1, "piano": 2}
itens = sorted(data["itens"], key=lambda i: ordem.get(i["tipo"], 9))
quando = format_datetime(datetime.fromisoformat(data["atualizado"]))

partes = []
for it in itens:
    partes.append(
        "<item>"
        f"<title>{escape(it['rotulo'] + ' | ' + it['titulo'])}</title>"
        f"<description>{escape(it['resumo'])}</description>"
        f"<link>{escape(it['link'])}</link>"
        f"<guid isPermaLink=\"false\">{escape(it['tipo'] + '-' + data['atualizado'])}</guid>"
        f"<pubDate>{quando}</pubDate>"
        "</item>"
    )

xml = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<rss version="2.0"><channel>'
    "<title>Radar Diário</title>"
    "<link>https://danielfbottega.github.io/radar-diario/</link>"
    f"<description>{escape(data['data'])}</description>"
    f"<lastBuildDate>{quando}</lastBuildDate>"
    + "".join(partes)
    + "</channel></rss>\n"
)
(ROOT / "feed.xml").write_text(xml, encoding="utf-8")
print("feed.xml gerado com", len(itens), "itens")
