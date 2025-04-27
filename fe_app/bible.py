# fe_app/bible.py

from flask import Blueprint, jsonify 
import json 
import os


BIBLE_FILE = 'bible.json'
biblia_data = None

def load_bible_data():
    global biblia_data
    try:
     
        base_dir = os.path.abspath(os.path.dirname(__file__))
        project_root = os.path.abspath(os.path.join(base_dir, '..'))
        bible_path = os.path.join(project_root, BIBLE_FILE)

        with open(bible_path, 'r', encoding='utf-8') as f:
            biblia_data = json.load(f)
        print(f"'{BIBLE_FILE}' cargado exitosamente desde '{bible_path}'.")
    except FileNotFoundError:
        biblia_data = {"error": f"Archivo de la Biblia '{BIBLE_FILE}' no encontrado en '{bible_path}'."}
        print(f"Error: Archivo de la Biblia '{BIBLE_FILE}' no encontrado en '{bible_path}'.")
    except json.JSONDecodeError:
        biblia_data = {"error": f"Error al decodificar el archivo JSON '{BIBLE_FILE}'."}
        print(f"Error: Error al decodificar el archivo JSON '{BIBLE_FILE}'.")

load_bible_data()

bible_bp = Blueprint('bible_bp', __name__)

@bible_bp.route('/libros')
def obtener_libros():
    if biblia_data is None or "error" in biblia_data:
        return jsonify({"error": "Datos de la Biblia no disponibles o con error.", "details": biblia_data.get("error") if biblia_data else "Datos no cargados"})
    libros_vistos = set()
    libros = []
    for verso in biblia_data.get("verses", []):
        nombre_libro = verso.get("book_name")
        if nombre_libro and nombre_libro not in libros_vistos:
            libros_vistos.add(nombre_libro)
            libros.append({"nombre": nombre_libro})
    return jsonify(libros)

@bible_bp.route('/capitulos/<nombre_libro>')
def obtener_capitulos(nombre_libro):
    if biblia_data is None or "error" in biblia_data:
        return jsonify({"error": "Datos de la Biblia no disponibles o con error.", "details": biblia_data.get("error") if biblia_data else "Datos no cargados"})
    capitulos = set()
    for verso in biblia_data.get("verses", []):
        if verso.get("book_name", "").strip() == nombre_libro.strip():
            capitulos.add(verso.get("chapter"))
    return jsonify(sorted(list(capitulos)))

@bible_bp.route('/versiculos/<nombre_libro>/<int:numero_capitulo>')
def obtener_versiculos(nombre_libro, numero_capitulo):
    if biblia_data is None or "error" in biblia_data:
        return jsonify({"error": "Datos de la Biblia no disponibles o con error.", "details": biblia_data.get("error") if biblia_data else "Datos no cargados"})
    versiculos_capitulo = []
    for verso in biblia_data.get("verses", []):
        if verso.get("book_name", "").strip() == nombre_libro.strip() and verso.get("chapter") == numero_capitulo:
            versiculos_capitulo.append({"verse": verso.get("verse"), "text": verso.get("text")})
    return jsonify(versiculos_capitulo)