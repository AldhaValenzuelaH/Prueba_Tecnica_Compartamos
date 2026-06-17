#!/bin/bash
# Punto de entrada único del pipeline.
# Ejecuta cada notebook en orden: ingesta -> limpieza -> tablas -> graficos -> sql.
set -e

echo "Iniciando pipeline completo..."

jupyter nbconvert --to notebook --execute --inplace notebooks/01_ingesta.ipynb
echo "Paso 1 (Ingesta) completado."

jupyter nbconvert --to notebook --execute --inplace notebooks/02_limpieza.ipynb
echo "Paso 2 (Limpieza) completado."

jupyter nbconvert --to notebook --execute --inplace notebooks/03_tablas.ipynb
echo "Paso 3 (Tablas FACT/DIM) completado."

jupyter nbconvert --to notebook --execute --inplace notebooks/04_graficos.ipynb
echo "Paso 4 (Reporte) completado."

jupyter nbconvert --to notebook --execute --inplace notebooks/05_sql_preguntas.ipynb
echo "Paso 5 (SQL) completado."

echo "Pipeline completo ejecutado sin errores."