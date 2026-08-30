"""Erzeugt aus contours_data.json den Höhenlinien-Hintergrund als CSS-Data-URI.

Sandfarbene Variante: Sepia-Höhenlinien auf Sandpapier, wie auf einer
gedruckten topografischen Karte. Index-Höhenlinien (jede vierte) werden
kräftiger und dicker gezeichnet als die Zwischenlinien.
"""
import json
import pathlib
from urllib.parse import quote

HERE = pathlib.Path(__file__).parent

# Sepia auf Sand, bewusst sehr schwach. Der Hintergrund soll als Textur
# spürbar sein, aber niemals mit dem Text um Aufmerksamkeit konkurrieren.
# Die Linien liegen daher nur wenige Prozent neben dem Sandton #E9E0CD.
LINE_SOFT = "#E2D8C1"   # Zwischenhöhenlinie
LINE_INDEX = "#D9CDB1"  # Index-Höhenlinie (jede vierte)
WIDTH_SOFT = "0.9"
WIDTH_INDEX = "1.3"


def build_svg(data):
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {data["viewW"]} {data["viewH"]}">'
    ]
    for p in data["paths"]:
        is_index = p["index"]
        color = LINE_INDEX if is_index else LINE_SOFT
        width = WIDTH_INDEX if is_index else WIDTH_SOFT
        parts.append(
            f'<path d="{p["d"]}" fill="none" '
            f'stroke="{color}" stroke-width="{width}"/>'
        )
    parts.append("</svg>")
    return "".join(parts)


def to_data_uri(svg):
    # safe="" lässt nichts ungequotet, das hält die URI robust in CSS.
    return 'url("data:image/svg+xml,' + quote(svg, safe="") + '")'


def main():
    data = json.loads((HERE / "contours_data.json").read_text())
    svg = build_svg(data)
    uri = to_data_uri(svg)
    (HERE / "topo_bg_sand.txt").write_text(uri)
    print(f"Pfade: {len(data['paths'])}")
    print(f"SVG: {len(svg):,} Zeichen")
    print(f"Data-URI: {len(uri):,} Zeichen")


if __name__ == "__main__":
    main()
