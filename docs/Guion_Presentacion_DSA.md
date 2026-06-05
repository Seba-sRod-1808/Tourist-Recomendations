# Guion — UTourist · Presentación Final DSA
**Duración:** 45 minutos | **4 presentadores** | **UVG 2026**

> Distribución sugerida de presentadores:
> - **Marco** → Secciones 1 y 2 (Contexto + Grafos)
> - **Fabricio** → Sección 3A (Content-Based + Collaborative)
> - **Mauricio** → Sección 3B (Hybrid + Cold Start + Complejidad)
> - **Sebastián** → Sección 4 (Implementación + Demo + Conclusiones)

---

## SLIDE 1 — PORTADA (1 min) · Marco

> *Pararse al frente, esperar silencio, comenzar con seguridad.*

"Buenos días. Somos el equipo de UTourist. A lo largo de este semestre trabajamos en un problema que todos conocemos: **¿a dónde ir de viaje con un presupuesto de estudiante universitario?**

Hoy les vamos a presentar cómo resolvemos ese problema usando **grafos**, **Neo4j** y un **algoritmo híbrido de recomendaciones** que fue el eje central de nuestro trabajo en Algoritmos y Estructuras de Datos.

Vamos a ser concretos: les vamos a mostrar el código, la matemática detrás del algoritmo y cómo todo conecta."

---

## SLIDE 2 — AGENDA (1 min) · Marco

"La presentación tiene cuatro bloques. Empezamos con el contexto del problema, luego entramos a la base de datos en grafo, después el núcleo técnico — los algoritmos — y cerramos con implementación y demo.

Son 45 minutos. Tenemos tiempo para preguntas al final."

---

## SLIDE 3 — EL PROBLEMA (2 min) · Marco

"El problema que identificamos es específico: un estudiante universitario guatemalteco quiere viajar, pero tiene restricciones reales.

**Primero, presupuesto.** No es lo mismo un fin de semana para un estudiante de primer año que para uno de quinto. El presupuesto varía mucho.

**Segundo, Guatemala tiene más de 300 destinos turísticos documentados.** Desde Tikal hasta el Paredon. La información está dispersa.

**Tercero, las recomendaciones existentes son genéricas.** TripAdvisor te recomienda lo mismo a vos que a un turista europeo de 50 años. No considera que sos estudiante de Ingeniería Civil, que tenés Q300 disponibles este fin de semana, y que ya visitaste Antigua.

**Cuarto, no existe ninguna plataforma orientada al perfil universitario guatemalteco.**

Eso es exactamente lo que UTourist resuelve."

---

## SLIDE 4 — LA SOLUCIÓN (2 min) · Marco

"UTourist es un sistema de recomendaciones turísticas con cuatro pilares.

**Personalizado:** no recomendamos lo mismo a todos. Consideramos carrera, presupuesto e intereses.

**Basado en grafos:** Neo4j nos permite modelar las relaciones entre usuarios y destinos de forma nativa. Más adelante explico por qué esto importa.

**Algoritmo híbrido:** combinamos tres enfoques distintos. No usamos solo uno porque cada uno tiene debilidades que los otros compensan.

**Datos reales:** 31 destinos guatemaltecos con coordenadas, costos y categorías reales."

---

## SLIDE 5 — STACK TECNOLÓGICO (2 min) · Marco

"El stack técnico es limpio y justificado.

Django nos da el framework web, autenticación y sesiones. Es la capa que el usuario ve.

Neo4j es la base de datos de grafos. La razón específica de elegir Neo4j sobre PostgreSQL o MySQL la vemos en la siguiente slide.

neomodel es el OGM — Object Graph Mapper — recomendado oficialmente por Neo4j. Sustituye a py2neo que ya está en end-of-life. Nos permite definir nodos como clases Python con propiedades tipadas.

django-neomodel es el puente entre el ciclo de vida de Django y neomodel.

La versión de neomodel que usamos es la 5.3, compatible con Neo4j 5.19."

---

## SLIDE 6 — SEPARADOR SECCIÓN 2 (15 seg) · Fabricio

> *Fabricio toma el frente.*

"Entramos a la parte de estructura de datos. Primero la pregunta fundamental."

---

