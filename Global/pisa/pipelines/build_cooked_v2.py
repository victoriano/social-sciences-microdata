#!/usr/bin/env python3
"""
Construcción del dataset "cooked" v2 de PISA España (2000-2025).

Extensión del cooked original (80 columnas) con variables accionables:
índices de familia y padres, hábitos, tiempo de instrucción, educación
infantil previa, clima de aula y prácticas docentes, socioemocionales,
bienestar, estrategias de aprendizaje, convivencia, educación financiera,
creatividad, ciencia y ambiente, y agregados de composición del centro.

Reglas:
- Nunca se inventan valores: si una variable no existe en un ciclo, queda
  vacía y la cobertura se documenta en cooked_cobertura_por_ciclo.csv.
- Los códigos de falta PISA (95-99, 995-999, 9995+, según variable) pasan
  a nulo.
- Las categóricas nuevas llevan etiquetas en español traducidas de las
  etiquetas oficiales OCDE de los metadatos por ciclo.
- Cada variable lleva "accionabilidad_padres" (alta/media/baja/nula):
  grado en que una familia puede influir directamente en ella.
  alta = decisión o hábito que la familia controla directamente
         (implicación, apoyo, hábitos en casa, elección de centro,
         educación infantil previa);
  media = influida en parte por la familia, mediada por el alumno o el
         centro (motivación, bienestar, uso de pantallas, orientación);
  baja  = depende del centro o del sistema; la familia solo influye
         indirectamente (clima de aula, prácticas docentes, recursos);
  nula  = estructural o de diseño muestral (sexo, región, ESCS, pesos, IDs).

Uso:
  python build_cooked_v2.py --cooked cooked_80.parquet --full full.parquet \
      --out-dir out/
"""
import argparse
import csv
import hashlib
from pathlib import Path

import duckdb

DIAS_SEMANA = {str(i): ("Nunca" if i == 0 else (f"{i} veces por semana" if i < 10 else "10 o más veces por semana")) for i in range(0, 11)}
DEBERES = {
    "1": "Hasta 30 min al día", "2": "Entre 30 min y 1 h al día",
    "3": "Entre 1 y 2 h al día", "4": "Entre 2 y 3 h al día",
    "5": "Entre 3 y 4 h al día", "6": "Más de 4 h al día",
}
ECEC = {
    "0": "Menos de 1 año", "1": "Entre 1 y 2 años", "2": "Entre 2 y 3 años",
    "3": "Entre 3 y 4 años", "4": "Entre 4 y 5 años", "5": "Entre 5 y 6 años",
    "6": "Entre 6 y 7 años", "7": "Entre 7 y 8 años", "8": "8 años o más",
}
ISCED = {
    "1": "Menos que secundaria inferior (ISCED 2)",
    "2": "Secundaria inferior (ISCED 2)",
    "3": "Secundaria superior (ISCED 3.3)",
    "4": "Secundaria superior no terminal (ISCED 3.4)",
    "5": "Postsecundaria no terciaria (ISCED 4)",
    "6": "FP superior / ciclo corto terciario (ISCED 5)",
    "7": "Grado universitario o equivalente (ISCED 6)",
    "8": "Máster o equivalente (ISCED 7)",
    "9": "Doctorado (ISCED 8)",
}
LENGUA = {"1": "Lengua del examen", "2": "Otra lengua"}
FAMSTRUC = {"1": "Monoparental", "2": "Dos progenitores", "3": "Otra estructura"}

# ESPEC: (nombre, fuente, tipo, umbral_falta, categorías, descripción, grupo, accionabilidad)
# tipos: indice | minutos | horas | conteo | categorica
ESPEC = []
def V(nombre, fuente, tipo, thr, cat, desc, grupo, acc):
    ESPEC.append(dict(nombre=nombre, fuente=fuente, tipo=tipo, thr=thr,
                      cat=cat, desc=desc, grupo=grupo, acc=acc))

# ---- 03 Situación socioeconómica
V("WEALTH", "WEALTH", "indice", 90, None,
  "Riqueza familiar (WLE). Posesiones materiales del hogar; no es renta en euros. Comparabilidad entre ciclos limitada.",
  "03 · Situación socioeconómica", "nula")
V("CULTPOSS", "CULTPOSS", "indice", 90, None,
  "Posesiones culturales del hogar (WLE): libros, arte, instrumentos. Proxy del capital cultural familiar.",
  "03 · Situación socioeconómica", "media")
V("HEDRES", "HEDRES", "indice", 90, None,
  "Recursos educativos del hogar (WLE): escritorio, lugar tranquilo de estudio, libros de texto, diccionarios.",
  "03 · Situación socioeconómica", "alta")
# ---- 04 Familia y hogar
V("PQSCHOOL", "PQSCHOOL", "indice", 90, None,
  "Calidad del centro percibida por los padres (WLE, cuestionario de padres; en España solo 2015 con datos).",
  "04 · Familia y hogar", "media")
V("PQGENSCI", "PQGENSCI", "indice", 90, None,
  "Visión de los padres sobre la ciencia (WLE, PAQ 2015).",
  "04 · Familia y hogar", "media")
V("PQENPERC", "PQENPERC", "indice", 90, None,
  "Preocupación de los padres por temas ambientales (WLE, PAQ 2015).",
  "04 · Familia y hogar", "media")
