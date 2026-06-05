"""
Script para generar la presentación de UTourist — DSA Final Project
Ejecutar: python3 generate_presentation.py
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
import copy

# ─── PALETA DE COLORES ───────────────────────────────────────────────────────
AZUL_OSCURO  = RGBColor(0x1B, 0x3A, 0x5C)   # fondos de sección
TEAL         = RGBColor(0x2E, 0x9B, 0x8F)   # acentos / headers
NARANJA      = RGBColor(0xF4, 0xA5, 0x35)   # highlights
BLANCO       = RGBColor(0xFF, 0xFF, 0xFF)
GRIS_CLARO   = RGBColor(0xF0, 0xF4, 0xF8)
GRIS_TEXTO   = RGBColor(0x2D, 0x3E, 0x50)
VERDE_SUAVE  = RGBColor(0x27, 0xAE, 0x60)
ROJO_SUAVE   = RGBColor(0xE7, 0x4C, 0x3C)
TEAL_OSCURO  = RGBColor(0x1A, 0x6B, 0x62)

SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.5)

prs = Presentation()
prs.slide_width  = SLIDE_W
prs.slide_height = SLIDE_H

blank_layout = prs.slide_layouts[6]   # completamente en blanco

# ─── HELPERS ─────────────────────────────────────────────────────────────────

def add_rect(slide, left, top, width, height, fill_color, alpha=None):
    shape = slide.shapes.add_shape(
        1, Inches(left), Inches(top), Inches(width), Inches(height)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    shape.line.fill.background()
    return shape


def add_text(slide, text, left, top, width, height,
             font_size=18, bold=False, color=BLANCO,
             align=PP_ALIGN.LEFT, italic=False, wrap=True):
    tb = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    tf = tb.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    run.font.name = "Calibri"
    return tb


def add_multiline(slide, lines, left, top, width, height,
                  font_size=16, color=BLANCO, line_spacing=1.15):
    """lines: list of (text, bold, size_override)"""
    tb = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    tf = tb.text_frame
    tf.word_wrap = True
    first = True
    for item in lines:
        if isinstance(item, str):
            text, bold, sz = item, False, font_size
        else:
            text = item[0]
            bold = item[1] if len(item) > 1 else False
            sz   = item[2] if len(item) > 2 else font_size

        if first:
            p = tf.paragraphs[0]
            first = False
        else:
            p = tf.add_paragraph()

        p.alignment = PP_ALIGN.LEFT
        run = p.add_run()
        run.text = text
        run.font.size = Pt(sz)
        run.font.bold = bold
        run.font.color.rgb = color
        run.font.name = "Calibri"
    return tb


def dark_slide(slide):
    add_rect(slide, 0, 0, 13.33, 7.5, AZUL_OSCURO)


def section_header(slide, title, subtitle=""):
    """Slide de separación entre secciones"""
    add_rect(slide, 0, 0, 13.33, 7.5, AZUL_OSCURO)
    add_rect(slide, 0, 2.8, 13.33, 0.08, TEAL)
    add_text(slide, title, 1.5, 2.3, 10, 1.2,
             font_size=40, bold=True, color=BLANCO, align=PP_ALIGN.CENTER)
    if subtitle:
        add_text(slide, subtitle, 1.5, 3.5, 10, 0.8,
                 font_size=20, color=TEAL, align=PP_ALIGN.CENTER)


def content_slide_bg(slide):
    add_rect(slide, 0, 0, 13.33, 7.5, GRIS_CLARO)
    add_rect(slide, 0, 0, 13.33, 1.1, AZUL_OSCURO)


def slide_title(slide, title, subtitle=""):
    add_text(slide, title, 0.4, 0.15, 12.5, 0.7,
             font_size=26, bold=True, color=BLANCO)
    if subtitle:
        add_text(slide, subtitle, 0.4, 0.72, 12.5, 0.35,
                 font_size=14, color=TEAL)


def footer(slide, num, total=28):
    add_rect(slide, 0, 7.2, 13.33, 0.3, AZUL_OSCURO)
    add_text(slide, "UTourist · Algoritmos y Estructuras de Datos · UVG 2026",
             0.3, 7.22, 10, 0.25, font_size=9, color=TEAL)
    add_text(slide, f"{num} / {total}", 12.5, 7.22, 0.8, 0.25,
             font_size=9, color=BLANCO, align=PP_ALIGN.RIGHT)


def bullet_box(slide, title, bullets, left, top, width, height,
               bg=AZUL_OSCURO, title_color=TEAL, bullet_color=BLANCO,
               font_size=15, title_size=17):
    add_rect(slide, left, top, width, height, bg)
    add_text(slide, title, left+0.15, top+0.12, width-0.3, 0.4,
             font_size=title_size, bold=True, color=title_color)
    lines = []
    for b in bullets:
        lines.append((f"  {b}", False, font_size))
    add_multiline(slide, lines, left+0.15, top+0.58,
                  width-0.3, height-0.7, font_size=font_size, color=bullet_color)


TOTAL = 28

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 1 — PORTADA
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
add_rect(s, 0, 0, 13.33, 7.5, AZUL_OSCURO)
add_rect(s, 0, 0, 13.33, 0.6, TEAL)
add_rect(s, 0, 6.9, 13.33, 0.6, TEAL)

add_text(s, "🗺  UTourist", 1, 1.4, 11.33, 1.4,
         font_size=60, bold=True, color=BLANCO, align=PP_ALIGN.CENTER)
add_text(s, "Sistema de Recomendaciones Turísticas con Grafos",
         1, 2.9, 11.33, 0.7, font_size=26, color=TEAL, align=PP_ALIGN.CENTER)
add_rect(s, 3.5, 3.75, 6.33, 0.06, NARANJA)
add_text(s, "Algoritmos y Estructuras de Datos · UVG 2026",
         1, 3.95, 11.33, 0.5, font_size=17, color=GRIS_CLARO, align=PP_ALIGN.CENTER)
add_text(s, "Marco Prera   ·   Fabricio Estrada   ·   Mauricio Corado   ·   Sebastián Rodas",
         1, 4.6, 11.33, 0.5, font_size=15, color=TEAL, align=PP_ALIGN.CENTER)
add_text(s, "Django  ·  Neo4j  ·  neomodel  ·  Python",
         1, 5.3, 11.33, 0.4, font_size=13, color=GRIS_CLARO, align=PP_ALIGN.CENTER, italic=True)
footer(s, 1, TOTAL)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 2 — AGENDA
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
content_slide_bg(s)
slide_title(s, "Agenda", "45 minutos · 4 secciones")

items = [
    ("01", "Contexto y Problema", "5 min", TEAL),
    ("02", "Arquitectura y Base de Datos en Grafos", "10 min", VERDE_SUAVE),
    ("03", "Algoritmos de Recomendación (DSA Core)", "18 min", NARANJA),
    ("04", "Implementación, Demo y Conclusiones", "12 min", TEAL),
]

for i, (num, title, dur, col) in enumerate(items):
    lft = 0.5
    tp = 1.4 + i * 1.35
    add_rect(s, lft, tp, 0.7, 1.05, col)
    add_text(s, num, lft, tp+0.2, 0.7, 0.6,
             font_size=28, bold=True, color=BLANCO, align=PP_ALIGN.CENTER)
    add_rect(s, lft+0.7, tp, 10.3, 1.05, AZUL_OSCURO)
    add_text(s, title, lft+0.9, tp+0.12, 8, 0.45,
             font_size=20, bold=True, color=BLANCO)
    add_text(s, dur, lft+0.9, tp+0.6, 8, 0.3,
             font_size=13, color=TEAL)
footer(s, 2, TOTAL)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 3 — EL PROBLEMA
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
content_slide_bg(s)
slide_title(s, "El Problema", "Estudiantes universitarios y el turismo en Guatemala")

add_text(s, "¿Cómo decide un estudiante a dónde viajar?",
         0.5, 1.3, 12, 0.6, font_size=22, bold=True, color=GRIS_TEXTO)

pain_points = [
    ("💸", "Presupuesto limitado y variable por persona"),
    ("🗺", "Guatemala tiene más de 300 destinos turísticos documentados"),
    ("🤷", "Las recomendaciones genéricas no consideran carrera ni gustos reales"),
    ("📱", "No existe una plataforma enfocada en el perfil universitario guatemalteco"),
]

for i, (icon, text) in enumerate(pain_points):
    add_rect(s, 0.5, 2.1 + i*1.1, 12.3, 0.95, AZUL_OSCURO)
    add_text(s, icon, 0.65, 2.15 + i*1.1, 0.7, 0.7, font_size=22, color=BLANCO)
    add_text(s, text, 1.5, 2.2 + i*1.1, 10.9, 0.7, font_size=17, color=BLANCO)
footer(s, 3, TOTAL)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 4 — LA SOLUCIÓN
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
add_rect(s, 0, 0, 13.33, 7.5, AZUL_OSCURO)
add_rect(s, 0, 0, 13.33, 1.1, TEAL_OSCURO)
add_text(s, "La Solución · UTourist", 0.4, 0.2, 12.5, 0.7,
         font_size=26, bold=True, color=BLANCO)

add_text(s, "Un motor de recomendaciones personalizado para estudiantes universitarios,\nbasado en grafos de conocimiento y algoritmos híbridos.",
         0.8, 1.25, 11.5, 1.0, font_size=20, color=TEAL, italic=True, align=PP_ALIGN.CENTER)

pillars = [
    ("🎯", "Personalizado", "Por carrera, presupuesto\ne intereses declarados"),
    ("🕸", "Basado en Grafos", "Neo4j modela relaciones\nentre usuarios y destinos"),
    ("🤖", "Algoritmo Híbrido", "Content + Collaborative\n+ Demographic Filtering"),
    ("🇬🇹", "Datos Reales", "31 destinos guatemaltecos\ncon coordenadas y costos"),
]

for i, (icon, title, desc) in enumerate(pillars):
    x = 0.5 + i * 3.1
    add_rect(s, x, 2.5, 2.8, 3.8, TEAL_OSCURO)
    add_text(s, icon, x, 2.7, 2.8, 0.6, font_size=30, align=PP_ALIGN.CENTER)
    add_text(s, title, x, 3.4, 2.8, 0.5, font_size=16, bold=True,
             color=NARANJA, align=PP_ALIGN.CENTER)
    add_text(s, desc, x+0.1, 4.05, 2.6, 1.5, font_size=13, color=BLANCO,
             align=PP_ALIGN.CENTER)
footer(s, 4, TOTAL)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 5 — STACK TECNOLÓGICO
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
content_slide_bg(s)
slide_title(s, "Stack Tecnológico", "Herramientas seleccionadas y justificación")

techs = [
    ("Django 6.0", "Framework web", "Autenticación, sesiones, ORM relacional para usuarios, REST API, templates HTML", TEAL),
    ("Neo4j 5.19", "Base de datos en grafo", "Almacena nodos y relaciones del grafo turístico. Consultas Cypher nativas para traversals", VERDE_SUAVE),
    ("neomodel 5.3", "OGM para Neo4j", "Mapeo de nodos a clases Python. Recomendado oficialmente por Neo4j (absorbió py2neo)", NARANJA),
    ("django-neomodel", "Integración OGM-Django", "Conecta el ciclo de vida de neomodel con la señalización y configuración de Django", TEAL),
    ("Python 3.10+", "Lenguaje base", "Tipado estático, dataclasses, math para cálculo de scores, random para serendipity", GRIS_TEXTO),
]

for i, (name, role, desc, col) in enumerate(techs):
    row = i // 3
    col_pos = i % 3
    x = 0.4 + col_pos * 4.3
    y = 1.3 + row * 2.85
    w = 4.0
    h = 2.6
    add_rect(s, x, y, w, h, AZUL_OSCURO)
    add_rect(s, x, y, w, 0.08, col)
    add_text(s, name, x+0.1, y+0.15, w-0.2, 0.4,
             font_size=17, bold=True, color=BLANCO)
    add_text(s, role, x+0.1, y+0.6, w-0.2, 0.35,
             font_size=13, color=col)
    add_text(s, desc, x+0.1, y+1.0, w-0.2, 1.4,
             font_size=12, color=GRIS_CLARO)
footer(s, 5, TOTAL)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 6 — SEPARADOR SECCIÓN 2
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
section_header(s, "02 · Grafos como Estructura de Datos",
               "Por qué Neo4j · Modelo de datos · Relaciones")
footer(s, 6, TOTAL)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 7 — ¿POR QUÉ GRAFOS?
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
content_slide_bg(s)
slide_title(s, "¿Por qué una Base de Datos en Grafo?",
            "Comparación con modelo relacional")

add_rect(s, 0.4, 1.2, 5.9, 5.7, AZUL_OSCURO)
add_text(s, "SQL Relacional", 0.55, 1.35, 5.6, 0.45,
         font_size=17, bold=True, color=ROJO_SUAVE)
sql_bullets = [
    "Requiere JOINs múltiples para traversals",
    "Query O(n²) para encontrar usuarios similares",
    "Agregar relaciones = alterar esquema",
    "Relaciones almacenadas como foreign keys",
    "Consulta típica: 5+ tablas para recomendar",
]
for i, b in enumerate(sql_bullets):
    add_text(s, f"✗  {b}", 0.55, 1.95 + i*0.85, 5.6, 0.75,
             font_size=13, color=GRIS_CLARO)

add_rect(s, 7.0, 1.2, 5.9, 5.7, AZUL_OSCURO)
add_text(s, "Neo4j — Grafo", 7.15, 1.35, 5.6, 0.45,
         font_size=17, bold=True, color=VERDE_SUAVE)
neo_bullets = [
    "Traversals son operaciones nativas O(k)",
    "Node Similarity: comparar vecindarios directamente",
    "Relaciones son ciudadanos de primera clase",
    "Propiedades en aristas (rating, weight, distance)",
    "Consulta típica: 1 patrón Cypher de 4 nodos",
]
for i, b in enumerate(neo_bullets):
    add_text(s, f"✓  {b}", 7.15, 1.95 + i*0.85, 5.6, 0.75,
             font_size=13, color=GRIS_CLARO)

add_rect(s, 6.0, 1.2, 1.0, 5.7, GRIS_CLARO)
add_text(s, "VS", 6.0, 3.9, 1.0, 0.6, font_size=22, bold=True,
         color=AZUL_OSCURO, align=PP_ALIGN.CENTER)
footer(s, 7, TOTAL)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 8 — NODOS DEL MODELO
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
content_slide_bg(s)
slide_title(s, "Modelo de Datos · Nodos", "6 tipos de nodos definidos con neomodel")

nodes_data = [
    ("👤 Student", ["uid (unique)", "django_user_id", "name", "budget", "universidad", "presupuesto"], TEAL),
    ("📍 Place", ["uid (unique)", "name", "cost", "popularity", "lat, lng"], VERDE_SUAVE),
    ("🏷 Category", ["name (unique)", "", "Ej: cultura, naturaleza,", "fiesta, comida", ""], NARANJA),
    ("🎓 Career", ["name (unique)", "", "Ingeniería, Derecho,", "Medicina...", ""], TEAL),
    ("🏙 City", ["name (unique)", "country", "", "", ""], VERDE_SUAVE),
    ("🔖 Tag", ["name (unique)", "", "trending, barato,", "instagrammable", ""], NARANJA),
]

for i, (nname, props, col) in enumerate(nodes_data):
    row = i // 3
    ci = i % 3
    x = 0.4 + ci * 4.3
    y = 1.3 + row * 2.85
    add_rect(s, x, y, 4.0, 2.6, AZUL_OSCURO)
    add_rect(s, x, y, 4.0, 0.55, col)
    add_text(s, nname, x+0.1, y+0.08, 3.8, 0.42,
             font_size=16, bold=True, color=AZUL_OSCURO)
    for j, prop in enumerate(props[:4]):
        if prop:
            add_text(s, f"  · {prop}", x+0.1, y+0.65 + j*0.47, 3.8, 0.42,
                     font_size=12, color=GRIS_CLARO)
footer(s, 8, TOTAL)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 9 — RELACIONES DEL MODELO
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
content_slide_bg(s)
slide_title(s, "Modelo de Datos · Relaciones (Aristas)", "Las relaciones son el núcleo del sistema de recomendaciones")

rels = [
    ("VISITED", "Student → Place", "rating · comment · timestamp · budget_spent", "Historial real + feedback del usuario", TEAL),
    ("LIKES", "Student → Category", "weight (1–5)", "Preferencias declaradas por el usuario", VERDE_SUAVE),
    ("STUDIES", "Student → Career", "—", "Segmentación demográfica por carrera", NARANJA),
    ("HAS_CATEGORY", "Place → Category", "—", "Clasificación del destino turístico", TEAL),
    ("PREFERS", "Career → Place", "weight", "Afinidad demográfica carrera-destino", VERDE_SUAVE),
    ("NEAR", "Place → Place", "distance_km", "Proximidad geográfica entre destinos", NARANJA),
    ("HAS_TAG", "Place → Tag", "—", "Etiquetas: trending, barato, instagrammable", TEAL),
    ("LOCATED_IN", "Place → City", "—", "Agrupación geográfica por ciudad", VERDE_SUAVE),
]

for i, (rel, path, props, purpose, col) in enumerate(rels):
    row = i // 2
    ci = i % 2
    x = 0.4 + ci * 6.4
    y = 1.25 + row * 1.45
    add_rect(s, x, y, 6.0, 1.3, AZUL_OSCURO)
    add_rect(s, x, y, 0.25, 1.3, col)
    add_text(s, rel, x+0.4, y+0.08, 5.5, 0.38,
             font_size=15, bold=True, color=col)
    add_text(s, path, x+0.4, y+0.48, 5.5, 0.3,
             font_size=12, color=BLANCO)
    add_text(s, f"Props: {props}", x+0.4, y+0.78, 5.5, 0.25,
             font_size=10, color=TEAL, italic=True)
    add_text(s, purpose, x+0.4, y+0.98, 5.5, 0.25,
             font_size=10, color=GRIS_CLARO)
footer(s, 9, TOTAL)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 10 — DIAGRAMA VISUAL DEL GRAFO
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
add_rect(s, 0, 0, 13.33, 7.5, AZUL_OSCURO)
add_rect(s, 0, 0, 13.33, 1.1, TEAL_OSCURO)
add_text(s, "Grafo del Modelo de Datos", 0.4, 0.18, 12.5, 0.72,
         font_size=26, bold=True, color=BLANCO)

# Nodos centrales representados como círculos con rectángulos
def node_box(slide, label, icon, x, y, color):
    add_rect(slide, x, y, 1.8, 0.95, color)
    add_text(slide, f"{icon} {label}", x+0.05, y+0.22, 1.7, 0.5,
             font_size=13, bold=True, color=AZUL_OSCURO, align=PP_ALIGN.CENTER)

node_box(s, "Student", "👤", 0.4, 3.1, TEAL)
node_box(s, "Place", "📍", 5.4, 1.1, VERDE_SUAVE)
node_box(s, "Category", "🏷", 5.4, 3.1, NARANJA)
node_box(s, "Career", "🎓", 5.4, 5.3, TEAL)
node_box(s, "City", "🏙", 9.8, 1.1, VERDE_SUAVE)
node_box(s, "Tag", "🔖", 9.8, 3.1, NARANJA)

# Conexiones (flechas como líneas)
def arrow_label(slide, text, x, y, col=TEAL):
    add_rect(slide, x-0.05, y-0.05, len(text)*0.09+0.2, 0.33, AZUL_OSCURO)
    add_text(slide, text, x, y, len(text)*0.09+0.1, 0.3,
             font_size=9, color=col, italic=True)

# Student → Place (VISITED)
add_rect(s, 2.2, 3.37, 3.2, 0.06, TEAL)
arrow_label(s, "VISITED", 3.1, 3.1, TEAL)

# Student → Category (LIKES)
add_rect(s, 2.2, 3.52, 0.06, 0.15, TEAL)
add_rect(s, 2.2, 3.67, 3.0, 0.06, TEAL)
add_rect(s, 5.2, 3.55, 0.06, 0.5, TEAL)
arrow_label(s, "LIKES", 3.3, 3.55, TEAL)

# Student → Career (STUDIES)
add_rect(s, 2.2, 3.65, 0.06, 2.15, VERDE_SUAVE)
add_rect(s, 2.2, 5.8, 3.2, 0.06, VERDE_SUAVE)
add_rect(s, 5.2, 5.7, 0.06, 0.16, VERDE_SUAVE)
arrow_label(s, "STUDIES", 3.1, 5.5, VERDE_SUAVE)

# Place → Category (HAS_CATEGORY)
add_rect(s, 6.35, 2.05, 0.06, 1.05, NARANJA)
arrow_label(s, "HAS_CATEGORY", 6.5, 2.4, NARANJA)

# Place → City (LOCATED_IN)
add_rect(s, 7.2, 1.52, 2.6, 0.06, VERDE_SUAVE)
arrow_label(s, "LOCATED_IN", 8.0, 1.35, VERDE_SUAVE)

# Place → Tag (HAS_TAG)
add_rect(s, 7.2, 1.6, 0.06, 1.87, NARANJA)
add_rect(s, 7.2, 3.47, 2.6, 0.06, NARANJA)
arrow_label(s, "HAS_TAG", 8.1, 3.3, NARANJA)

# Career → Place (PREFERS)
add_rect(s, 5.4, 5.35, 0.06, -3.75, ROJO_SUAVE)
arrow_label(s, "PREFERS", 4.3, 4.2, ROJO_SUAVE)

# Place ↔ Place (NEAR)
add_rect(s, 5.4, 2.0, 0.8, 0.06, TEAL_OSCURO)
add_rect(s, 6.2, 2.0, 0.06, -0.45, TEAL_OSCURO)
arrow_label(s, "NEAR", 5.5, 1.78, TEAL_OSCURO)

footer(s, 10, TOTAL)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 11 — SEPARADOR SECCIÓN 3 (DSA)
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
section_header(s, "03 · Algoritmos de Recomendación",
               "Content-Based · Collaborative · Demographic · Híbrido · Cold Start")
footer(s, 11, TOTAL)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 12 — OVERVIEW DE LOS ALGORITMOS INVESTIGADOS
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
content_slide_bg(s)
slide_title(s, "Landscape de Algoritmos de Recomendación", "Investigación y selección")

algos = [
    ("Collaborative\nFiltering", "Usuarios similares → ítems similares", "✓ Implementado como Componente B", TEAL, True),
    ("Content-Based\nFiltering", "Atributos del ítem → perfil del usuario", "✓ Implementado como Componente A", VERDE_SUAVE, True),
    ("Sistema\nHíbrido", "Combina múltiples enfoques ponderados", "✓ Arquitectura principal del sistema", NARANJA, True),
    ("Graph\nTraversals", "Explorar rutas del grafo por patrones", "✓ Mecanismo de consulta en Neo4j", TEAL, True),
    ("Node\nSimilarity", "Jaccard entre vecindarios de nodos", "✓ Mide similitud entre estudiantes", VERDE_SUAVE, True),
    ("Community\nDetection", "Agrupar nodos más conectados entre sí", "◐ Solo complementario (no primario)", GRIS_TEXTO, False),
    ("PageRank", "Relevancia global por conexiones", "✗ Produce rankings globales, no personalizados", ROJO_SUAVE, False),
]

for i, (name, desc, status, col, selected) in enumerate(algos):
    row = i // 4
    ci = i % 4
    if i >= 4:
        row = 1
        ci = i - 4
    x = 0.35 + ci * 3.25
    y = 1.25 + row * 2.8
    w, h = 3.0, 2.55
    border_col = col if selected else GRIS_TEXTO
    add_rect(s, x, y, w, h, AZUL_OSCURO)
    add_rect(s, x, y, w, 0.07, border_col)
    add_text(s, name, x+0.1, y+0.12, w-0.2, 0.65,
             font_size=14, bold=True, color=border_col if selected else GRIS_CLARO)
    add_text(s, desc, x+0.1, y+0.85, w-0.2, 0.8,
             font_size=11, color=GRIS_CLARO)
    add_text(s, status, x+0.1, y+1.75, w-0.2, 0.65,
             font_size=10, color=VERDE_SUAVE if selected else GRIS_CLARO,
             italic=True)

footer(s, 12, TOTAL)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 13 — COMPONENTE A: CONTENT-BASED
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
content_slide_bg(s)
slide_title(s, "Componente A · Content-Based Filtering",
            "Peso: 40% (normal) | 50% (cold start)")

add_rect(s, 0.4, 1.2, 12.5, 0.55, TEAL)
add_text(s, "Pregunta: ¿Qué tan bien encajan las categorías del lugar con los gustos declarados del estudiante?",
         0.55, 1.25, 12.2, 0.45, font_size=14, bold=True, color=AZUL_OSCURO)

add_text(s, "Traversal en el grafo:", 0.4, 1.9, 8, 0.35,
         font_size=14, bold=True, color=GRIS_TEXTO)
add_rect(s, 0.4, 2.3, 8.0, 0.65, AZUL_OSCURO)
add_text(s, "(Student) -[LIKES, weight]→ (Category) ←[HAS_CATEGORY]- (Place)",
         0.55, 2.38, 7.7, 0.5, font_size=13, color=TEAL, italic=True)

add_text(s, "Fórmula:", 0.4, 3.15, 8, 0.35, font_size=14, bold=True, color=GRIS_TEXTO)
add_rect(s, 0.4, 3.55, 8.0, 1.05, AZUL_OSCURO)
add_text(s, "direct_matches  = |cats_lugar ∩ cats_liked|  × 1.0", 0.6, 3.62, 7.6, 0.32, font_size=12, color=VERDE_SUAVE)
add_text(s, "visited_matches = |cats_lugar ∩ cats_visited| × 0.5", 0.6, 3.94, 7.6, 0.32, font_size=12, color=TEAL)
add_text(s, "content_score   = (direct + visited) / |cats_lugar|", 0.6, 4.26, 7.6, 0.32, font_size=12, color=NARANJA)

add_rect(s, 8.6, 1.2, 4.3, 5.7, AZUL_OSCURO)
add_text(s, "Ejemplo", 8.75, 1.32, 4.0, 0.4, font_size=15, bold=True, color=TEAL)
add_text(s, "Lugar: Antigua Guatemala\nCategorías: [cultura, historia]",
         8.75, 1.82, 4.0, 0.8, font_size=12, color=BLANCO)
add_text(s, "Estudiante:\n LIKES cultura (w=4)\n LIKES arte   (w=3)\n NO LIKES historia",
         8.75, 2.75, 4.0, 1.3, font_size=12, color=BLANCO)
add_rect(s, 8.75, 4.15, 3.8, 0.06, TEAL)
add_text(s, "direct = 1 × 1.0 = 1.0\nvisited = 0\nscore = 1.0 / 2 = 0.50",
         8.75, 4.3, 4.0, 1.2, font_size=13, bold=True, color=VERDE_SUAVE)

footer(s, 13, TOTAL)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 14 — COMPONENTE B: COLLABORATIVE FILTERING + NODE SIMILARITY
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
content_slide_bg(s)
slide_title(s, "Componente B · Collaborative Filtering",
            "Peso: 35% (normal) | 20% (cold start) — Node Similarity + Traversal")

add_rect(s, 0.4, 1.2, 12.5, 0.55, VERDE_SUAVE)
add_text(s, "Pregunta: ¿Qué lugares visitaron y valoraron estudiantes similares a mí, que yo aún no conozco?",
         0.55, 1.25, 12.2, 0.45, font_size=14, bold=True, color=AZUL_OSCURO)

add_text(s, "Paso 1 — Node Similarity (Jaccard):", 0.4, 1.95, 8, 0.35,
         font_size=14, bold=True, color=GRIS_TEXTO)
add_rect(s, 0.4, 2.35, 8.0, 0.65, AZUL_OSCURO)
add_text(s, "jaccard(A, B) = |visited_A ∩ visited_B| / |visited_A ∪ visited_B|",
         0.55, 2.42, 7.7, 0.5, font_size=13, color=TEAL, italic=True)

add_text(s, "Paso 2 — Traversal ponderado por similitud:", 0.4, 3.12, 8, 0.35,
         font_size=14, bold=True, color=GRIS_TEXTO)
add_rect(s, 0.4, 3.52, 8.0, 0.9, AZUL_OSCURO)
add_text(s, "(Student) -[VISITED]→ (común) ←[VISITED]- (similar) -[VISITED]→ (candidato)",
         0.55, 3.59, 7.7, 0.38, font_size=12, color=VERDE_SUAVE, italic=True)
add_text(s, "collab_score = Σ(jaccard_i × rating_i / 5) / Σ(jaccard_i)",
         0.55, 3.97, 7.7, 0.38, font_size=12, color=NARANJA)

add_text(s, "Similitud en Cypher (Neo4j):", 0.4, 4.6, 8, 0.35,
         font_size=12, bold=True, color=GRIS_TEXTO)
add_rect(s, 0.4, 4.98, 8.0, 1.45, AZUL_OSCURO)
add_text(s,
         "MATCH (s)-[:LIKES]->(cat:Category)<-[:LIKES]-(peer:Student)\n"
         "WHERE s <> peer\n"
         "WITH s, collect(DISTINCT peer) AS similar_peers\n"
         "MATCH (counted:Student)-[:VISITED]->(p)\n"
         "WHERE counted IN similar_peers",
         0.55, 5.05, 7.7, 1.3, font_size=11, color=TEAL, italic=True)

add_rect(s, 8.6, 1.2, 4.3, 5.7, AZUL_OSCURO)
add_text(s, "¿Por qué Jaccard?", 8.75, 1.32, 4.0, 0.4,
         font_size=15, bold=True, color=VERDE_SUAVE)
add_multiline(s, [
    ("Compara conjuntos de lugares", False, 12),
    ("visitados sin importar el orden", False, 12),
    ("", False, 8),
    ("Jaccard = 0  → sin nada en común", False, 12),
    ("Jaccard = 1  → exactamente iguales", False, 12),
    ("", False, 8),
    ("Umbral mínimo: 0.10", True, 13),
    ("Menos de 10% en común =", False, 11),
    ("no se considera 'similar'", False, 11),
    ("", False, 8),
    ("Escalabilidad: en producción", False, 11),
    ("se delega a Neo4j GDS", False, 11),
    ("gds.nodeSimilarity()", True, 12),
], 8.8, 1.82, 3.9, 4.9, font_size=12, color=BLANCO)
footer(s, 14, TOTAL)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 15 — COMPONENTE C: DEMOGRAPHIC + CAREER
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
content_slide_bg(s)
slide_title(s, "Componente C · Demographic Filtering (Carrera)",
            "Peso: 25% — Traversal de 2 saltos")

add_rect(s, 0.4, 1.2, 12.5, 0.55, NARANJA)
add_text(s, "Pregunta: ¿Este destino está recomendado para la carrera universitaria del estudiante?",
         0.55, 1.25, 12.2, 0.45, font_size=14, bold=True, color=AZUL_OSCURO)

add_text(s, "Traversal — 2 saltos:", 0.4, 1.9, 8, 0.35,
         font_size=14, bold=True, color=GRIS_TEXTO)
add_rect(s, 0.4, 2.3, 8.0, 0.65, AZUL_OSCURO)
add_text(s, "(Student) -[STUDIES]→ (Career) -[PREFERS, weight]→ (Place)",
         0.55, 2.38, 7.7, 0.5, font_size=13, color=NARANJA, italic=True)

add_text(s, "Por qué es relevante para DSA:", 0.4, 3.15, 8, 0.35,
         font_size=14, bold=True, color=GRIS_TEXTO)
why = [
    "Es el traversal más corto del sistema (distancia = 2)",
    "Complejidad: O(1) — directo en el grafo si existe la arista",
    "Resuelve el problema de cold start: funciona sin historial",
    "Combina señal demográfica con señal de grafo",
]
for i, w in enumerate(why):
    add_text(s, f"→  {w}", 0.55, 3.65 + i*0.75, 7.7, 0.65,
             font_size=13, color=GRIS_TEXTO)

add_text(s, "Fórmula:", 0.4, 6.1, 3, 0.3,
         font_size=13, bold=True, color=GRIS_TEXTO)
add_rect(s, 0.4, 6.45, 8.0, 0.6, AZUL_OSCURO)
add_text(s, "demographic_score = PreferenceRel.weight / MAX_WEIGHT  ∈ [0.0, 1.0]",
         0.55, 6.52, 7.7, 0.45, font_size=12, color=NARANJA, italic=True)

add_rect(s, 8.6, 1.2, 4.3, 5.7, AZUL_OSCURO)
add_text(s, "Relación PREFERS", 8.75, 1.32, 4.0, 0.4,
         font_size=15, bold=True, color=NARANJA)
add_multiline(s, [
    ("Career → Place con peso", False, 13),
    ("", False, 6),
    ("Ingeniería Civil → Tikal (0.9)", True, 12),
    ("Ingeniería Civil → Pacaya (0.7)", True, 12),
    ("Medicina → Fuentes Georginas (0.8)", True, 12),
    ("Arte → Chichicastenango (0.9)", True, 12),
    ("", False, 6),
    ("Los pesos se pueden ajustar", False, 11),
    ("con el management command:", False, 11),
    ("setup_neo4j --seed", True, 12),
], 8.8, 1.82, 3.9, 4.9, font_size=12, color=BLANCO)
footer(s, 15, TOTAL)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 16 — SISTEMA HÍBRIDO PONDERADO
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
add_rect(s, 0, 0, 13.33, 7.5, AZUL_OSCURO)
add_rect(s, 0, 0, 13.33, 1.1, TEAL_OSCURO)
add_text(s, "Sistema Híbrido · Fórmula Final de Score", 0.4, 0.18, 12.5, 0.72,
         font_size=26, bold=True, color=BLANCO)

# Fórmula visual
add_rect(s, 0.6, 1.25, 12.1, 1.6, TEAL_OSCURO)
add_text(s, "score_final = (0.40 × content) + (0.35 × collaborative) + (0.25 × demographic)",
         0.8, 1.38, 11.7, 0.5, font_size=17, bold=True, color=NARANJA, align=PP_ALIGN.CENTER)
add_text(s, "+ (0.05 × geo_proximity)  +  (0.05 × popularity_norm)  +  serendipity [0, 0.10]",
         0.8, 1.9, 11.7, 0.5, font_size=15, color=TEAL, align=PP_ALIGN.CENTER)

comps = [
    ("Content\n40%", TEAL, "Categorías\nLIKED + VISITED"),
    ("Collaborative\n35%", VERDE_SUAVE, "Jaccard\nNode Similarity"),
    ("Demographic\n25%", NARANJA, "Carrera →\nPREFERS"),
    ("Geo Bonus\n5%", RGBColor(0x8E, 0x44, 0xAD), "Distancia a\nGuat. City"),
    ("Popularity\n5%", ROJO_SUAVE, "Avg rating\nnormalizado"),
]

for i, (label, col, sub) in enumerate(comps):
    x = 0.5 + i * 2.5
    add_rect(s, x, 3.1, 2.2, 1.8, col)
    add_text(s, label, x+0.05, 3.18, 2.1, 0.9,
             font_size=15, bold=True, color=AZUL_OSCURO, align=PP_ALIGN.CENTER)
    add_text(s, sub, x+0.05, 4.1, 2.1, 0.7,
             font_size=11, color=AZUL_OSCURO, align=PP_ALIGN.CENTER)

add_text(s, "El score final se escala a [0, 100] con min(score × 100, 100.0)",
         1.0, 5.15, 11.0, 0.45, font_size=13, color=TEAL, align=PP_ALIGN.CENTER, italic=True)

add_rect(s, 0.6, 5.7, 12.1, 1.25, TEAL_OSCURO)
add_text(s, "Explicabilidad de resultados:", 0.8, 5.78, 3.5, 0.35,
         font_size=13, bold=True, color=NARANJA)
add_text(s, 'Si collaborative > 0.6  → "Muchos estudiantes con tus mismos gustos han visitado este lugar."',
         0.8, 6.12, 11.5, 0.3, font_size=11, color=BLANCO)
add_text(s, 'Si demographic > 0.8    → "Este destino es muy popular entre estudiantes de tu carrera."',
         0.8, 6.42, 11.5, 0.3, font_size=11, color=BLANCO)
footer(s, 16, TOTAL)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 17 — COLD START
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
content_slide_bg(s)
slide_title(s, "Manejo del Cold Start",
            "El sistema se adapta automáticamente a usuarios nuevos")

add_text(s, "Problema: un nuevo usuario sin historial no tiene datos para Collaborative Filtering.",
         0.5, 1.25, 12.3, 0.5, font_size=16, color=GRIS_TEXTO, italic=True)

states = [
    ("Estado 1", "Usuario con historial\n(≥ 3 visitas)",
     "Content: 40%\nCollaborative: 35%\nDemographic: 25%",
     "Sistema completo activado.\nTodos los componentes aportan señal.", VERDE_SUAVE),
    ("Estado 2", "Usuario nuevo\ncon preferencias declaradas",
     "Content: 50%\nCollaborative: 20%\nDemographic: 25%",
     "Se reduce peso colaborativo.\nSe refuerza contenido e intereses.", NARANJA),
    ("Estado 3", "Cold Start total\n(sin visitas ni likes)",
     "Solo Demographic\n+ Popularidad global",
     "Solo carrera y popularidad.\nEl sistema pide onboarding al usuario.", ROJO_SUAVE),
]

for i, (estado, cond, pesos, desc, col) in enumerate(states):
    x = 0.4 + i * 4.3
    add_rect(s, x, 1.9, 4.0, 4.8, AZUL_OSCURO)
    add_rect(s, x, 1.9, 4.0, 0.5, col)
    add_text(s, estado, x+0.1, 1.97, 3.8, 0.38,
             font_size=14, bold=True, color=AZUL_OSCURO)
    add_text(s, cond, x+0.1, 2.55, 3.8, 0.8,
             font_size=13, color=col, bold=True)
    add_rect(s, x+0.1, 3.48, 3.8, 0.06, col)
    add_text(s, pesos, x+0.1, 3.6, 3.8, 1.0,
             font_size=13, color=BLANCO)
    add_text(s, desc, x+0.1, 4.72, 3.8, 1.5,
             font_size=12, color=GRIS_CLARO, italic=True)

add_text(s, "Umbral de cold start: < 3 visitas registradas  (_COLD_START_THRESHOLD = 3)",
         0.5, 6.88, 12.3, 0.4, font_size=12, color=TEAL,
         align=PP_ALIGN.CENTER, italic=True)
footer(s, 17, TOTAL)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 18 — COMPLEJIDAD ALGORÍTMICA
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
content_slide_bg(s)
slide_title(s, "Análisis de Complejidad",
            "DSA: costo computacional de cada componente")

rows_data = [
    ("Componente A (Content)", "Traversal 2 saltos", "O(|C|)  C = categorías del lugar", "Bajo"),
    ("Componente B (Collaborative)", "Jaccard entre pares", "O(|V|²) en Python naive", "Alto sin GDS"),
    ("Componente B (Cypher)", "Shared category peer lookup", "O(|likes_edges|) — nativo en grafo", "Bajo"),
    ("Componente C (Demographic)", "Traversal 2 saltos directo", "O(1) si existe arista PREFERS", "Muy bajo"),
    ("Geo Bonus", "Distancia euclidiana", "O(|visited|) por candidato", "Bajo"),
    ("Filtro de presupuesto", "Condición sobre propiedad", "O(|P|)  P = total de places", "Bajo"),
    ("Pipeline completo", "Todo el scoring", "O(|P| × |V|) sin GDS", "Medio-alto"),
]

add_rect(s, 0.3, 1.2, 12.7, 0.5, AZUL_OSCURO)
for j, h in enumerate(["Componente", "Técnica", "Complejidad", "Costo"]):
    add_text(s, h, 0.4 + j*3.15, 1.28, 3.0, 0.35,
             font_size=13, bold=True, color=TEAL)

for i, row in enumerate(rows_data):
    bg = AZUL_OSCURO if i % 2 == 0 else RGBColor(0x22, 0x46, 0x70)
    add_rect(s, 0.3, 1.75 + i*0.72, 12.7, 0.68, bg)
    colors = [BLANCO, GRIS_CLARO, NARANJA,
              VERDE_SUAVE if "Bajo" in row[3] else ROJO_SUAVE if "Alto" in row[3] else NARANJA]
    for j, cell in enumerate(row):
        add_text(s, cell, 0.4 + j*3.15, 1.82 + i*0.72, 3.0, 0.55,
                 font_size=12, color=colors[j])

add_rect(s, 0.3, 6.72, 12.7, 0.55, TEAL_OSCURO)
add_text(s, "Optimización clave: el Cypher de _fetch_candidates() calcula peers similares en una sola query — "
         "evita el O(|V|²) del naive Python", 0.5, 6.78, 12.3, 0.45,
         font_size=12, color=BLANCO)
footer(s, 18, TOTAL)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 19 — SEPARADOR SECCIÓN 4
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
section_header(s, "04 · Implementación y Resultados",
               "Arquitectura · Código clave · Demo · Lecciones aprendidas")
footer(s, 19, TOTAL)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 20 — ARQUITECTURA DEL SISTEMA
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
content_slide_bg(s)
slide_title(s, "Arquitectura del Sistema", "Capas y responsabilidades")

layers = [
    ("Templates (HTML/CSS)", "UI · 12 vistas: landing, onboarding, recomendaciones,\ndetalle, explorar, favoritos, perfil", TEAL),
    ("Views Layer (Django)", "api/views.py · Routing, sesiones, autenticación,\norquestación de requests", VERDE_SUAVE),
    ("Service Layer", "services/recomendation_service.py · Pipeline híbrido,\nRecommendationScore dataclass, cold start logic", NARANJA),
    ("Scoring Layer", "utils/scoring.py · Fórmulas matemáticas:\ncontent, jaccard, geo, serendipity, demographic", TEAL),
    ("Query Layer (Cypher)", "queries/queries.py · Consultas Neo4j:\nfetch_student_profile, fetch_candidates, add_review", VERDE_SUAVE),
    ("Neo4j + neomodel", "Base de datos de grafos · 6 nodos · 8 tipos de relaciones\n31 destinos de Guatemala", NARANJA),
]

for i, (name, desc, col) in enumerate(layers):
    y = 1.25 + i * 0.98
    add_rect(s, 0.4, y, 1.5, 0.85, col)
    add_text(s, name, 0.45, y+0.18, 1.4, 0.55,
             font_size=9, bold=True, color=AZUL_OSCURO, align=PP_ALIGN.CENTER)
    add_rect(s, 1.9, y, 10.9, 0.85, AZUL_OSCURO)
    add_text(s, desc, 2.05, y+0.1, 10.6, 0.65, font_size=13, color=BLANCO)

footer(s, 20, TOTAL)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 21 — CÓDIGO CLAVE: PIPELINE
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
add_rect(s, 0, 0, 13.33, 7.5, AZUL_OSCURO)
add_rect(s, 0, 0, 13.33, 1.1, TEAL_OSCURO)
add_text(s, "Código Clave · RecommendationService.recommend()", 0.4, 0.18, 12.5, 0.72,
         font_size=22, bold=True, color=BLANCO)

code = [
    "def recommend(self, student_uid, limit=10, budget_factor=1.0):",
    "    profile = self._fetch_student_profile(student_uid)",
    "    if profile is None:",
    "        return self._fallback_popular(limit)      # cold start total",
    "",
    "    cold_start = len(profile['visited_uids']) < 3 # umbral DSA",
    "    candidates  = self._fetch_candidates(student_uid, profile['budget'])",
    "",
    "    scored = [self._score_candidate(profile, c, cold_start)",
    "              for c in candidates]",
    "",
    "    scored.sort(key=lambda r: r.final_score, reverse=True)",
    "    return [self._enrich(r) for r in scored[:limit]]",
]

add_rect(s, 0.4, 1.2, 12.5, 5.8, RGBColor(0x0D, 0x1B, 0x2A))
for i, line in enumerate(code):
    color = TEAL if line.startswith("def ") else (
            VERDE_SUAVE if "#" in line else (
            NARANJA if "cold_start" in line or "fallback" in line else BLANCO))
    add_text(s, line, 0.6, 1.3 + i*0.42, 12.2, 0.38,
             font_size=12, color=color)

footer(s, 21, TOTAL)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 22 — CÓDIGO CLAVE: SCORING
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
add_rect(s, 0, 0, 13.33, 7.5, AZUL_OSCURO)
add_rect(s, 0, 0, 13.33, 1.1, TEAL_OSCURO)
add_text(s, "Código Clave · score_place() — utils/scoring.py", 0.4, 0.18, 12.5, 0.72,
         font_size=22, bold=True, color=BLANCO)

code2 = [
    "WEIGHT_CONTENT       = 0.45   # Coincidencia de categorías",
    "WEIGHT_DEMOGRAPHIC   = 0.30   # Afinidad por carrera",
    "WEIGHT_COLLABORATIVE = 0.15   # Visitas de peers similares",
    "WEIGHT_POPULARITY    = 0.05   # Popularidad normalizada",
    "WEIGHT_GEO           = 0.05   # Cercanía a Guat. City",
    "",
    "final_score = (",
    "    (content_score      * WEIGHT_CONTENT)       +",
    "    (demographic_score  * WEIGHT_DEMOGRAPHIC)   +",
    "    (collaborative_score* WEIGHT_COLLABORATIVE) +",
    "    (popularity_bonus   * WEIGHT_POPULARITY)    +",
    "    (geo_bonus          * WEIGHT_GEO)            +",
    "    random.uniform(0, 0.10)   # serendipity",
    ")",
]

add_rect(s, 0.4, 1.2, 12.5, 5.9, RGBColor(0x0D, 0x1B, 0x2A))
for i, line in enumerate(code2):
    color = TEAL if "WEIGHT_" in line else (
            VERDE_SUAVE if "random" in line else (
            NARANJA if "final_score" in line else BLANCO))
    add_text(s, line, 0.6, 1.3 + i*0.4, 12.2, 0.36,
             font_size=12, color=color)
footer(s, 22, TOTAL)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 23 — DATOS Y SETUP
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
content_slide_bg(s)
slide_title(s, "Datos y Configuración del Sistema",
            "Management commands y datos de Guatemala")

add_rect(s, 0.4, 1.2, 5.8, 5.7, AZUL_OSCURO)
add_text(s, "Management Commands", 0.55, 1.32, 5.5, 0.4,
         font_size=16, bold=True, color=TEAL)
cmds = [
    ("python manage.py migrate", "Configura SQLite para autenticación Django"),
    ("python manage.py setup_neo4j\n  --clear --seed", "Crea nodos de lugares, categorías, carreras\ny relaciones PREFERS con pesos iniciales"),
    ("python manage.py\n  populate_simulated_users", "Genera usuarios sintéticos desde encuesta.csv\npara nutrir el Collaborative Filtering"),
]
for i, (cmd, desc) in enumerate(cmds):
    add_rect(s, 0.55, 1.85 + i*1.7, 5.5, 0.6, RGBColor(0x0D, 0x1B, 0x2A))
    add_text(s, cmd, 0.65, 1.9 + i*1.7, 5.3, 0.52,
             font_size=11, color=VERDE_SUAVE, italic=True)
    add_text(s, desc, 0.55, 2.52 + i*1.7, 5.5, 0.75,
             font_size=12, color=GRIS_CLARO)

add_rect(s, 6.7, 1.2, 6.2, 5.7, AZUL_OSCURO)
add_text(s, "Datos de Guatemala", 6.85, 1.32, 6.0, 0.4,
         font_size=16, bold=True, color=NARANJA)
data_items = [
    "31 destinos turísticos guatemaltecos",
    "Coordenadas reales (lat/lng) de cada lugar",
    "Costo estimado de visita en GTQ",
    "Categorías: cultura, naturaleza, aventura,\n  gastronomía, historia, playa, ecoturismo",
    "Ciudades: Antigua, Petén, Atitlán, Xela...",
    "Imágenes desde Unsplash (CDN)",
    "encuesta.csv: datos reales de preferencias\n  estudiantiles para simulación masiva",
]
for i, item in enumerate(data_items):
    add_text(s, f"·  {item}", 6.85, 1.85 + i*0.7, 5.9, 0.62,
             font_size=12, color=BLANCO)
footer(s, 23, TOTAL)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 24 — FLUJO DE USUARIO
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
content_slide_bg(s)
slide_title(s, "Flujo de Usuario", "De registro a recomendación personalizada")

steps = [
    ("1", "Registro", "Email + contraseña\nDjango auth", TEAL),
    ("2", "Onboarding", "Universidad · Carrera\nCategorías · Presupuesto", VERDE_SUAVE),
    ("3", "Recomendaciones", "Algoritmo híbrido\nTop 10 destinos", NARANJA),
    ("4", "Interacción", "Visitar · Calificar\nGuardar favoritos", TEAL),
    ("5", "Mejora continua", "Nuevas visitas\nmejoran el CF score", VERDE_SUAVE),
]

for i, (num, title, desc, col) in enumerate(steps):
    x = 0.3 + i * 2.55
    add_rect(s, x, 1.3, 2.3, 4.8, AZUL_OSCURO)
    add_rect(s, x, 1.3, 2.3, 0.75, col)
    add_text(s, num, x, 1.35, 2.3, 0.62,
             font_size=34, bold=True, color=AZUL_OSCURO, align=PP_ALIGN.CENTER)
    add_text(s, title, x+0.1, 2.2, 2.1, 0.5,
             font_size=16, bold=True, color=col)
    add_text(s, desc, x+0.1, 2.85, 2.1, 1.5,
             font_size=12, color=BLANCO)

    if i < 4:
        add_text(s, "→", x+2.3, 3.3, 0.25, 0.4,
                 font_size=22, bold=True, color=col, align=PP_ALIGN.CENTER)

add_rect(s, 0.3, 6.3, 12.7, 0.65, TEAL_OSCURO)
add_text(s,
         "Cada calificación y visita actualiza la popularidad del lugar y enriquece el grafo de comportamiento",
         0.5, 6.4, 12.3, 0.45, font_size=13, color=BLANCO, align=PP_ALIGN.CENTER)
footer(s, 24, TOTAL)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 25 — API REST
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
content_slide_bg(s)
slide_title(s, "API REST · Endpoints", "Integración con frontend y debug del algoritmo")

endpoints = [
    ("GET", "/api/recommendations/", "Retorna top N recomendaciones del usuario autenticado.\nRespuesta JSON con score, componentes y razón de match.", VERDE_SUAVE),
    ("POST", "/api/recommendations/review/", "Registra visita con {place_uid, rating, comment}.\nActualiza popularity del lugar en Neo4j.", TEAL),
    ("GET", "/api/recommendations/explain/", "Desglose de score por componente para un destino específico.\nÚtil para debugear y demostrar el algoritmo.", NARANJA),
]

for i, (method, path, desc, col) in enumerate(endpoints):
    y = 1.35 + i * 1.85
    add_rect(s, 0.4, y, 1.1, 0.6, col)
    add_text(s, method, 0.4, y+0.1, 1.1, 0.42,
             font_size=14, bold=True, color=AZUL_OSCURO, align=PP_ALIGN.CENTER)
    add_rect(s, 1.5, y, 11.3, 0.6, AZUL_OSCURO)
    add_text(s, path, 1.65, y+0.1, 11.0, 0.42,
             font_size=14, bold=True, color=col)
    add_rect(s, 0.4, y+0.6, 12.4, 1.05, RGBColor(0x22, 0x3A, 0x52))
    add_text(s, desc, 0.55, y+0.7, 12.1, 0.85, font_size=13, color=BLANCO)

footer(s, 25, TOTAL)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 26 — DESAFÍOS Y LECCIONES
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
content_slide_bg(s)
slide_title(s, "Desafíos y Lecciones Aprendidas", "Los problemas reales que resolvimos")

challenges = [
    ("🔁", "Cold Start",
     "Un usuario nuevo sin historial rompe el Collaborative Filtering.",
     "Umbral de 3 visitas + redistribución de pesos automática.", ROJO_SUAVE),
    ("⚖", "Calibración de pesos",
     "Los pesos iniciales (40/35/25) daban recomendaciones sesgadas.",
     "Iteración con datos reales de encuesta.csv hasta equilibrar.", NARANJA),
    ("🕸", "Complejidad del Cypher",
     "El JOIN de peers similares en Python era O(n²) inaceptable.",
     "Reescribir toda la lógica de peers dentro de una sola query Cypher.", ROJO_SUAVE),
    ("🔖", "Serendipity vs Relevancia",
     "Sin variación aleatoria, las recomendaciones eran monótonas.",
     "Agregar random.uniform(0, 0.10) como factor de exploración.", NARANJA),
]

for i, (icon, title, problem, solution, col) in enumerate(challenges):
    row = i // 2
    ci = i % 2
    x = 0.4 + ci * 6.4
    y = 1.3 + row * 2.7
    add_rect(s, x, y, 6.0, 2.5, AZUL_OSCURO)
    add_rect(s, x, y, 6.0, 0.07, col)
    add_text(s, f"{icon}  {title}", x+0.15, y+0.15, 5.7, 0.42,
             font_size=16, bold=True, color=col)
    add_text(s, f"Problema:  {problem}", x+0.15, y+0.7, 5.7, 0.75,
             font_size=12, color=ROJO_SUAVE)
    add_text(s, f"Solución:    {solution}", x+0.15, y+1.5, 5.7, 0.82,
             font_size=12, color=VERDE_SUAVE)
footer(s, 26, TOTAL)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 27 — CONCLUSIONES
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
add_rect(s, 0, 0, 13.33, 7.5, AZUL_OSCURO)
add_rect(s, 0, 0, 13.33, 1.1, TEAL_OSCURO)
add_text(s, "Conclusiones", 0.4, 0.18, 12.5, 0.72,
         font_size=30, bold=True, color=BLANCO)

conclusions = [
    ("Los grafos son la estructura ideal", "para sistemas de recomendación: las relaciones son ciudadanos de primera clase, no columnas en una tabla.", TEAL),
    ("El algoritmo híbrido superó", "cualquier enfoque individual: resuelve el cold start, reduce el ruido del CF y aprovecha datos demográficos.", VERDE_SUAVE),
    ("La complejidad importa en producción", "reescribir el O(n²) de Python a Cypher fue crítico para que el sistema funcione con datos reales.", NARANJA),
    ("La explicabilidad es un feature", "no un extra: poder decirle al usuario POR QUÉ se recomienda un lugar aumenta la confianza.", TEAL),
]

for i, (title, body, col) in enumerate(conclusions):
    add_rect(s, 0.5, 1.2 + i*1.45, 12.3, 1.3, RGBColor(0x22, 0x46, 0x70))
    add_rect(s, 0.5, 1.2 + i*1.45, 0.18, 1.3, col)
    add_text(s, title, 0.85, 1.28 + i*1.45, 11.7, 0.42,
             font_size=16, bold=True, color=col)
    add_text(s, body, 0.85, 1.72 + i*1.45, 11.7, 0.65,
             font_size=13, color=BLANCO)
footer(s, 27, TOTAL)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 28 — Q&A
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
add_rect(s, 0, 0, 13.33, 7.5, AZUL_OSCURO)
add_rect(s, 0, 0, 13.33, 0.5, TEAL)
add_rect(s, 0, 7.0, 13.33, 0.5, TEAL)

add_text(s, "¿Preguntas?", 1, 2.0, 11.33, 1.4,
         font_size=56, bold=True, color=BLANCO, align=PP_ALIGN.CENTER)
add_rect(s, 3.5, 3.55, 6.33, 0.08, NARANJA)
add_text(s, "Marco Prera  ·  Fabricio Estrada  ·  Mauricio Corado  ·  Sebastián Rodas",
         1, 3.75, 11.33, 0.5, font_size=16, color=TEAL, align=PP_ALIGN.CENTER)
add_text(s, "UTourist · Algoritmos y Estructuras de Datos · UVG 2026",
         1, 4.3, 11.33, 0.5, font_size=14, color=GRIS_CLARO, align=PP_ALIGN.CENTER)

repo_info = [
    "Stack:      Django 6 · Neo4j 5.19 · neomodel 5.3 · Python 3.10+",
    "Algoritmo: Content-Based (40%) + Collaborative (35%) + Demographic (25%)",
    "Datos:      31 destinos guatemaltecos · encuesta.csv de usuarios reales",
]
for i, line in enumerate(repo_info):
    add_text(s, line, 2, 5.1 + i*0.55, 9.33, 0.48,
             font_size=13, color=BLANCO, align=PP_ALIGN.CENTER)

footer(s, 28, TOTAL)

# ─── GUARDAR ─────────────────────────────────────────────────────────────────
output = "/home/user/Tourist-Recomendations/docs/UTourist_Presentacion_DSA.pptx"
prs.save(output)
print(f"Presentación guardada en: {output}")