## SLIDE 7 — ¿POR QUÉ GRAFOS? (3 min) · Fabricio

"Esta es la pregunta que más nos hicieron durante el semestre: ¿por qué Neo4j y no simplemente PostgreSQL con varios JOINs?

La respuesta es de complejidad algorítmica.

**En SQL,** para encontrar 'qué lugares visitaron personas con gustos similares a mí', necesitás hacer un JOIN de usuarios con visitas, cruzarlo con otro JOIN de categorías, filtrar por similitud... típicamente 5 o más tablas. La complejidad para encontrar usuarios similares es **O(n²)** — cuadrática sobre el número de usuarios.

**En Neo4j,** esa misma consulta es un patrón de 4 nodos: usuario, lugar en común, usuario similar, lugar candidato. La complejidad es **O(k)** donde k es el grado del nodo — el número de conexiones directas. El grafo ya almacena las relaciones como estructura de primer nivel.

Además, en grafos podemos poner **propiedades en las aristas**. La relación VISITED tiene rating, timestamp y budget_spent. En SQL eso requeriría una tabla intermedia adicional.

Para sistemas de recomendación, los grafos no son solo una opción — son la herramienta correcta para el problema."

---

## SLIDE 8 — NODOS DEL MODELO (2 min) · Fabricio

"Nuestro modelo tiene 6 tipos de nodos.

**Student** es el usuario central. Tiene su ID de Django, nombre y presupuesto. Importante: `django_user_id` es el puente entre el sistema de autenticación de Django y el nodo en Neo4j.

**Place** es un destino turístico. Tiene coordenadas reales para el cálculo geográfico, costo y popularidad que se actualiza con las calificaciones.

**Category** agrupa destinos: cultura, naturaleza, aventura, gastronomía...

**Career** es la carrera universitaria del estudiante. Este nodo es clave para el filtrado demográfico.

**City** agrupa destinos por ciudad geográfica.

**Tag** son etiquetas dinámicas: trending, barato, instagrammable. Su potencial es que se pueden actualizar programáticamente.

Los nodos se definen con neomodel como clases Python, similar a los modelos de Django."

---

## SLIDE 9 — RELACIONES DEL MODELO (3 min) · Fabricio

"Las relaciones son el núcleo del sistema. En un grafo relacional, las aristas son tan importantes como los nodos.

**VISITED** conecta Student con Place. Tiene tres propiedades críticas: rating — de 1 a 5 — comment y budget_spent. Este último nos permite refinar las recomendaciones por presupuesto real, no solo declarado.

**LIKES** conecta Student con Category con un peso de 1 a 5. Es la preferencia declarada durante el onboarding.

**STUDIES** conecta Student con Career. Sin propiedades, pero activa el filtrado demográfico.

**HAS_CATEGORY** clasifica un Place en categorías.

**PREFERS** — esta es la relación más interesante para el algoritmo. Conecta Career directamente con Place con un peso. Significa 'esta carrera tiene afinidad con este destino'. Los estudiantes de Medicina tienden a ir a Fuentes Georginas; los de Ingeniería Civil, a sitios de construcción histórica.

**NEAR** conecta Place con Place con la distancia en kilómetros. Solo creamos esta arista si la distancia es menor al umbral configurado.

Estas ocho relaciones son las que hacen posibles los tres componentes del algoritmo."

---

## SLIDE 10 — DIAGRAMA DEL GRAFO (1 min) · Fabricio

"Este es el grafo completo de forma visual. Pueden ver cómo Student está en el centro conectando hacia Place, Category y Career.

Place conecta hacia Category, Tag y City, y tiene auto-relaciones NEAR.

Career tiene la relación PREFERS directa hacia Place — ese es el shortcut demográfico.

La densidad de relaciones alrededor de Student y Place es lo que hace que el algoritmo tenga múltiples señales para trabajar."

---

## SLIDE 11 — SEPARADOR SECCIÓN 3 (15 seg) · Fabricio

"Ahora entramos al núcleo técnico: los algoritmos."

---

## SLIDE 12 — LANDSCAPE DE ALGORITMOS (2 min) · Fabricio

"Durante el semestre investigamos siete tipos de algoritmos de recomendación.