V("PQENVOPT", "PQENVOPT", "indice", 90, None,
  "Visión de los padres sobre los temas ambientales del futuro (WLE, PAQ 2015).",
  "04 · Familia y hogar", "media")
V("PRESUPP", "PRESUPP", "indice", 90, None,
  "Actividades científicas pasadas del hijo según los padres (WLE, PAQ 2015).",
  "04 · Familia y hogar", "alta")
V("CURSUPP", "CURSUPP", "indice", 90, None,
  "Apoyo parental actual al aprendizaje en casa (WLE, PAQ 2015).",
  "04 · Familia y hogar", "alta")
V("EMOSUPS", "EMOSUPS", "indice", 90, None,
  "Apoyo emocional de los padres percibido por el alumno (WLE, 2015/2018).",
  "04 · Familia y hogar", "alta")
V("SOCONPA", "SOCONPA", "indice", 90, None,
  "Conexión social con los padres: facilidad para hablar de preocupaciones (WLE, 2018/2022).",
  "04 · Familia y hogar", "alta")
V("FAMSTRUC", "FAMSTRUC", "categorica", 90, FAMSTRUC,
  "Estructura familiar (2012): monoparental, dos progenitores u otra.",
  "04 · Familia y hogar", "nula")
V("lengua_casa", "ST022Q01TA", "categorica", 90, LENGUA,
  "Lengua hablada en casa la mayor parte del tiempo: lengua del examen u otra (2015-2025).",
  "04 · Familia y hogar", "nula")
# ---- 05 Bienestar
V("EUDMO", "EUDMO", "indice", 90, None,
  "Sentido y propósito en la vida (eudaimonía, WLE 2018).", "05 · Bienestar", "media")
V("SWBP", "SWBP", "indice", 90, None,
  "Bienestar subjetivo: afecto positivo (WLE 2018).", "05 · Bienestar", "media")
V("RESILIENCE", "RESILIENCE", "indice", 90, None,
  "Resiliencia percibida ante dificultades (WLE 2018).", "05 · Bienestar", "media")
V("LIFESAT", "LIFESAT", "indice", 90, None,
  "Satisfacción con la vida por dominios (WLE 2022).", "05 · Bienestar", "media")
V("PSYCHSYM", "PSYCHSYM", "indice", 90, None,
  "Síntomas psicosomáticos (WLE 2022; más alto = más síntomas).", "05 · Bienestar", "media")
V("BODYIMA", "BODYIMA", "indice", 90, None,
  "Imagen corporal (WLE 2018/2022).", "05 · Bienestar", "media")
V("SOCCON", "SOCCON", "indice", 90, None,
  "Conexiones sociales: facilidad para comunicar preocupaciones (WLE 2022).", "05 · Bienestar", "media")
V("EXPWB", "EXPWB", "indice", 90, None,
  "Bienestar experimentado el día anterior (WLE 2022). Cobertura parcial (submuestra).", "05 · Bienestar", "media")
# ---- 08 Entorno y hábitos digitales
V("HOMESCH", "HOMESCH", "indice", 90, None,
  "Uso de TIC fuera del centro para tareas escolares (WLE 2015/2018).",
  "08 · Entorno y hábitos digitales", "alta")
V("USESCH", "USESCH", "indice", 90, None,
  "Uso de TIC en el centro (WLE 2009-2018).", "08 · Entorno y hábitos digitales", "baja")
V("USEMATH", "USEMATH", "indice", 90, None,
  "Uso de TIC en las clases de matemáticas (WLE 2012).", "08 · Entorno y hábitos digitales", "baja")
V("SOIAICT", "SOIAICT", "indice", 90, None,
  "Las TIC como tema de interacción social (WLE 2015/2018/2025).",
  "08 · Entorno y hábitos digitales", "media")

# ---- 09 Hábitos y expectativas
V("DURECEC", "DURECEC", "categorica", 90, ECEC,
  "Duración de la educación infantil previa (ECEC) antes de primaria (2015/2018/2022).",
  "09 · Hábitos y expectativas", "alta")
V("STUDYHMW", "STUDYHMW", "categorica", 90, DIAS_SEMANA,
  "Días por semana estudiando o haciendo deberes fuera del horario (2022).",
  "09 · Hábitos y expectativas", "alta")
V("ST296Q01JA", "ST296Q01JA", "categorica", 90, DEBERES,
  "Tiempo diario de deberes de matemáticas (2022).", "09 · Hábitos y expectativas", "alta")
V("ST296Q02JA", "ST296Q02JA", "categorica", 90, DEBERES,
  "Tiempo diario de deberes de lengua (2022).", "09 · Hábitos y expectativas", "alta")
V("ST296Q03JA", "ST296Q03JA", "categorica", 90, DEBERES,
  "Tiempo diario de deberes de ciencias (2022/2025).", "09 · Hábitos y expectativas", "alta")
V("WORKPAY", "WORKPAY", "categorica", 90, DIAS_SEMANA,
  "Días por semana trabajando remunerado fuera del horario escolar (2022/2025).",
  "09 · Hábitos y expectativas", "alta")
V("WORKHOME", "WORKHOME", "categorica", 90, DIAS_SEMANA,
  "Días por semana en tareas del hogar o cuidando familiares (2022).",
  "09 · Hábitos y expectativas", "alta")
