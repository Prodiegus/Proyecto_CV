import sqlite3
import pickle
import numpy as np

class DatabaseManager:
    def __init__(self, db_path="database/proyecto_cv.db"):
        self.db_path = db_path
    
    def conectar(self):
        try:
            conn = sqlite3.connect(self.db_path)
            return conn
        except sqlite3.Error as e:
            print(f"Error al conectar: {e}")
            return None
    
    def cerrar_conexion(self, conn):
        if conn:
            conn.close()
    
    def agregar_persona(self, nombre, encoding, imagen_referencia=None):
        conn = self.conectar()
        if not conn:
            return None
        
        try:
            # Serializar el encoding
            encoding_blob = pickle.dumps(encoding)
            
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO personas (nombre, encoding, imagen_referencia)
                VALUES (?, ?, ?)
            """, (nombre, encoding_blob, imagen_referencia))
            
            persona_id = cursor.lastrowid
            conn.commit()
            print(f"Persona '{nombre}' agregada con ID: {persona_id}")
            return persona_id
            
        except sqlite3.IntegrityError:
            print(f"Error: Ya existe una persona con el nombre '{nombre}'")
            return None
        except Exception as e:
            print(f"Error al agregar persona: {e}")
            return None
        finally:
            self.cerrar_conexion(conn)

    def obtener_encodings_conocidos(self):
        conn = self.conectar()
        if not conn:
            return [], [], []
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, nombre, encoding
                FROM personas ORDER BY nombre
            """)
            
            resultados = cursor.fetchall()
            
            encodings = []
            nombres = []
            ids = []
            
            for resultado in resultados:
                persona_id, nombre, encoding_blob = resultado
                
                # Deserializar el encoding
                encoding = pickle.loads(encoding_blob)
                
                encodings.append(encoding)
                nombres.append(nombre)
                ids.append(persona_id)
            
            print(f"Se cargaron {len(encodings)} rostros conocidos en memoria")
            return encodings, nombres, ids
            
        except Exception as e:
            print(f"Error al obtener encodings: {e}")
            return [], [], []
        finally:
            self.cerrar_conexion(conn)

if __name__ == "__main__":
    db = DatabaseManager()
    conexion = db.conectar()
    
    if conexion:
        print("CONECTADO")
        db.cerrar_conexion(conexion)
    else:
        print("NO CONECTADO")