Los marcados en verde son los que implementamos. Los dos marcados en rojo — **PageRank** y **Community Detection** — los descartamos como componentes primarios y quiero explicar por qué.

**PageRank** es brillante para ranking global de páginas web, pero produce relevancia global del grafo completo. Para recomendaciones personalizadas no sirve: le daría el mismo rank a un destino sin importar si encaja con vos o no.

**Community Detection** agrupa nodos muy conectados. El problema es que asume que si pertenecés a una comunidad, compartís todos sus gustos. Eso es demasiado grueso para recomendaciones individuales.

Los cinco que implementamos se complementan entre sí: Traversals para las consultas, Node Similarity para medir similitud entre usuarios, y los tres enfoques clásicos para los componentes del score."

---

## SLIDE 13 — COMPONENTE A: CONTENT-BASED (3 min) · Fabricio

"El primer componente responde una pregunta simple: ¿cuánto encajan las categorías de este destino con los gustos que el usuario declaró?

El traversal en el grafo es de dos saltos: Student — LIKES — Category — HAS_CATEGORY — Place.

La fórmula diferencia entre coincidencias directas — categorías que el usuario explícitamente declaró que le gustan — y coincidencias visitadas — categorías de lugares que ya visitó antes. Las directas valen 1.0 y las visitadas valen 0.5 porque son señal implícita, no explícita.

Normalizamos por el número de categorías del lugar para que un lugar con muchas categorías no tenga ventaja injusta.

En el ejemplo: Antigua tiene categorías cultura e historia. El estudiante declaró que le gusta cultura con peso 4. Hay una coincidencia directa. El score es 1 dividido 2 categorías = 0.50. Si el estudiante también hubiera visitado un lugar histórico antes, sumaría 0.25 adicional.

Este componente tiene peso 40% en el score final y se incrementa a 50% en cold start."

---

## SLIDE 14 — COMPONENTE B: COLLABORATIVE FILTERING (3 min) · Fabricio

"El segundo componente es el más sofisticado algorítmicamente. Responde: ¿qué lugares visitaron y valoraron bien estudiantes similares a mí, que yo aún no conozco?

Se divide en dos pasos.

**Paso 1 — Node Similarity con Jaccard.** Para medir qué tan similares son dos estudiantes, calculamos el coeficiente de Jaccard entre sus conjuntos de lugares visitados. Jaccard es intersección sobre unión. Si dos estudiantes visitaron exactamente los mismos lugares, Jaccard = 1. Si no tienen nada en común, Jaccard = 0. Solo consideramos estudiantes con Jaccard mayor a 0.10 como 'similares'.

**Paso 2 — Traversal ponderado.** Para cada estudiante similar, miramos qué lugares visitaron que yo no he visitado. El score colaborativo es la suma de — Jaccard multiplicado por el rating que dieron — dividido la suma de Jaccards. Es un promedio ponderado por similitud.

La implementación naive de esto en Python es O(n²) — para cada usuario comparar con todos los demás. **Esto fue uno de nuestros desafíos principales.** La solución fue reescribir la búsqueda de peers dentro de un solo Cypher query usando la estructura del grafo, lo que lo convierte en O(grado del nodo).

Este componente pesa 35% en modo normal y baja a 20% en cold start porque sin historial no hay Jaccard que calcular."

---

## SLIDE 15 — COMPONENTE C: DEMOGRAPHIC (2 min) · Mauricio

> *Mauricio toma el frente.*

"El tercer componente es el más directo en términos de traversal de grafo: **dos saltos, Student → Career → Place**.

Responde: ¿este destino tiene afinidad con la carrera del estudiante?

La relación Career PREFERS Place tiene un peso. Ese peso se carga durante el setup del sistema con el management command `setup_neo4j --seed`.

¿Por qué es valioso en términos de DSA? Porque es **O(1)** si existe la arista PREFERS. El grafo ya almacena esa información; no hay que calcularla en tiempo de query.

Y lo más importante para el sistema: **funciona sin ningún historial del usuario**. Un estudiante nuevo con solo su carrera registrada ya recibe recomendaciones relevantes. Esto resuelve el cold start total.

El peso demográfico es 25% del score final, tanto en modo normal como en cold start."