V("MISSSC", "MISSSC", "categorica", 90,
  {"0": "Nunca faltó más de 3 meses", "1": "Faltó más de 3 meses al menos una vez"},
  "Haber faltado al colegio más de 3 meses alguna vez (2022; sin datos para España: la columna solo contiene códigos de falta).",
  "09 · Hábitos y expectativas", "alta")
V("EXPECEDU", "EXPECEDU", "categorica", 90, ISCED,
  "Nivel educativo máximo que el alumno espera completar (2022/2025).",
  "09 · Hábitos y expectativas", "media")
V("INFOCAR", "INFOCAR", "indice", 90, None,
  "Búsqueda de información sobre carreras futuras (WLE 2018).",
  "09 · Hábitos y expectativas", "alta")
V("MMINS", "MMINS", "minutos", 9000, None,
  "Minutos semanales de clase de matemáticas (2000-2018).", "09 · Hábitos y expectativas", "nula")
V("LMINS", "LMINS", "minutos", 9000, None,
  "Minutos semanales de clase de lengua (2009-2018).", "09 · Hábitos y expectativas", "nula")
V("SMINS", "SMINS", "minutos", 9000, None,
  "Minutos semanales de clase de ciencias (2000-2018).", "09 · Hábitos y expectativas", "nula")
V("TMINS", "TMINS", "minutos", 9000, None,
  "Minutos semanales totales de instrucción (2003/2015/2018).", "09 · Hábitos y expectativas", "nula")
V("OUTHOURS", "OUTHOURS", "horas", 900, None,
  "Horas semanales de estudio o clases fuera del horario escolar (2012/2015).",
  "09 · Hábitos y expectativas", "alta")
V("HADDINST", "HADDINST", "horas", 900, None,
  "Horas totales de instrucción adicional (refuerzo) por semana (2015).",
  "09 · Hábitos y expectativas", "alta")
V("ADDSCIIN", "ADDSCIIN", "conteo", 5, None,
  "Número de materias de ciencias con instrucción adicional (2015).",
  "09 · Hábitos y expectativas", "alta")

