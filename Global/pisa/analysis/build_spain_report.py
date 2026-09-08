"""Build a bounded, aggregate-only report artifact from reviewed analysis CSVs."""
import argparse
import json
from pathlib import Path

import pandas as pd

REGIONS = {'Andalusia':'Andalucía','Aragon':'Aragón','Asturias':'Asturias',
 'Balearic Islands':'Baleares','Basque Country':'País Vasco','Canary Islands':'Canarias',
 'Cantabria':'Cantabria','Castile and Leon':'Castilla y León','Castile-La Mancha':'Castilla-La Mancha',
 'Ceuta':'Ceuta','Comunidad Valenciana':'Comunitat Valenciana','Extremadura':'Extremadura',
 'Galicia':'Galicia','La Rioja':'La Rioja','Madrid':'Madrid','Melilla':'Melilla','Murcia':'Murcia','Navarre':'Navarra'}
DOMAINS={'MATH':'Matemáticas','READ':'Lectura','SCIE':'Ciencias'}
ITEMS={'ST300Q01JA':'Hablan de cómo va en el colegio','ST300Q05JA':'Hablan de problemas escolares',
 'ST300Q08JA':'Se interesan por lo que aprende','ST300Q09JA':'Hablan de sus estudios futuros',
 'ST300Q10JA':'Preguntan qué ha hecho hoy en clase'}