---

## SLIDE 16 — SISTEMA HÍBRIDO · FÓRMULA FINAL (3 min) · Mauricio

"Ahora conectamos los tres componentes.

La fórmula final es una combinación lineal ponderada:

**score = 0.40 × content + 0.35 × collaborative + 0.25 × demographic + 0.05 × geo + 0.05 × popularidad**

¿Por qué estos pesos específicos? Los calibramos iterativamente con datos reales de encuesta.csv. Content tiene el mayor peso porque es la señal más directa y confiable — el usuario declaró explícitamente qué le gusta. Collaborative tiene el segundo mayor peso cuando hay historial porque la sabiduría colectiva de usuarios similares es muy poderosa.

El geo bonus premia destinos cercanos a la Ciudad de Guatemala usando distancia euclidiana sobre coordenadas. La popularidad es un desempate entre destinos con score similar.

Y hay un factor que no estaba en el plan original: **serendipity**. Le agregamos `random.uniform(0, 0.10)` al score. Sin esto, las recomendaciones se volvían monótonas — siempre los mismos tres destinos para el mismo perfil. El factor de aleatoriedad del 10% introduce variedad sin dañar significativamente la relevancia.

El score final se escala a [0, 100] con `min(score × 100, 100.0)`.

El sistema también genera una explicación en texto: si el componente colaborativo supera 0.6, dice 'muchos estudiantes con tus mismos gustos visitaron este lugar'. Esto hace el sistema explicable y aumenta la confianza del usuario."

---

## SLIDE 17 — COLD START (2 min) · Mauricio

"El cold start es el problema clásico de cualquier sistema de recomendación: ¿qué recomendás cuando no sabés nada del usuario?

Tenemos tres estados.

**Estado 1 — usuario con historial:** más de 3 visitas registradas. Sistema completo con pesos normales.

**Estado 2 — usuario nuevo con preferencias:** declaró categorías en el onboarding pero aún no visitó lugares. Reducimos el peso colaborativo de 35% a 20% porque hay poco Jaccard disponible, y subimos content de 40% a 50%.

**Estado 3 — cold start total:** sin visitas ni likes. Solo usamos carrera y popularidad global. El sistema le pide al usuario que complete el onboarding.

El umbral de 3 visitas es la constante `_COLD_START_THRESHOLD = 3` en el código. Es configurable.

Esta lógica está en el método `recommend()` de RecommendationService y se activa automáticamente."

---

## SLIDE 18 — COMPLEJIDAD ALGORÍTMICA (3 min) · Mauricio

"Esta tabla es importante para la clase de DSA. Vamos componente por componente.

**Content-Based:** O(|C|) donde C es el número de categorías del lugar. Típicamente 3-7 categorías. Trivialmente rápido.

**Collaborative naive en Python:** O(|V|²) — cuadrático en el número de usuarios. Inaceptable con cientos de usuarios.

**Collaborative en Cypher:** O(|aristas de LIKES|). Neo4j ya tiene las conexiones almacenadas. La búsqueda de peers similares es lineal sobre los vecinos del nodo, no sobre todos los usuarios.

**Demographic:** O(1) si existe la arista PREFERS. El grafo responde en tiempo constante.

**Pipeline completo:** O(|P| × |V|) donde P son los places candidatos y V los usuarios. Esto es el cuello de botella real.

La optimización clave fue mover la lógica de búsqueda de peers al interior del Cypher de `_fetch_candidates()`. En lugar de traer todos los usuarios a Python y calcular Jaccard en memoria, le pedimos a Neo4j que haga esa agregación nativamente. Eso redujo la carga de memoria en órdenes de magnitud.

Para escalar aún más, la siguiente mejora sería usar **Neo4j Graph Data Science Library** con `gds.nodeSimilarity()`, que está optimizado para grafos grandes."

---

## SLIDE 19 — SEPARADOR SECCIÓN 4 (15 seg) · Sebastián

> *Sebastián toma el frente.*

"Pasamos a implementación y demo."

---

## SLIDE 20 — ARQUITECTURA DEL SISTEMA (2 min) · Sebastián

"La arquitectura tiene seis capas bien separadas.