# ---- 10 Motivación y autorregulación
V("INSTMOT", "INSTMOT", "indice", 90, None, "Motivación instrumental en matemáticas (WLE 2003/2012).", "10 · Motivación y autorregulación", "media")
V("INTMAT", "INTMAT", "indice", 90, None, "Interés por las matemáticas (WLE 2003/2012).", "10 · Motivación y autorregulación", "media")
V("MATINTFC", "MATINTFC", "indice", 90, None, "Intenciones futuras con las matemáticas (WLE 2012).", "10 · Motivación y autorregulación", "media")
V("OPENPS", "OPENPS", "indice", 90, None, "Apertura a la resolución de problemas (WLE 2012).", "10 · Motivación y autorregulación", "media")
V("MATHEFF", "MATHEFF", "indice", 90, None, "Autoeficacia en matemáticas (WLE 2003/2012/2022; opciones de respuesta invertidas en 2022).", "10 · Motivación y autorregulación", "media")
V("SCMAT", "SCMAT", "indice", 90, None, "Autoconcepto en matemáticas (WLE 2003/2012).", "10 · Motivación y autorregulación", "media")
V("FAILMAT", "FAILMAT", "indice", 90, None, "Atribución del fracaso en matemáticas (WLE 2012).", "10 · Motivación y autorregulación", "media")
V("MATWKETH", "MATWKETH", "indice", 90, None, "Ética de trabajo en matemáticas (WLE 2012).", "10 · Motivación y autorregulación", "media")
V("ATTLNACT", "ATTLNACT", "indice", 90, None, "Actitud hacia las actividades de aprendizaje (WLE 2012/2018).", "10 · Motivación y autorregulación", "media")
V("ATSCHL", "ATSCHL", "indice", 90, None, "Actitud hacia la escuela: resultados de aprendizaje (WLE 2003/2009/2012).", "10 · Motivación y autorregulación", "media")
V("MATBEH", "MATBEH", "indice", 90, None, "Comportamiento en matemáticas (WLE 2012).", "10 · Motivación y autorregulación", "media")
V("MOTIVAT", "MOTIVAT", "indice", 90, None, "Motivación de logro (WLE 2015).", "10 · Motivación y autorregulación", "media")
V("INSTSCIE", "INSTSCIE", "indice", 90, None, "Motivación instrumental por la ciencia (WLE 2006/2015).", "10 · Motivación y autorregulación", "media")
V("INTBRSCI", "INTBRSCI", "indice", 90, None, "Interés por temas amplios de ciencia (WLE 2015).", "10 · Motivación y autorregulación", "media")
V("ANXTEST", "ANXTEST", "indice", 90, None, "Ansiedad ante los exámenes (WLE 2015).", "10 · Motivación y autorregulación", "media")
V("COOPERATE", "COOPERATE", "indice", 90, None, "Disposición a la colaboración: disfrutar cooperando (WLE 2015).", "10 · Motivación y autorregulación", "media")
V("CPSVALUE", "CPSVALUE", "indice", 90, None, "Disposición a la colaboración: valorar la cooperación (WLE 2015).", "10 · Motivación y autorregulación", "media")
V("GROSAGR", "GROSAGR", "indice", 90, None, "Mentalidad de crecimiento (WLE 2022).", "10 · Motivación y autorregulación", "media")
V("MATHEF21", "MATHEF21", "indice", 90, None, "Autoeficacia en mates: razonamiento y habilidades s. XXI (WLE 2022).", "10 · Motivación y autorregulación", "media")
V("MATHPERS", "MATHPERS", "indice", 90, None, "Esfuerzo y persistencia en matemáticas (WLE 2022).", "10 · Motivación y autorregulación", "media")
V("MATHMOT", "MATHMOT", "categorica", 90, {"0": "No más motivado en mates que en otras materias", "1": "Más motivado en mates que en otras materias"}, "Motivación comparada hacia las matemáticas (2022).", "10 · Motivación y autorregulación", "media")
V("MATHEASE", "MATHEASE", "categorica", 90, {"0": "No percibe las mates como más fáciles", "1": "Percibe las mates como más fáciles que otras materias"}, "Percepción de las mates como más fáciles que otras materias (2022).", "10 · Motivación y autorregulación", "media")
V("PERSEVAGR", "PERSEVAGR", "indice", 90, None, "Perseverancia (WLE 2022).", "10 · Motivación y autorregulación", "media")
V("CURIOAGR", "CURIOAGR", "indice", 90, None, "Curiosidad (WLE 2022).", "10 · Motivación y autorregulación", "media")
V("ASSERAGR", "ASSERAGR", "indice", 90, None, "Asertividad (WLE 2022).", "10 · Motivación y autorregulación", "media")
V("EMPATAGR", "EMPATAGR", "indice", 90, None, "Empatía (WLE 2022).", "10 · Motivación y autorregulación", "media")
V("COOPAGR", "COOPAGR", "indice", 90, None, "Cooperación (WLE 2022).", "10 · Motivación y autorregulación", "media")
V("EMOCOAGR", "EMOCOAGR", "indice", 90, None, "Control emocional (WLE 2022).", "10 · Motivación y autorregulación", "media")
V("MASTGOAL", "MASTGOAL", "indice", 90, None, "Orientación a metas de maestría (WLE 2018).", "10 · Motivación y autorregulación", "media")
V("WORKMAST", "WORKMAST", "indice", 90, None, "Ética de trabajo y esfuerzo (WLE 2018).", "10 · Motivación y autorregulación", "media")
V("COMPETE", "COMPETE", "indice", 90, None, "Competitividad (WLE 2018).", "10 · Motivación y autorregulación", "media")
V("GFOFAIL", "GFOFAIL", "indice", 90, None, "Miedo general al fracaso (WLE 2018). Ojo: es el indicador de mentalidad de crecimiento de 2018, no comparable con GROSAGR de 2022.", "10 · Motivación y autorregulación", "media")
V("ADAPTIVITY", "ADAPTIVITY", "indice", 90, None, "Adaptación de la instrucción percibida (WLE 2018).", "10 · Motivación y autorregulación", "baja")
V("COGFLEX", "COGFLEX", "indice", 90, None, "Flexibilidad/adaptabilidad cognitiva (WLE 2018).", "10 · Motivación y autorregulación", "media")
V("JOYREAD", "JOYREAD", "indice", 90, None, "Gusto por la lectura (WLE 2000/2009/2018).", "10 · Motivación y autorregulación", "alta")
V("METASUM", "METASUM", "indice", 90, None, "Metacognición lectora: resumir (2009/2018).", "10 · Motivación y autorregulación", "media")
V("UNDREM", "UNDREM", "indice", 90, None, "Metacognición lectora: comprender y recordar (2009/2018).", "10 · Motivación y autorregulación", "media")
V("METASPAM", "METASPAM", "indice", 90, None, "Metacognición: evaluar credibilidad de fuentes (2018).", "10 · Motivación y autorregulación", "media")
V("ELAB", "ELAB", "indice", 90, None, "Estrategias de elaboración (WLE 2003/2009).", "10 · Motivación y autorregulación", "media")
V("CSTRAT", "CSTRAT", "indice", 90, None, "Estrategias de control (WLE 2003/2009).", "10 · Motivación y autorregulación", "media")
V("MEMOR", "MEMOR", "indice", 90, None, "Estrategias de memorización (WLE 2003/2009).", "10 · Motivación y autorregulación", "media")
V("DIVREAD", "DIVREAD", "indice", 90, None, "Diversidad de lectura (WLE 2000/2009).", "10 · Motivación y autorregulación", "alta")
V("ONLNREAD", "ONLNREAD", "indice", 90, None, "Lectura en línea (WLE 2009).", "10 · Motivación y autorregulación", "media")
V("SDLEFF", "SDLEFF", "indice", 90, None, "Autoeficacia en aprendizaje autodirigido (WLE 2022; submuestra).", "10 · Motivación y autorregulación", "media")
V("PROBSELF", "PROBSELF", "indice", 90, None, "Problemas con el aprendizaje autodirigido (WLE 2022; submuestra).", "10 · Motivación y autorregulación", "media")
V("LEARRES", "LEARRES", "indice", 90, None, "Recursos de aprendizaje usados con el centro cerrado (WLE 2022; submuestra).", "10 · Motivación y autorregulación", "alta")
V("EFFORT1", "EFFORT1", "indice", 90, None, "Esfuerzo declarado en la prueba PISA, 1-10 (2018/2022/2025). Técnica: interpretar caídas de rendimiento.", "10 · Motivación y autorregulación", "nula")
V("DEFFORT", "DEFFORT", "indice", 90, None, "Diferencia de esfuerzo declarado entre la prueba y un esfuerzo real (2006/2012). Técnica.", "10 · Motivación y autorregulación", "nula")
V("PISADIFF", "PISADIFF", "indice", 90, None, "Percepción de dificultad de la prueba PISA (WLE 2018). Técnica.", "10 · Motivación y autorregulación", "nula")