def build(output):
    g=pd.read_csv(output/'subgroup_changes.csv')
    n=pd.read_csv(output/'national_changes.csv')
    d=pd.read_csv(output/'composition_decomposition.csv')
    f=pd.read_csv(output/'family_support.csv')
    if len(g)!=747 or abs(n.set_index('domain').loc['READ','change']+22.95135969)>.001:
        raise ValueError('This reviewed narrative belongs to the 8 September 2026 snapshot; review claims before rebuilding with different data')
    title='Dónde cae España en PISA 2025'
    blocks=[]; charts=[]; tables=[]; datasets={}
    def prose(id,body,source=True):
        block={'id':id,'type':'markdown','body':body}
        if source: block['sourceId']='analysis'
        blocks.append(block)
    def table(id,title,frame,columns,sort):
        datasets[id]=json.loads(frame.to_json(orient='records'))
        tables.append({'id':id,'title':title,'dataset':id,'sourceId':'analysis',
            'defaultSort':{'field':sort,'direction':'asc'},
            'columns':[{'field':field,'label':label,'format':'number' if pd.api.types.is_numeric_dtype(frame[field]) else 'text'} for field,label in columns]})
        blocks.append({'id':id+'_block','type':'table','tableId':id})
    def chart(id,title,frame,category,value):
        datasets[id]=json.loads(frame.to_json(orient='records'))
        charts.append({'id':id,'title':title,'subtitle':'Cambio en puntos de lectura: 2025 menos 2022',
            'type':'bar','intent':'comparison','question':'¿Dónde es mayor el descenso en lectura?',
            'rationale':'Barras horizontales para comparar cambios por grupos; no es una serie temporal.',
            'dataset':id,'sourceId':'analysis','valueFormat':'number',
            'encodings':{'x':{'field':category,'type':'nominal','label':'Grupo'},
                         'y':{'field':value,'type':'quantitative','label':'Cambio en puntos'}},
            'options':{'orientation':'horizontal'},
            'palette':{'kind':'sequential','name':'blue'},'legend':{'show':False}})
        blocks.append({'id':id+'_block','type':'chart','chartId':id})
    prose('title','# '+title,False)
    prose('summary','''## Executive Summary

- **La caída no se explica principalmente por el cambio demográfico.** Sexo y origen representan 0,7 de los 23,0 puntos perdidos en lectura; el resto ocurre dentro de esos grupos. Al añadir los estudios familiares declarados, el componente de composición sube a 4,4 puntos, pero depende de una variable cuya distribución cambia mucho entre cuestionarios.
- **El cuartil socioeconómico alto cae especialmente en lectura: −33,0 puntos.** Dentro de él, destacan Comunitat Valenciana (−54,6) y País Vasco (−52,7). El alumnado de origen nativo del cuartil alto pierde 32,3 puntos y, por su tamaño, aporta 7,2 puntos al componente interno de la caída nacional.
- **Hay menos conversación familiar declarada, pero no una causa demostrada.** Hablar semanalmente de problemas escolares pasa del 60,3% al 50,5%. La cobertura de estas preguntas difiere mucho entre ciclos.

La conclusión es descriptiva: identifica dónde se concentra la bajada y descarta que una simple variación de la composición observada baste para explicarla. No identifica qué política, práctica familiar o cambio social la causó.''')
    prose('scope','''## Lectura pierde más que matemáticas y ciencias

Comparamos alumnos de 15 años escolarizados en España evaluados en **2025 frente a 2022**, no dos años consecutivos. Son dos muestras distintas: 30.800 registros en 2022 y 29.966 en el fichero público de 2025. Las medias incorporan pesos muestrales y los diez valores plausibles de cada materia.

La tabla muestra puntos PISA, no porcentajes ni años de aprendizaje. Las medias de 2025 reproducen, al redondear, 457 en matemáticas, 451 en lectura y 477 en ciencias.''')
    nt=n.copy();nt['materia']=nt.domain.map(DOMAINS)
    table('national','Resultados de España',nt.round(2),[('materia','Materia'),('mean2022','2022'),('mean2025','2025'),('change','Cambio')],'change')
    prose('mix','''## Entre el 81% y el 97% de la bajada lectora queda dentro de los grupos

La descomposición separa cambios en el peso de los grupos y cambios en su resultado. Con sexo y origen, **22,2 de 23,0 puntos** quedan dentro de los grupos (97%). Al añadir educación familiar declarada, quedan **18,6 puntos** (81%). En matemáticas, los componentes de composición son 1,0 y 4,7 puntos, respectivamente.

Estos son dos modelos descriptivos alternativos, no efectos que se puedan sumar. La versión con estudios familiares exige especial cautela: la proporción clasificada con padres de educación terciaria pasa del 72,0% al 61,3%, y cambian la codificación y la falta de respuesta. No podemos atribuir toda esa variación a un cambio real de las familias.

El origen migratorio por sí solo aporta **0,6 puntos** al cambio de composición en lectura y **1,1 en matemáticas**. Esto no significa que exista un efecto causal de la inmigración, ni una diferencia innata entre grupos.''')
    dt=d.groupby(['dimensions','domain'])[['composition','within']].sum().reset_index()
    dt=dt[dt.dimensions.isin(['sexo + origen','sexo + origen + educacion_familiar'])].copy()
    dt['materia']=dt.domain.map(DOMAINS);dt['modelo']=dt.dimensions.map({'sexo + origen':'Sexo y origen','sexo + origen + educacion_familiar':'Sexo, origen y estudios familiares'})
    table('decomposition','Componentes de la variación nacional',dt.round(2),[('modelo','Agrupación'),('materia','Materia'),('composition','Composición'),('within','Dentro de grupos')],'materia')
    prose('ses','''## No es una caída concentrada únicamente en familias desfavorecidas

El cuartil socioeconómico alto pierde **33,0 puntos en lectura**, frente a 15,1 en el cuartil bajo. Su descenso interno aporta **7,9 puntos**, alrededor del 34% de la caída nacional. La diferencia de evolución frente al resto supera la corrección por comparaciones múltiples.

Las barras comparan los cuatro cuartiles de posición socioeconómica dentro de España en cada ciclo. Q4 es el cuarto más favorecido y Q1 el menos favorecido, entre quienes tienen índice observado. **No son tramos fijos de renta** ni necesariamente las mismas familias.''')
    sg=g[g.dimensions.eq('nivel_socioeconomico') & g.domain.eq('READ') & g.group.isin(['Q1','Q2','Q3','Q4'])].sort_values('group')
    chart('ses_chart','Cambio lector por cuartil socioeconómico',sg.round(3),'group','change')
    prose('combinations','''## El cruce entre territorio y nivel alto señala dos focos claros

En el cuartil socioeconómico alto, Comunitat Valenciana pierde **54,6 puntos** de lectura y País Vasco **52,7**. Ambos cruces muestran una evolución peor que el resto tras ajustar las comparaciones múltiples. También cae con fuerza el alumnado de origen nativo del cuartil alto: **−32,3 puntos**, con una muestra amplia de 6.825 alumnos en 2025.

La tabla recoge combinaciones relevantes y el tamaño de muestra, no un ranking causal. Los grupos se solapan y sus contribuciones **no se suman**. El pequeño cruce de primera generación y Q4 tiene una caída estimada aún mayor (−58,6), pero solo 212 alumnos en 2025 y no supera el umbral ajustado del 5%; no lo trataría como el hallazgo principal.''')
    selections=[('region + nivel_socioeconomico','Comunidad Valenciana | Q4'),('region + nivel_socioeconomico','Basque Country | Q4'),('sexo + nivel_socioeconomico','No varón | Q4'),('sexo + nivel_socioeconomico','Varón | Q4'),('origen + nivel_socioeconomico','Origen nativo | Q4')]
    cg=pd.concat([g[g.dimensions.eq(dim)&g.group.eq(group)&g.domain.eq('READ')] for dim,group in selections]).copy()
    cg['grupo']=cg.group.str.replace('Basque Country','País Vasco').str.replace('Comunidad Valenciana','Comunitat Valenciana')
    table('crosses','Cruces demográficos: lectura',cg.round(3),[('grupo','Grupo'),('n2022','Muestra 2022'),('n2025','Muestra 2025'),('change','Cambio'),('q_vs_rest','p ajustado frente al resto')],'change')
    prose('regions','''## Comunitat Valenciana y País Vasco concentran una parte importante del descenso

En el conjunto del alumnado, Comunitat Valenciana baja **58,2 puntos en lectura** y País Vasco **47,2**. Su componente de descenso interno, ponderado por su tamaño, suma **8,5 puntos**, un 37% de la caída nacional. No es el efecto que tendría eliminar estos territorios: es una contribución contable al cambio.

Las barras muestran las seis mayores caídas estimadas entre los territorios que podemos publicar por separado. **Cataluña se excluye de este ranking**, siguiendo la advertencia de la OCDE sobre exclusiones; sus alumnos permanecen en las cifras nacionales. No todas las diferencias entre posiciones del ranking son estadísticamente distinguibles.''')
    rg=g[g.dimensions.eq('region') & g.domain.eq('READ')].sort_values('change').head(6).copy();rg['territorio']=rg.group.map(REGIONS)
    chart('regions_chart','Cambios lectores por territorio',rg.round(3),'territorio','change')
    prose('family','''## Baja el apoyo familiar declarado, sin demostrar que cause la caída

Hablar al menos semanalmente de los problemas escolares pasa de **60,3% a 50,5%**; preguntar qué ha hecho el alumno ese día, de **76,7% a 69,1%**. También baja el interés por lo aprendido, de 64,9% a 59,3%.

Son porcentajes entre quienes responden a cada pregunta. En 2022 faltan respuestas observadas para aproximadamente el 57% del peso muestral; en 2025, alrededor del 11%. En el archivo original de 2022, 14.624 de los 30.800 registros tienen «no aplicable» en la pregunta sobre problemas escolares. **No equivale a que esas familias no se interesasen por sus hijos.** La diferencia de administración/cobertura impide convertir este cambio directamente en puntos PISA explicados.''')
    fp=f.pivot(index='variable',columns='year',values='weekly_share').reset_index();fp['pregunta']=fp.variable.map(ITEMS);fp['2022_pct']=fp[2022]*100;fp['2025_pct']=fp[2025]*100;fp['cambio_pp']=fp['2025_pct']-fp['2022_pct']
    table('families','Conversación familiar semanal o diaria',fp[['pregunta','2022_pct','2025_pct','cambio_pp']].round(1),[('pregunta','Actividad'),('2022_pct','2022 (%)'),('2025_pct','2025 (%)'),('cambio_pp','Cambio (pp)')],'cambio_pp')
    prose('missing','''## Los cuestionarios incompletos merecen una investigación propia

El grupo sin índice socioeconómico observado pierde 73,3 puntos de lectura. Representa aproximadamente el 4,3% del alumnado ponderado en 2025 y su componente interno aporta unos 3,1 puntos a la caída nacional. **No es un perfil demográfico interpretable**: puede mezclar cambios de respuesta, selección y alumnos con situaciones muy distintas.

Por eso conservamos los datos faltantes como categoría visible, pero no los presentamos como una supuesta clase de familia. El contraste entre cuartiles es relativo a quienes tienen índice observado.''')
    prose('next','''## Qué conviene preguntar ahora

1. Dentro de Comunitat Valenciana y País Vasco, ¿se mantiene el patrón al ajustar simultáneamente por centro, lengua de la prueba, origen y nivel socioeconómico?
2. ¿Cuánto cambia la conclusión al restringir la comparación a cuestionarios y preguntas con cobertura verdaderamente equivalente?
3. ¿Qué mecanismos medibles —asistencia, prácticas de lectura, enseñanza, motivación o contexto de la prueba— acompañan la caída dentro de los grupos? Requerirían hipótesis y controles explícitos; no basta con encontrar una correlación.

La base ya conserva todas las variables originales de España de ambos ciclos para continuar estas preguntas sin limitarse a las columnas del histórico compacto.''',False)
    prose('limits','''## Límites que cambian la interpretación

- **No hay identificación causal:** son dos cortes transversales, no los mismos alumnos seguidos en el tiempo.
- Se usan 80 pesos replicados, Fay BRR y diez valores plausibles. Los intervalos de cambio guardados en CSV incluyen muestreo e imputación, pero no el error de enlace entre escalas. En ciencias, al añadir el error de enlace de 2,9 puntos indicado por la [guía de la OCDE](https://www.oecd.org/en/publications/pisa-2025-results-volume-i_73451bc5-en/full-report/reader-s-guide_0364240f.html), el intervalo aproximado es **−14,9 a +0,1**: no debe presentarse esa bajada como concluyente al 95%.
- Los contrastes de evolución de un grupo frente al resto cancelan el error común aditivo de enlace; se corrigen 747 comparaciones con Benjamini–Hochberg. Son hallazgos exploratorios, no pruebas confirmatorias de mecanismos.
- Se requieren al menos 100 alumnos y 10 centros en ambos ciclos para publicar un subgrupo. Las diferencias entre dos subgrupos concretos no se infieren solo de sus rankings.
- «No varón» corresponde a mujeres en 2022 y a mujeres/otra categoría en el indicador disponible de 2025; no es una comparación estricta solo de chicas. El campo anterior está vacío en el PUF español de 2025.
- El fichero público contiene 29.966 registros de España y 956 centros, frente a 29.967 alumnos en la nota publicada. No se ha determinado el motivo de esa diferencia de una observación; las medias redondeadas sí coinciden.
- Los resultados se basan en la versión descargada el 8 de septiembre de 2026. Los originales y registros individuales no se publican con el informe.''',False)
    source={'id':'analysis','label':'Cálculos propios sobre los PUF de la OCDE 2022 y 2025',
        'path':'Global/pisa/analysis/spain_cycle_change.py',
        'href':'https://github.com/victoriano/social-sciences-microdata/blob/main/Global/pisa/analysis/spain_cycle_change.py',
        'query':{'language':'python','engine':'python','sql':Path(__file__).with_name('spain_cycle_change.py').read_text(),'description':'Código Python ejecutable (no SQL): pesos finales, 80 réplicas BRR, diez PV; subgrupos y descomposición simétrica. Archivos agregados guardados junto al informe.',
                 'tables_used':['CY08MSP_STU_QQQ.SAV','CY09_MS_STU_PUF.sav'],
                 'filters':['CNT = ESP','assessment cycles 2022 and 2025'],
                 'executed_at':'2026-09-08T20:24:00Z'}}
    artifact={'surface':'report','manifest':{'version':1,'surface':'report','title':title,'blocks':blocks,'charts':charts,'tables':tables,'sources':[source]},
              'snapshot':{'version':1,'status':'ready','generatedAt':'2026-09-08T20:24:00Z','datasets':datasets},'sources':[source]}
    (output/'artifact.json').write_text(json.dumps(artifact,ensure_ascii=False,indent=2))
    # Supporting readable source; the selected report renderer owns presentation.
    narrative='\n\n'.join(b['body'] for b in blocks if b['type']=='markdown')
    (output/'analisis-pisa-2025.md').write_text(narrative+'\n',encoding='utf-8')
    (output/'report-notes.md').write_text('''Report audience: stakeholder; native report artifact. Required roles: title, Executive Summary, findings with evidence, next steps/open questions, limitations. Spanish used to match the user. Exact values use tables; SES/territorial comparisons use horizontal bars with direct category labels and a single blue root. Both charts share the comparison family intentionally; only two assessment cycles, so no interpolated trend. Full-width native blocks. Source CSVs retain counts, baseline/current scores, weighted shares, errors, and FDR values. Individual microdata excluded. Alternative demographic, SES and geographic contributions overlap and must not be summed. No figure or inference from the legacy PV1/unweighted archive is used.\n''')
    print(output/'artifact.json')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output_dir',type=Path)
    build(p.parse_args().output_dir)