**Templates** son las 12 vistas HTML: landing, registro, onboarding, recomendaciones, detalle de destino, explorar, favoritos, perfil y más.

**Views** son los controladores Django: manejan sesiones, autenticación y coordinan los requests.

**Service Layer** es donde vive el algoritmo: `RecommendationService` con el dataclass `RecommendationScore`.

**Scoring Layer** son las funciones matemáticas puras: `score_place()`, `calculate_jaccard_similarity()`, `score_geographic_proximity()`.

**Query Layer** son los Cypher queries que hablan con Neo4j: `_fetch_student_profile()`, `_fetch_candidates()`, `add_review()`.

**Neo4j** en la base: el grafo con los 6 nodos y 8 tipos de relaciones.

Esta separación de capas nos permitió testear las funciones de scoring de forma independiente y debugear el algoritmo sin tocar la UI."

---

## SLIDE 21 — CÓDIGO CLAVE: PIPELINE (2 min) · Sebastián

"Este es el método `recommend()` — el punto de entrada del sistema.

Primero obtiene el perfil del estudiante con una query Cypher. Si no hay perfil, cae al fallback de popularidad global.

Detecta cold start comparando el número de visitas contra el umbral de 3.

Obtiene los candidatos — los places no visitados dentro del presupuesto — con otra query.

Para cada candidato calcula el score con `_score_candidate()`, que internamente llama a `score_place()`.

Ordena por score descendente y retorna el top N enriquecido con imagen, tag y la razón de match en texto.

Todo el pipeline corre en una sola llamada al método. El debug completo está disponible en `recommendation_debugger.py` que imprime cada paso en consola."

---

## SLIDE 22 — CÓDIGO CLAVE: SCORING (2 min) · Sebastián

"Este es `score_place()` en utils/scoring.py — la función matemática central.

Los pesos están como constantes al inicio. En la versión de scoring.py los pesos son ligeramente diferentes a los de RecommendationService porque fueron calibrados en distintas iteraciones. La versión definitiva vive en `_score_candidate()` del service.

El factor de serendipity está al final del cálculo, antes de escalar. Es un `random.uniform(0, 0.10)` — máximo 10% de variación aleatoria.

El resultado final se escala multiplicando por 100 y saturando en 100.0."

---

## SLIDE 23 — DATOS Y SETUP (2 min) · Sebastián

"Para levantar el sistema desde cero son tres comandos.

`migrate` configura SQLite para la autenticación de Django.

`setup_neo4j --clear --seed` es el más importante: limpia el grafo y lo puebla con los 31 destinos guatemaltecos, sus categorías, ciudades, y las relaciones PREFERS entre carreras y lugares con sus pesos.

`populate_simulated_users` lee `encuesta.csv` — datos de una encuesta real que hicimos a estudiantes de UVG — y crea nodos de Student en Neo4j con sus preferencias. Estos usuarios sintéticos son los que nutren el Collaborative Filtering desde el primer día.

Los 31 destinos tienen imágenes de Unsplash, costos reales en GTQ y coordenadas geográficas para el bonus de proximidad."

---

## SLIDE 24 — FLUJO DE USUARIO (1 min) · Sebastián

"El flujo es lineal y diseñado para alimentar el grafo rápidamente.

Registro — Onboarding donde el estudiante declara carrera, universidad, categorías y presupuesto — Recomendaciones inmediatas — Interacción con los resultados — Mejora continua.

Cada calificación actualiza `popularity` del lugar directamente en Neo4j con una query Cypher que recalcula el promedio. Eso significa que las recomendaciones mejoran con el uso."

---

## SLIDE 25 — API REST (1 min) · Sebastián

"Tenemos tres endpoints REST.

GET `/api/recommendations/` retorna las recomendaciones con el score completo y los componentes desglosados.

POST `/api/recommendations/review/` registra una visita con rating y comentario.

GET `/api/recommendations/explain/` fue especialmente útil para el desarrollo: retorna el desglose de score para un destino específico. Usamos esto para calibrar los pesos durante el semestre."

---

## SLIDE 26 — DESAFÍOS Y LECCIONES (3 min) · Sebastián

"Cuatro desafíos reales que enfrentamos.

