# Utourist — Recommendation System

Sistema de recomendaciones de viajes diseñado para estudiantes universitarios, integrando **Django** y **Neo4j** para ofrecer sugerencias personalizadas basadas en presupuesto, carrera académica e intereses.

---

## Guía de Configuración Local

Segui estos pasos para poner en marcha el proyecto en tu máquina:

### 1. Requisitos Previos
*   **Python 3.10+**
*   **Neo4j** (Recomendado vía Docker)
*   **Git**

### 2. Clonar y Preparar Entorno
```bash
# Clonar repositorio
git clone 
cd Tourist-Recomendations

# Crear entorno virtual
python -m venv venv
source venv/Scripts/activate 

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configurar Neo4j
Si usas Docker:
```bash
docker run -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest
```
*Nota: Si tu contraseña de Neo4j es diferente, actualiza `NEOMODEL_NEO4J_BOLT_URL` en `config/settings.py`.*

### 4. Inicializar Bases de Datos
Es necesario preparar tanto SQLite como Neo4j:
```bash
# Migraciones de Django
python manage.py migrate

# Configurar esquema y datos base en Neo4j
python manage.py setup_neo4j --clear --seed

# POBLACIÓN MASIVA: Generar cientos de usuarios simulados desde encuesta.csv
python manage.py populate_simulated_users
```

### 5. Ejecutar Servidor
```bash
python manage.py runserver
```
Accede a `http://localhost:8000` para ver la aplicación.

---

## Arquitectura del Algoritmo

El sistema utiliza un **Algoritmo Híbrido de Recomendación** con los siguientes pesos:

1.  **Filtrado por Contenido (40%)**: Compara categorías del destino con intereses explícitos y lugares visitados previamente.
2.  **Filtrado Colaborativo (35%)**: Encuentra estudiantes con perfiles similares y recomienda lugares que ellos calificaron altamente.
3.  **Filtrado Demográfico (25%)**: Prioriza destinos populares dentro de la carrera universitaria del estudiante.
4.  **Bonos adicionales**: 
    *   **Proximidad Geográfica**: Premia destinos más cercanos a la Ciudad de Guatemala.
    *   **Popularidad Global**: Normalizada para dar visibilidad a destinos tendencia.

---

## Estructura del Proyecto

*   `recomendations/models.py`: Definición de nodos y relaciones (neomodel).
*   `recomendations/services/`: Lógica central del algoritmo de recomendación.
*   `recomendations/queries/`: Consultas Cypher optimizadas para Neo4j.
*   `recomendations/utils/scoring.py`: Implementación matemática de los scores.
*   `encuesta.csv`: Datos de origen para la simulación masiva.

---

## 👥 Equipo
*   Marco Prera, Fabricio Estrada, Mauricio Corado, Sebastián Rodas.
*   **Curso**: Programación de Microprocesadores, UVG 2026.