# ---- 11 Aula y aprendizaje por materia
V("DISCLIMA", "DISCLIMA", "indice", 90, None, "Clima disciplinario (WLE 2000/2009/2012/2018; la materia de referencia varía por ciclo: general 2000, lengua 2009/2018, mates 2012).", "11 · Aula y aprendizaje por materia", "baja")
V("DISCLIM", "DISCLIM", "indice", 90, None, "Clima disciplinario en matemáticas (WLE 2022; también existe con datos en 2003). No comparar con DISCLIMA.", "11 · Aula y aprendizaje por materia", "baja")
V("STUDREL", "STUDREL", "indice", 90, None, "Relación alumno-profesor (WLE 2000/2009/2012).", "11 · Aula y aprendizaje por materia", "baja")
V("RELATST", "RELATST", "indice", 90, None, "Calidad de la relación alumno-profesor (WLE 2022).", "11 · Aula y aprendizaje por materia", "baja")
V("CLSMAN", "CLSMAN", "indice", 90, None, "Gestión del aula del profesor de mates (WLE 2012).", "11 · Aula y aprendizaje por materia", "baja")
V("TCHBEHFA", "TCHBEHFA", "indice", 90, None, "Comportamiento docente: evaluación formativa (2012).", "11 · Aula y aprendizaje por materia", "baja")
V("TCHBEHSO", "TCHBEHSO", "indice", 90, None, "Comportamiento docente: orientación al alumno (2012).", "11 · Aula y aprendizaje por materia", "baja")
V("TCHBEHTD", "TCHBEHTD", "indice", 90, None, "Comportamiento docente: instrucción directa (2012).", "11 · Aula y aprendizaje por materia", "baja")
V("COGACT", "COGACT", "indice", 90, None, "Activación cognitiva en matemáticas (2012).", "11 · Aula y aprendizaje por materia", "baja")
V("COGACMCO", "COGACMCO", "indice", 90, None, "Activación cognitiva en mates: fomentar el pensamiento (WLE 2022).", "11 · Aula y aprendizaje por materia", "baja")
V("COGACRCO", "COGACRCO", "indice", 90, None, "Activación cognitiva en mates: fomentar el razonamiento (WLE 2022).", "11 · Aula y aprendizaje por materia", "baja")
V("COGACSC", "COGACSC", "indice", 90, None, "Activación cognitiva en ciencias (WLE 2025).", "11 · Aula y aprendizaje por materia", "baja")
V("EXPOFA", "EXPOFA", "indice", 90, None, "Exposición a tareas de mates formales y aplicadas (WLE 2022).", "11 · Aula y aprendizaje por materia", "baja")
V("EXPO21ST", "EXPO21ST", "indice", 90, None, "Exposición a tareas de razonamiento matemático y s. XXI (WLE 2022).", "11 · Aula y aprendizaje por materia", "baja")
V("EXAPPLM", "EXAPPLM", "indice", 90, None, "Experiencia con tareas de mates aplicadas (2012).", "11 · Aula y aprendizaje por materia", "baja")
V("EXPUREM", "EXPUREM", "indice", 90, None, "Experiencia con tareas de mates puras (2012).", "11 · Aula y aprendizaje por materia", "baja")
V("DIRINS", "DIRINS", "indice", 90, None, "Instrucción dirigida por el profesor (WLE 2018).", "11 · Aula y aprendizaje por materia", "baja")
V("TEACHINT", "TEACHINT", "indice", 90, None, "Interés percibido del profesor (WLE 2018).", "11 · Aula y aprendizaje por materia", "baja")
V("PERFEED", "PERFEED", "indice", 90, None, "Feedback percibido del profesor (WLE 2015/2018).", "11 · Aula y aprendizaje por materia", "baja")
V("ADINST", "ADINST", "indice", 90, None, "Adaptación de la enseñanza (WLE 2015).", "11 · Aula y aprendizaje por materia", "baja")
V("TDTEACH", "TDTEACH", "indice", 90, None, "Enseñanza de ciencias dirigida por el profesor (WLE 2015).", "11 · Aula y aprendizaje por materia", "baja")
V("IBTEACH", "IBTEACH", "indice", 90, None, "Enseñanza de ciencias por indagación (WLE 2015).", "11 · Aula y aprendizaje por materia", "baja")
V("ENGSCIPR", "ENGSCIPR", "indice", 90, None, "Implicación del alumnado en prácticas científicas (WLE 2025).", "11 · Aula y aprendizaje por materia", "baja")

