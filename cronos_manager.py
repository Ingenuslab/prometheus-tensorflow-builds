#!/usr/bin/python3
# Gestor Inteligente de la Bitácora Cronos - cronos_manager.py

import sqlite3
import sys
import os
from datetime import datetime
import json
import numpy as np

DB_PATH = "/data/data/com.termux/files/home/cronos.db"

def _generate_simple_embedding(text):
    """Genera un embedding simplificado para un texto dado (frecuencia de caracteres)."""
    # Este es un embedding muy básico, solo para fines de demostración y prueba.
    # En un entorno real, usaríamos modelos de embedding pre-entrenados.
    char_counts = [0] * 256  # Para caracteres ASCII extendidos
    for char in text:
        if ord(char) < 256:
            char_counts[ord(char)] += 1
    return json.dumps(char_counts)

def _check_and_add_embedding_column():
    """Verifica y añade la columna embedding_vector a las tablas si no existe."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    tables = {
        "eventos_sistema": "comando",
        "conversaciones": "texto",
        "memoria_proyectos": "valor",
        "tareas_omnicompute": "description"
    }

    for table, text_column in tables.items():
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in cursor.fetchall()]
        if "embedding_vector" not in columns:
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN embedding_vector TEXT")
                conn.commit()
                # print(f"Columna 'embedding_vector' añadida a la tabla '{table}'.")
            except sqlite3.Error as e:
                # print(f"Error al añadir columna 'embedding_vector' a la tabla '{table}': {e}")
                pass
    conn.close()

_check_and_add_embedding_column()

def registrar_evento(comando):
    """Registra un nuevo comando en la tabla eventos_sistema."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        directorio_actual = os.getcwd()
        sesion_id = os.getenv('TERMUX_SESSION_ID', 'default_session')
        embedding = _generate_simple_embedding(comando)

        cursor.execute(
            "INSERT INTO eventos_sistema (directorio, comando, sesion_id, embedding_vector) VALUES (?, ?, ?, ?)",
            (directorio_actual, comando, sesion_id, embedding)
        )
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        pass

def revisar_ultima_actividad():
    """Muestra los últimos 10 eventos registrados en la bitácora."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT timestamp, directorio, comando FROM eventos_sistema ORDER BY timestamp DESC LIMIT 10"
        )
        
        eventos = cursor.fetchall()
        
        print("--- [ Bitácora Cronos: Última Actividad Registrada (Eventos del Sistema) ] ---")
        if not eventos:
            print("No hay actividad registrada aún.")
        else:
            for evento in reversed(eventos):
                timestamp, directorio, comando = evento
                print(f"[{timestamp}] [{directorio}]> {comando}")
        print("------------------------------------------------------------------------------")

        cursor.execute(
            "SELECT timestamp, autor, texto FROM conversaciones ORDER BY timestamp DESC LIMIT 10"
        )
        conversaciones = cursor.fetchall()

        print("\n--- [ Bitácora Cronos: Últimas Conversaciones ] ---")
        if not conversaciones:
            print("No hay conversaciones registradas aún.")
        else:
            for conv in reversed(conversaciones):
                timestamp, autor, texto = conv
                print(f"[{timestamp}] ({autor}): {texto}")
        print("----------------------------------------------------")

        cursor.execute(
            "SELECT timestamp, proyecto, clave, valor FROM memoria_proyectos ORDER BY timestamp DESC LIMIT 10"
        )
        memoria_proyectos = cursor.fetchall()

        print("\n--- [ Bitácora Cronos: Última Memoria de Proyectos ] ---")
        if not memoria_proyectos:
            print("No hay memoria de proyectos registrada aún.")
        else:
            for mem in reversed(memoria_proyectos):
                timestamp, proyecto, clave, valor = mem
                print(f"[{timestamp}] [Proyecto: {proyecto}] [Clave: {clave}]: {valor}")
        print("--------------------------------------------------------")

        conn.close()

    except sqlite3.Error as e:
        print(f"Error al consultar la Bitácora Cronos: {e}")

def guardar_conversacion(autor, texto):
    """Guarda una conversación en la bitácora de forma automática."""
    try:
        if autor not in ['Comandante', 'Gemini'] or not texto:
            # print("Autor o texto inválido. Abortando.") # Desactivado para evitar spam en la salida
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        sesion_id = os.getenv('TERMUX_SESSION_ID', 'default_session')
        embedding = _generate_simple_embedding(texto)

        cursor.execute(
            "INSERT INTO conversaciones (sesion_id, autor, texto, embedding_vector) VALUES (?, ?, ?, ?)",
            (sesion_id, autor, texto, embedding)
        )
        conn.commit()
        conn.close()
        # print("Conversación guardada en la Bitácora Cronos.") # Desactivado para evitar spam en la salida

    except sqlite3.Error as e:
        # print(f"Error al guardar la conversación: {e}") # Desactivado para evitar spam en la salida
        pass

def guardar_conversacion_cli():
    """Función para guardar conversación desde la línea de comandos (interactiva)."""
    print("Introduce el texto de la conversación a guardar.")
    print("Autor (Comandante/Gemini): ", end="")
    autor = sys.stdin.readline().strip()
    print("Texto: ", end="")
    texto = sys.stdin.readline().strip()
    guardar_conversacion(autor, texto)

def analizar_comportamientos_sistema():
    """Analiza los eventos del sistema para identificar patrones y guarda insights en memoria_proyectos."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Comandos más frecuentes
        cursor.execute("SELECT comando, COUNT(*) as count FROM eventos_sistema GROUP BY comando ORDER BY count DESC LIMIT 5")
        comandos_frecuentes = cursor.fetchall()
        if comandos_frecuentes:
            insight_comandos = "Comandos más frecuentes: " + ", ".join([f"'{cmd}' ({count})" for cmd, count in comandos_frecuentes])
            guardar_memoria_proyecto("sistema_comportamiento", "comandos_frecuentes", insight_comandos)

        # Directorios más utilizados
        cursor.execute("SELECT directorio, COUNT(*) as count FROM eventos_sistema GROUP BY directorio ORDER BY count DESC LIMIT 5")
        directorios_frecuentes = cursor.fetchall()
        if directorios_frecuentes:
            insight_directorios = "Directorios más utilizados: " + ", ".join([f"'{dir}' ({count})" for dir, count in directorios_frecuentes])
            guardar_memoria_proyecto("sistema_comportamiento", "directorios_frecuentes", insight_directorios)

        conn.close()
        print("Análisis de comportamientos del sistema completado y guardado en memoria_proyectos.")

    except sqlite3.Error as e:
        print(f"Error al analizar comportamientos del sistema: {e}")
    except Exception as e:
        print(f"Error inesperado durante el análisis de comportamientos: {e}")

