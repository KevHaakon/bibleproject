from flask import Flask, jsonify
import json
import os

app = Flask(__name__)

# Configuración
BIBLE_FILE = 'bible.json'

# Imprimir el directorio de trabajo actual para depuración
print(f"Directorio de trabajo actual: {os.getcwd()}")

# Función para cargar los datos de la Biblia desde el archivo JSON
def cargar_biblia():
    try:
        with open(BIBLE_FILE, 'r', encoding='utf-8') as f:
            biblia = json.load(f)
        return biblia
    except FileNotFoundError:
        return {"error": "Archivo de la Biblia no encontrado."}

# Rutas de la API
@app.route('/')
def inicio():
    return "¡Bienvenido a la API de la Biblia!"

@app.route('/libros')
def obtener_libros():
    biblia = cargar_biblia()
    if "error" in biblia:
        return jsonify(biblia)
    libros_vistos = set()
    libros = []
    for verso in biblia.get("verses", []):
        nombre_libro = verso.get("book_name")
        if nombre_libro and nombre_libro not in libros_vistos:
            libros_vistos.add(nombre_libro)
            libros.append({"nombre": nombre_libro})
    return jsonify(libros)

@app.route('/capitulos/<nombre_libro>')
def obtener_capitulos(nombre_libro):
    biblia = cargar_biblia()
    if "error" in biblia:
        return jsonify(biblia)

    capitulos = set()
    for verso in biblia.get("verses", []):
        if verso.get("book_name").strip() == nombre_libro.strip():
            capitulos.add(verso.get("chapter"))

    return jsonify(sorted(list(capitulos)))

@app.route('/versiculos/<nombre_libro>/<int:numero_capitulo>')
def obtener_versiculos(nombre_libro, numero_capitulo):
    biblia = cargar_biblia()
    if "error" in biblia:
        return jsonify(biblia)

    versiculos_capitulo = []
    for verso in biblia.get("verses", []):
        if verso.get("book_name").strip() == nombre_libro.strip() and verso.get("chapter") == numero_capitulo:
            versiculos_capitulo.append({"verse": verso.get("verse"), "text": verso.get("text")})

    return jsonify(versiculos_capitulo)

if __name__ == '__main__':
    app.run(debug=True)