# ---- 12 Convivencia y contexto global
V("ATTIMM", "ATTIMM", "indice", 90, None, "Actitud del alumnado hacia los inmigrantes (WLE 2018).", "12 · Convivencia y contexto global", "baja")
V("DISCRIM", "DISCRIM", "indice", 90, None, "Clima discriminatorio en el centro (WLE 2018).", "12 · Convivencia y contexto global", "baja")
V("PERCOMP", "PERCOMP", "indice", 90, None, "Percepción de competitividad en el centro (WLE 2018).", "12 · Convivencia y contexto global", "baja")
V("PERCOOP", "PERCOOP", "indice", 90, None, "Percepción de cooperación en el centro (WLE 2018).", "12 · Convivencia y contexto global", "baja")
V("PERSPECT", "PERSPECT", "indice", 90, None, "Toma de perspectiva (WLE 2018).", "12 · Convivencia y contexto global", "media")
V("GLOBMIND", "GLOBMIND", "indice", 90, None, "Mentalidad global (WLE 2018).", "12 · Convivencia y contexto global", "media")
V("GCSELFEFF", "GCSELFEFF", "indice", 90, None, "Autoeficacia ante temas globales (WLE 2018).", "12 · Convivencia y contexto global", "media")
V("INTCULT", "INTCULT", "indice", 90, None, "Interés por otras culturas (WLE 2018).", "12 · Convivencia y contexto global", "media")
V("RESPECT", "RESPECT", "indice", 90, None, "Respeto por personas de otras culturas (WLE 2018).", "12 · Convivencia y contexto global", "media")
V("GCAWARE", "GCAWARE", "indice", 90, None, "Conciencia de temas globales (WLE 2018).", "12 · Convivencia y contexto global", "media")

# ---- 13 Educación financiera
V("FLSCHOOL", "FLSCHOOL", "indice", 90, None, "Educación financiera recibida en el centro (WLE 2018/2022).", "13 · Educación financiera", "baja")
V("FLFAMILY", "FLFAMILY", "indice", 90, None, "Implicación parental en temas financieros (WLE 2018/2022).", "13 · Educación financiera", "alta")
V("FCFMLRTY", "FCFMLRTY", "conteo", 90, None, "Familiaridad con conceptos financieros (nº de conceptos aprendidos, 2018/2022).", "13 · Educación financiera", "media")
V("FLCONFIN", "FLCONFIN", "indice", 90, None, "Confianza en asuntos financieros (WLE 2018/2022).", "13 · Educación financiera", "media")
V("FLCONICT", "FLCONICT", "indice", 90, None, "Confianza financiera con dispositivos digitales (WLE 2018/2022).", "13 · Educación financiera", "media")

# ---- 14 Creatividad (2022)
V("CREATEFF", "CREATEFF", "indice", 90, None, "Autoeficacia creativa (WLE 2022).", "14 · Creatividad (2022)", "media")
V("OPENART", "OPENART", "indice", 90, None, "Apertura al arte y la reflexión (WLE 2022).", "14 · Creatividad (2022)", "media")
V("CREATSCH", "CREATSCH", "indice", 90, None, "Entorno escolar y de aula creativo (WLE 2022).", "14 · Creatividad (2022)", "baja")
V("CREATAS", "CREATAS", "indice", 90, None, "Actividades creativas en el centro (WLE 2022).", "14 · Creatividad (2022)", "baja")
V("CREATOOS", "CREATOOS", "indice", 90, None, "Actividades creativas fuera del centro (WLE 2022).", "14 · Creatividad (2022)", "alta")
V("CREATFAM", "CREATFAM", "indice", 90, None, "Entorno creativo de iguales y familia (WLE 2022).", "14 · Creatividad (2022)", "alta")

# ---- 15 Ciencia y ambiente
V("SCIEACT", "SCIEACT", "indice", 90, None, "Actividades científicas (WLE 2006/2015).", "15 · Ciencia y ambiente", "alta")
V("EPIST", "EPIST", "indice", 90, None, "Creencias epistemológicas sobre la ciencia (WLE 2015).", "15 · Ciencia y ambiente", "media")
V("ENVAWARE", "ENVAWARE", "indice", 90, None, "Conciencia ambiental (WLE 2006/2015/2025; comparabilidad limitada entre ciclos).", "15 · Ciencia y ambiente", "media")
V("ENVOPT", "ENVOPT", "indice", 90, None, "Optimismo ambiental (WLE 2006/2015).", "15 · Ciencia y ambiente", "media")
V("ENVAPART", "ENVAPART", "indice", 90, None, "Participación en actividades ambientales (WLE 2025).", "15 · Ciencia y ambiente", "alta")
V("ENVCAPCH", "ENVCAPCH", "indice", 90, None, "Creencia en la propia capacidad de generar cambio ambiental (WLE 2025).", "15 · Ciencia y ambiente", "media")
V("OPENVLRN", "OPENVLRN", "indice", 90, None, "Oportunidades de aprendizaje ambiental en clase (WLE 2025).", "15 · Ciencia y ambiente", "baja")
V("COLLENEFF", "COLLENEFF", "indice", 90, None, "Eficacia colectiva ambiental (WLE 2025).", "15 · Ciencia y ambiente", "media")