def generar_y_guardar_resumen(entry_type, entry_id):
    """Genera un resumen básico de una entrada (evento o conversación) y lo guarda en memoria_proyectos."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        text_to_summarize = ""
        project_name = f"resumen_{entry_type}_{entry_id}"

        if entry_type == "evento":
            cursor.execute("SELECT comando FROM eventos_sistema WHERE id = ?", (entry_id,))
            result = cursor.fetchone()
            if result:
                text_to_summarize = result[0]
        elif entry_type == "conversacion":
            cursor.execute("SELECT texto FROM conversaciones WHERE id = ?", (entry_id,))
            result = cursor.fetchone()
            if result:
                text_to_summarize = result[0]
        else:
            print("Tipo de entrada no válido. Use 'evento' o 'conversacion'.")
            return

        if text_to_summarize:
            # Resumen muy básico: primeros 50 caracteres
            summary = text_to_summarize[:50] + "..." if len(text_to_summarize) > 50 else text_to_summarize
            guardar_memoria_proyecto(project_name, "resumen", summary)
            print(f"Resumen generado y guardado para {entry_type} ID {entry_id}.")
        else:
            print(f"No se encontró texto para {entry_type} ID {entry_id}.")

        conn.close()

    except sqlite3.Error as e:
        print(f"Error al generar o guardar resumen: {e}")
    except Exception as e:
        print(f"Error inesperado durante la generación de resumen: {e}")

def guardar_memoria_proyecto(proyecto, clave, valor):
    """Guarda o actualiza una entrada en la tabla memoria_proyectos."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        embedding = _generate_simple_embedding(valor)
        cursor.execute(
            "INSERT OR REPLACE INTO memoria_proyectos (proyecto, clave, valor, embedding_vector) VALUES (?, ?, ?, ?)",
            (proyecto, clave, valor, embedding)
        )
        conn.commit()
        conn.close()
        print(f"Memoria de proyecto '{proyecto}' - '{clave}' guardada/actualizada.")
    except sqlite3.Error as e:
        print(f"Error al guardar memoria de proyecto: {e}")

