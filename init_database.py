import sqlite3

# Conectar a la base de datos existente
conn = sqlite3.connect('database/proyecto_cv.db')
cursor = conn.cursor()

# Crear tabla personas
cursor.execute("""
CREATE TABLE IF NOT EXISTS personas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    encoding BLOB NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    imagen_referencia TEXT
)
""")

# Crear tabla eventos_reconocimiento
cursor.execute("""
CREATE TABLE IF NOT EXISTS eventos_reconocimiento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    persona_id INTEGER,
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confianza REAL,
    imagen_captura TEXT,
    FOREIGN KEY (persona_id) REFERENCES personas (id)
)
""")

# Confirmar cambios y cerrar
conn.commit()
conn.close()

print("Tablas creadas correctamente")

"""
import sqlite3

conn = sqlite3.connect('database/proyecto_cv.db')
cursor = conn.cursor()

# Verificar qué tablas existen
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tablas = cursor.fetchall()

print("Tablas en la base de datos:")
for tabla in tablas:
    print(f"  • {tabla[0]}")

# Verificar estructura de tabla personas
print("\nEstructura tabla 'personas':")
cursor.execute("PRAGMA table_info(personas);")
for columna in cursor.fetchall():
    print(f"  • {columna[1]} - {columna[2]}")

# Verificar estructura de tabla eventos_reconocimiento
print("\nEstructura tabla 'eventos_reconocimiento':")
cursor.execute("PRAGMA table_info(eventos_reconocimiento);")
for columna in cursor.fetchall():
    print(f"  • {columna[1]} - {columna[2]}")

conn.close()
"""