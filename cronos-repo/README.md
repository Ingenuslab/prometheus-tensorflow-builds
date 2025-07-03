# Gestor Inteligente de la Bitácora Cronos

**Cronos Manager** es un sistema inteligente de bitácora diseñado para registrar y gestionar eventos del sistema, conversaciones, memoria de proyectos y tareas de Omni-Compute. Proporciona una visión centralizada de la actividad del sistema y facilita la recuperación de información relevante.

## Características Principales

*   **Registro de Eventos:** Registra comandos ejecutados, directorios y sesiones.
*   **Gestión de Conversaciones:** Almacena interacciones entre el Comandante y Gemini.
*   **Memoria de Proyectos:** Guarda datos clave y notas sobre proyectos específicos.
*   **Gestión de Tareas Omni-Compute:** Registra y actualiza el estado de las tareas de computación compartida.
*   **Análisis de Comportamientos:** Identifica patrones de uso del sistema.
*   **Búsqueda por Similitud:** Permite buscar entradas relacionadas utilizando embeddings simplificados.

## Instalación

Cronos Manager requiere Python 3 y las librerías `sqlite3`, `json`, `numpy`, `os`, `sys`, `datetime` y `rich` (para la interfaz de línea de comandos).

1.  **Clonar el Repositorio:**
    ```bash
    git clone https://github.com/Ingenuslab/cronos-manager.git
    cd cronos-manager
    ```

2.  **Instalar Dependencias:**
    ```bash
    pip install rich
    ```

3.  **Inicializar la Base de Datos:**
    Asegúrese de que el archivo `cronos_schema.sql` esté en el mismo directorio que `cronos_manager.py`. Luego, puede inicializar la base de datos ejecutando:
    ```bash
    sqlite3 cronos.db < cronos_schema.sql
    ```

## Uso

Cronos Manager se utiliza a través de la línea de comandos. Aquí están los comandos principales:

*   **Registrar un Evento (comando ejecutado):**
    ```bash
    python3 cronos_manager.py <tu_comando_a_registrar>
    ```
    Ejemplo:
    ```bash
    python3 cronos_manager.py ls -la
    ```

*   **Revisar Última Actividad:**
    ```bash
    python3 cronos_manager.py --revisar
    ```

*   **Guardar una Conversación:**
    ```bash
    python3 cronos_manager.py --guardar_conversacion "Comandante" "Este es un mensaje de prueba."
    ```
    O de forma interactiva:
    ```bash
    python3 cronos_manager.py --guardar_conversacion
    ```

*   **Guardar Memoria de Proyecto:**
    ```bash
    python3 cronos_manager.py --guardar_memoria "MiProyecto" "clave" "valor"
    ```

*   **Obtener Memoria de Proyecto:**
    ```bash
    python3 cronos_manager.py --obtener_memoria "MiProyecto" "clave"
    ```

*   **Listar Memoria de Proyecto:**
    ```bash
    python3 cronos_manager.py --listar_memoria "MiProyecto"
    ```

*   **Buscar Similitud:**
    ```bash
    python3 cronos_manager.py --buscar_similitud "palabra clave" [top_n]
    ```

*   **Revisar Tareas Omni-Compute:**
    ```bash
    python3 cronos_manager.py --revisar_tareas_omnicompute
    ```

## Contribución

¡Las contribuciones son bienvenidas! Si desea mejorar Cronos Manager, por favor, envíe sus pull requests.