def registrar_tarea_omnicompute(task_id, description, platform, status="PENDING"):
    """Registra una nueva tarea de Omni-Compute en la tabla tareas_omnicompute."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        embedding = _generate_simple_embedding(description)
        cursor.execute(
            "INSERT INTO tareas_omnicompute (task_id, description, platform, status, start_time, embedding_vector) VALUES (?, ?, ?, ?, ?, ?)",
            (task_id, description, platform, status, datetime.now().isoformat(), embedding)
        )
        conn.commit()
        conn.close()
        print(f"Tarea Omni-Compute '{task_id}' registrada con estado '{status}'.")
        return True
    except sqlite3.Error as e:
        print(f"Error al registrar tarea Omni-Compute: {e}")
        return False

def actualizar_estado_tarea_omnicompute(task_id, status, output_log=None, error_log=None):
    """Actualiza el estado y los logs de una tarea de Omni-Compute."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        update_query = "UPDATE tareas_omnicompute SET status = ?, end_time = ?"
        params = [status, datetime.now().isoformat()]
        if output_log:
            update_query += ", output_log = ?"
            params.append(output_log)
        if error_log:
            update_query += ", error_log = ?"
            params.append(error_log)
        update_query += " WHERE task_id = ?"
        params.append(task_id)

        cursor.execute(update_query, params)
        conn.commit()
        conn.close()
        print(f"Estado de tarea Omni-Compute '{task_id}' actualizado a '{status}'.")
        return True
    except sqlite3.Error as e:
        print(f"Error al actualizar estado de tarea Omni-Compute: {e}")
        return False

def obtener_memoria_proyecto(proyecto, clave):
    """Obtiene el valor de una clave específica de la memoria de proyectos."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT valor FROM memoria_proyectos WHERE proyecto = ? AND clave = ?",
            (proyecto, clave)
        )
        resultado = cursor.fetchone()
        conn.close()
        if resultado:
            return resultado[0]
        return None
    except sqlite3.Error as e:
        print(f"Error al obtener memoria de proyecto: {e}")
        return None

def listar_memoria_proyecto(proyecto):
    """Lista todas las claves y valores para un proyecto específico en la memoria de proyectos."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT clave, valor FROM memoria_proyectos WHERE proyecto = ?",
            (proyecto,)
        )
        resultados = cursor.fetchall()
        conn.close()
        return resultados
    except sqlite3.Error as e:
        print(f"Error al listar memoria de proyecto: {e}")
        return []

def eliminar_memoria_proyecto(proyecto, clave):
    """Elimina una entrada específica de la memoria de proyectos."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM memoria_proyectos WHERE proyecto = ? AND clave = ?",
            (proyecto, clave)
        )
        conn.commit()
        conn.close()
        print(f"Memoria de proyecto '{proyecto}' - '{clave}' eliminada.")
    except sqlite3.Error as e:
        print(f"Error al eliminar memoria de proyecto: {e}")

def buscar_similitud(query_text, top_n=5):
    """Busca entradas similares en eventos_sistema y conversaciones usando embeddings simplificados."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        query_embedding = np.array(json.loads(_generate_simple_embedding(query_text)))

        results = []

        # Buscar en eventos_sistema
        cursor.execute("SELECT comando, embedding_vector FROM eventos_sistema WHERE embedding_vector IS NOT NULL")
        for comando, emb_str in cursor.fetchall():
            stored_embedding = np.array(json.loads(emb_str))
            similarity = np.dot(query_embedding, stored_embedding) / (np.linalg.norm(query_embedding) * np.linalg.norm(stored_embedding))
            results.append(("Evento", comando, similarity))

        # Buscar en conversaciones
        cursor.execute("SELECT texto, embedding_vector FROM conversaciones WHERE embedding_vector IS NOT NULL")
        for texto, emb_str in cursor.fetchall():
            stored_embedding = np.array(json.loads(emb_str))
            similarity = np.dot(query_embedding, stored_embedding) / (np.linalg.norm(query_embedding) * np.linalg.norm(stored_embedding))
            results.append(("Conversación", texto, similarity))

        # Buscar en memoria_proyectos
        cursor.execute("SELECT proyecto, clave, valor, embedding_vector FROM memoria_proyectos WHERE embedding_vector IS NOT NULL")
        for proyecto, clave, valor, emb_str in cursor.fetchall():
            stored_embedding = np.array(json.loads(emb_str))
            similarity = np.dot(query_embedding, stored_embedding) / (np.linalg.norm(query_embedding) * np.linalg.norm(stored_embedding))
            results.append(("Memoria de Proyecto", f"[Proyecto: {proyecto}] [Clave: {clave}]: {valor}", similarity))

        conn.close()

        results.sort(key=lambda x: x[2], reverse=True)

        print(f"\n--- [ Resultados de Búsqueda de Similitud para: '{query_text}' ] ---")
        if not results:
            print("No se encontraron resultados similares.")
        else:
            for i, (tipo, texto, sim) in enumerate(results[:top_n]):
                print(f"{i+1}. Tipo: {tipo}, Similitud: {sim:.4f}\n   Texto: {texto}\n")
        print("------------------------------------------------------------------")

    except sqlite3.Error as e:
        print(f"Error al realizar la búsqueda de similitud: {e}")
    except Exception as e:
        print(f"Error inesperado durante la búsqueda de similitud: {e}")