# ---- 16 Composición del centro (agregados calculados por CNTSCHID)
# Se calculan desde las columnas ya armonizadas del cooked; ver builder.
AGREGADOS = [
    ("centro_escs_medio", "ESCS medio del centro (ponderado con W_FSTUWT). Composición socioeconómica; base para análisis de segregación escolar.", "baja"),
    ("centro_pct_inmigrantes", "% de alumnado de origen inmigrante (primera o segunda generación) en el centro, sobre alumnos con dato, ponderado.", "baja"),
    ("centro_pct_repetidores", "% de repetidores en el centro, sobre alumnos con dato, ponderado.", "baja"),
    ("centro_pct_ausentismo", "% de alumnado que faltó a clases o días de colegio en el centro, sobre alumnos con dato, ponderado.", "baja"),
    ("centro_alumnos_muestra", "Nº de alumnos del centro en la muestra PISA del ciclo. Control de fiabilidad de los agregados: descartar centros con pocos alumnos.", "nula"),
]

# ---------------------------------------------------------------------------
# Accionabilidad de las 80 columnas existentes (cooked original)
# ---------------------------------------------------------------------------
ACC80 = {
    "fila_origen": "nula", "CNTSCHID": "nula", "pisa_year": "nula",
    "math_exploracion": "nula", "read_exploracion": "nula", "scie_exploracion": "nula",
    "sexo": "nula", "AGE": "nula", "origen": "nula", "region": "nula",
    "sector": "media", "GRADE": "nula", "repeticion": "baja",
    "educacion_familiar": "nula", "nivel_socioeconomico": "nula", "ESCS": "nula",
    "PAREDINT": "nula", "HISEI": "nula",
    "HOMEPOS": "media", "recursos_hogar": "alta", "posesiones_hogar": "media",
    "apoyo_familiar": "alta", "FAMSUP": "alta",
    "BELONG": "media", "BULLIED": "media", "ST016Q01NA": "media",
    "W_FSTUWT": "nula",
    "ST438Q01DA": "alta", "ST438Q02DA": "alta", "ST438Q03DA": "alta",
    "ST438Q04DA": "alta", "IC170Q10DA": "baja", "IC171Q10DA": "alta",
    "ST436Q16DA": "baja", "IC182Q05DA": "media",
    "AIUSESCH": "baja", "ICTSCH": "baja", "ICTHOME": "alta", "ICTQUAL": "alta",
    "ICTFEED": "baja", "ICTOUT": "alta", "ICTWKDY": "alta", "ICTWKEND": "alta",
    "ICTREG": "media", "ICTINFO": "media", "ICTDISTR": "media",
    "ICTRES": "alta", "ICTAVSCH": "baja",
    "ST255Q01JA": "alta", "ST296Q04JA": "alta", "ST322Q01JA": "alta",
    "SKIPPING": "alta", "TARDYSD": "alta", "EXERPRAC": "alta",
    "BSMJ": "media", "SISCO": "media",
    "PERSEV": "media", "CURIO": "media", "ENPROBS": "media", "COGABIL": "media",
    "GOALSET": "media", "SELFREG": "media", "DIGINTLRN": "media", "INTICT": "media",
    "FEELSAFE": "media", "TEACHSUP_2022": "baja", "TEACHSUP_2025": "baja",
    "DISCLISCI": "baja", "JOYSCIE": "media", "EFFSCIE": "media", "ANXMAT": "media",
    "ST273Q06DA": "baja", "ST097Q06DA": "baja",
    "numero_pv_math": "nula", "peso_math": "nula", "numero_pv_read": "nula",
    "peso_read": "nula", "numero_pv_scie": "nula", "peso_scie": "nula",
    "aviso_ciclo": "nula",
}

MISSING_CODES = "95,96,97,98,99,995,996,997,998,999,9995,9996,9997,9998,9999,99995,99996,99997,99998,99999,9999995,9999996,9999997,9999998,99999999"