**Cold start:** no lo habíamos considerado al principio. Lo descubrimos cuando un usuario nuevo sin historial recibía recomendaciones sin sentido. La solución fue el sistema de umbrales y redistribución de pesos.

**Calibración de pesos:** los pesos iniciales de 40/35/25 producían recomendaciones sesgadas hacia lugares de moda sin importar el perfil. Los ajustamos con datos reales de encuesta.csv hasta que el top 10 tuviera sentido para diferentes perfiles.

**Complejidad del Cypher:** este fue el desafío técnico más grande. La primera versión calculaba Jaccard en Python comparando cada usuario con todos los demás — O(n²). Con 200 usuarios simulados tardaba segundos. La solución fue mover toda la lógica de peers dentro de la query de candidatos. Ahora Neo4j hace la agregación nativa y el tiempo de respuesta bajó a milisegundos.

**Serendipity:** sin el factor aleatorio, si dos usuarios tenían el mismo perfil, recibían exactamente las mismas 10 recomendaciones en el mismo orden. El random.uniform(0, 0.10) resuelve esto sin sacrificar relevancia significativa."

---

## SLIDE 27 — CONCLUSIONES (2 min) · Marco

> *Marco vuelve al frente para cerrar.*

"Cuatro conclusiones del proyecto.

**Los grafos son la estructura correcta para recomendaciones.** No es solo una decisión tecnológica — es una decisión algorítmica. Las relaciones como ciudadanos de primera clase, con propiedades y traversals nativos, hacen que el problema sea más expresivo y eficiente.

**El algoritmo híbrido ganó a cualquier enfoque individual.** Content-based solo tiene baja diversidad. Collaborative solo falla con usuarios nuevos. Demographic solo es demasiado grueso. Los tres juntos se compensan.

**La complejidad computacional importa en producción.** Reescribir el O(n²) de Python a Cypher no fue un detalle de optimización — fue lo que hizo funcionar el sistema.

**La explicabilidad es un feature.** Poder decirle al usuario 'te recomendamos esto porque estudiantes de tu carrera lo visitaron' aumenta la confianza. No es solo un texto bonito — es parte del diseño del sistema."

---

## SLIDE 28 — Q&A (tiempo restante)

> *Todo el equipo al frente.*

"Gracias por su atención. Estamos disponibles para preguntas."

---

## Preguntas frecuentes — preparación

**P: ¿Por qué neomodel y no usar Cypher directo?**
R: neomodel nos da type safety en las definiciones de nodos, signals de Django, y validación de relaciones. Para el algoritmo sí usamos Cypher crudo con `db.cypher_query()` donde necesitamos control fino.

**P: ¿Cómo se actualiza la popularidad de un lugar?**
R: Con cada review POST, ejecutamos una query Cypher que calcula el promedio de todos los ratings de ese Place y lo escribe en `Place.popularity`. Es una actualización O(grado del nodo).

**P: ¿Qué pasaría si escalamos a miles de usuarios?**
R: El cuello de botella sería el Collaborative Filtering. La solución es mover ese cálculo a **Neo4j Graph Data Science Library** con `gds.nodeSimilarity()`, que está optimizado para grafos masivos y puede correrse en batch overnight.

**P: ¿Por qué el umbral de cold start es 3 y no otro número?**
R: Es una constante configurable (`_COLD_START_THRESHOLD = 3`). El número 3 lo elegimos porque con menos de 3 visitas el Jaccard tiene muy poco overlap para ser significativo. Con datos más ricos se podría subir a 5 o 10.

**P: ¿El serendipity no afecta la calidad de las recomendaciones?**
R: El máximo es 10% del score. En práctica, un destino con score 0.75 puede llegar máximo a 0.85 por serendipity. Eso no lo va a superar a un destino con score 0.90, pero sí puede rotar el puesto 8-10 del ranking, que es donde queremos variedad.

**P: ¿Por qué descartaron Community Detection?**
R: Community Detection agrupa nodos que comparten más conexiones entre sí que con el resto del grafo. El problema es que asume que si pertenecés a una comunidad, compartís todos los gustos de esa comunidad. Para turismo eso es demasiado grueso — dentro de la misma carrera hay personas con gustos completamente distintos.