def revisar_tareas_omnicompute():
    """Muestra las últimas 10 tareas de Omni-Compute registradas."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT timestamp, task_id, description, platform, status, start_time, end_time, output_log, error_log FROM tareas_omnicompute ORDER BY timestamp DESC LIMIT 10"
        )
        
        tareas = cursor.fetchall()
        
        print("\n--- [ Bitácora Cronos: Últimas Tareas de Omni-Compute ] ---")
        if not tareas:
            print("No hay tareas de Omni-Compute registradas aún.")
        else:
            for tarea in reversed(tareas):
                timestamp, task_id, description, platform, status, start_time, end_time, output_log, error_log = tarea
                print(f"[{timestamp}] [ID: {task_id}] [Plataforma: {platform}] [Estado: {status}]\n  Descripción: {description}\n  Inicio: {start_time}, Fin: {end_time if end_time else 'N/A'}")
                if output_log:
                    print(f"  Output Log:\n{output_log}")
                if error_log:
                    print(f"  Error Log:\n{error_log}")
        print("------------------------------------------------------------")

        conn.close()

    except sqlite3.Error as e:
        print(f"Error al consultar tareas de Omni-Compute: {e}")

if __name__ == "__main__":

    if len(sys.argv) > 1:
        if sys.argv[1] == '--revisar':
            revisar_ultima_actividad()
        elif sys.argv[1] == '--guardar_conversacion':
            if len(sys.argv) == 4:
                guardar_conversacion(sys.argv[2], sys.argv[3])
            else:
                guardar_conversacion_cli()
        elif sys.argv[1] == '--guardar_memoria':
            if len(sys.argv) == 5:
                guardar_memoria_proyecto(sys.argv[2], sys.argv[3], sys.argv[4])
            else:
                print("Uso: --guardar_memoria <proyecto> <clave> <valor>")
        elif sys.argv[1] == '--obtener_memoria':
            if len(sys.argv) == 4:
                valor = obtener_memoria_proyecto(sys.argv[2], sys.argv[3])
                if valor is not None:
                    print(f"Valor para '{sys.argv[2]}' - '{sys.argv[3]}': {valor}")
                else:
                    print(f"No se encontró la clave '{sys.argv[3]}' en el proyecto '{sys.argv[2]}'.")
            else:
                print("Uso: --obtener_memoria <proyecto> <clave>")
        elif sys.argv[1] == '--listar_memoria':
            if len(sys.argv) == 3:
                resultados = listar_memoria_proyecto(sys.argv[2])
                if resultados:
                    print(f"--- Memoria para el proyecto '{sys.argv[2]}' ---")
                    for clave, valor in resultados:
                        print(f"  {clave}: {valor}")
                else:
                    print(f"No hay entradas para el proyecto '{sys.argv[2]}'.")
            else:
                print("Uso: --listar_memoria <proyecto>")
        elif sys.argv[1] == '--eliminar_memoria':
            if len(sys.argv) == 4:
                eliminar_memoria_proyecto(sys.argv[2], sys.argv[3])
            else:
                print("Uso: --eliminar_memoria <proyecto> <clave>")
        elif sys.argv[1] == '--buscar_similitud':
            if len(sys.argv) >= 3:
                query_text = sys.argv[2]
                top_n = 5
                if len(sys.argv) == 4:
                    try:
                        top_n = int(sys.argv[3])
                    except ValueError:
                        print("Error: top_n debe ser un número entero.")
                        sys.exit(1)
                buscar_similitud(query_text, top_n)
            else:
                print("Uso: --buscar_similitud <texto_consulta> [top_n]")
        elif sys.argv[1] == '--analizar_comportamientos':
            analizar_comportamientos_sistema()
        elif sys.argv[1] == '--generar_resumen':
            if len(sys.argv) == 4:
                entry_type = sys.argv[2]
                entry_id = int(sys.argv[3])
                generar_y_guardar_resumen(entry_type, entry_id)
            else:
                print("Uso: --generar_resumen <tipo_entrada> <id_entrada>")
                print("  <tipo_entrada>: 'evento' o 'conversacion'")
        elif sys.argv[1] == '--revisar_tareas_omnicompute':
            revisar_tareas_omnicompute()
        else:
            comando_completo = ' '.join(sys.argv[1:])
            registrar_evento(comando_completo)