def sql_nueva_columna(e):
    """SQL que extrae una variable del full parquet con faltantes a nulo."""
    src, tipo, thr = e["fuente"], e["tipo"], e["thr"]
    base = f"try_cast({src} as double)"
    if tipo == "categorica":
        limpio = f"case when {base} is null or abs({base}) >= {thr} then null else cast({base} as int) end"
        pares = " ".join(f"when cast({limpio} as varchar) = '{k}' then '{v}'" for k, v in e["cat"].items())
        return f"case {pares} else null end"
    return f"case when {base} is null or abs({base}) >= {thr} then null else {base} end"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cooked", required=True)
    ap.add_argument("--full", required=True)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect()
    fuentes = sorted({e["fuente"] for e in ESPEC})
    print(f"Extrayendo {len(ESPEC)} variables nuevas del full parquet...")

    select_nuevas = ",\n  ".join(
        f"{sql_nueva_columna(e)} as {e['nombre']}" for e in ESPEC
    )
    # fila_origen = índice base cero dentro del ciclo, en orden de archivo.
    # Verificado contra cooked: 0 desajustes en ANXMAT/BELONG/ESCS (2012-2022).
    con.execute(f"""
        create or replace table nuevas as
        with base as (
          select row_number() over () - 1 as rn, pisa_year,
            {select_nuevas}
          from read_parquet('{args.full}')
        )
        -- 2022/2025 comparten fichero CY09: fila_origen continua (0..30799, 30800..60765)
        select pisa_year,
               rn - min(rn) over (partition by case when pisa_year in (2022, 2025) then 9999 else pisa_year end) as fila_origen,
               * exclude (rn, pisa_year)
        from base
    """)

    print("Calculando agregados por centro desde el cooked...")
    con.execute(f"""
        create or replace table agregados as
        select pisa_year, CNTSCHID,
          sum(ESCS * W_FSTUWT) / nullif(sum(case when ESCS is not null then W_FSTUWT end), 0)
            as centro_escs_medio,
          100.0 * sum(case when origen in ('Primera generación','Segunda generación') then W_FSTUWT else 0 end)
            / nullif(sum(case when origen is not null and origen <> 'Sin dato' then W_FSTUWT end), 0)
            as centro_pct_inmigrantes,
          100.0 * sum(case when repeticion = 'Repetidor' then W_FSTUWT else 0 end)
            / nullif(sum(case when repeticion is not null and repeticion <> 'Sin dato' then W_FSTUWT end), 0)
            as centro_pct_repetidores,
          100.0 * sum(case when SKIPPING = 'Faltó al menos una vez' then W_FSTUWT else 0 end)
            / nullif(sum(case when SKIPPING is not null then W_FSTUWT end), 0)
            as centro_pct_ausentismo,
          count(*) as centro_alumnos_muestra
        from read_parquet('{args.cooked}')
        where CNTSCHID is not null
        group by pisa_year, CNTSCHID
    """)

    out_parquet = out / "pisa_espana_2000_2025_cocinado.parquet"
    print("Escribiendo cooked v2...")
    con.execute(f"""
        copy (
          select c.*, n.* exclude (pisa_year, fila_origen),
                 a.* exclude (pisa_year, CNTSCHID)
          from read_parquet('{args.cooked}') c
          left join nuevas n using (pisa_year, fila_origen)
          left join agregados a on a.pisa_year = c.pisa_year and a.CNTSCHID = c.CNTSCHID
        ) to '{out_parquet}' (format parquet, compression zstd)
    """)
    ncols = con.execute(f"select count(*) from (describe select * from read_parquet('{out_parquet}'))").fetchone()[0]
    nrows = con.execute(f"select count(*) from read_parquet('{out_parquet}')").fetchone()[0]
    print(f"cooked v2: {nrows} filas x {ncols} columnas")
    sha = hashlib.sha256(out_parquet.read_bytes()).hexdigest()
    print("sha256:", sha)

    # Cobertura real por ciclo de las columnas nuevas y agregadas
    cols_nuevas = [e["nombre"] for e in ESPEC] + [a[0] for a in AGREGADOS]
    partes = []
    for cn in cols_nuevas:
        partes.append(f"""
          select pisa_year as year, '{cn}' as column, count({cn}) as observed
          from read_parquet('{out_parquet}') group by pisa_year""")
    con.execute(f"""
        create or replace table cob as
        select * from ({" union all ".join(partes)})
    """)
    con.execute("""
        create or replace table tot as
        select pisa_year as year, count(*) as total
        from read_parquet('%s') group by pisa_year
    """ % out_parquet)
    cov_path = out / "cooked_v2_cobertura_nuevas_por_ciclo.csv"
    with open(cov_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "column", "observed", "total", "percent"])
        for row in con.execute("""
            select cob.year, cob.column, cob.observed, tot.total,
                   round(100.0 * cob.observed / tot.total, 1) as percent
            from cob join tot using (year) order by cob.column, cob.year
        """).fetchall():
            w.writerow(row)
    print("cobertura:", cov_path)

    # Diccionario v2: 80 originales (con accionabilidad) + nuevas + agregados
    import pandas as pd
    dic = pd.read_csv(Path(__file__).resolve().parent.parent / "site/metadata/cooked_diccionario.csv")
    dic["accionabilidad_padres"] = dic["codigo"].map(ACC80).fillna("nula")
    nuevas_rows = [{
        "codigo": e["nombre"],
        "nombre": e["nombre"],
        "descripcion": e["desc"],
        "grupo": e["grupo"],
        "columnas_origen": e["fuente"],
        "accionabilidad_padres": e["acc"],
    } for e in ESPEC] + [{
        "codigo": a[0],
        "nombre": a[0],
        "descripcion": a[1],
        "grupo": "16 · Composición del centro (agregados)",
        "columnas_origen": "calculada",
        "accionabilidad_padres": a[2],
    } for a in AGREGADOS]
    dic_v2 = pd.concat([dic, pd.DataFrame(nuevas_rows)], ignore_index=True)
    dic_path = out / "cooked_diccionario_v2.csv"
    dic_v2.to_csv(dic_path, index=False)
    print("diccionario v2:", dic_path, len(dic_v2), "filas")

    # Cobertura completa v2 (todas las columnas) por ciclo
    todas = [r[0] for r in con.execute(f"select column_name from (describe select * from read_parquet('{out_parquet}'))").fetchall()]
    partes = []
    for cn in todas:
        partes.append(f"select pisa_year as year, '{cn}' as column, count(\"{cn}\") as observed from read_parquet('{out_parquet}') group by pisa_year")
    con.execute("create or replace table cob_all as select * from (" + " union all ".join(partes) + ")")
    cov_all = out / "cooked_cobertura_por_ciclo.csv"
    with open(cov_all, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "column", "observed", "total", "percent"])
        for row in con.execute("""
            select cob_all.year, cob_all.column, cob_all.observed, tot.total,
                   round(100.0 * cob_all.observed / tot.total, 1)
            from cob_all join tot using (year) order by cob_all.column, cob_all.year
        """).fetchall():
            w.writerow(row)
    print("cobertura completa:", cov_all, len(todas), "columnas")


if __name__ == "__main__":
    main()
