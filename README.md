# Prueba Técnica - Practicante Data Engineer

Pipeline de datos end-to-end que ingiere, limpia y transforma datos de 
clientes, productos y pedidos, siguiendo una arquitectura de capas 
(RAW → STAGE → ANALYTICS) sobre una base de datos local DuckDB.

## Stack utilizado

- **Python 3.9** + Pandas para manipulación y limpieza de datos
- **DuckDB** como base de datos local (On-Premise)
- **Seaborn / Matplotlib** para visualizaciones
- **Jupyter Notebooks** como entorno de desarrollo y entregable
- **Git** para control de versiones

## Estructura del proyecto
```
Prueba_Tecnica_Compartamos/

├── data/raw/              # CSVs originales (no versionados en Git)

├── notebooks/

│   ├── 01_ingesta.ipynb

│   ├── 02_limpieza.ipynb

│   ├── 03_tablas.ipynb

│   ├── 04_graficos.ipynb

│   └── 05_sql_preguntas.ipynb

├── src/seguridad.py        # Hashing y enmascaramiento de PII

├── run.sh                  # Punto de entrada unico del pipeline

├── lakehouse.duckdb

├── .gitignore

└── README.md
```

## Cómo ejecutar el proyecto

```bash
python3 -m venv venv
source venv/bin/activate
pip install pandas duckdb seaborn matplotlib jupyter

# Pipeline completo con un solo comando:
chmod +x run.sh
./run.sh

# O alternativamente, ejecutar los notebooks en orden: 01 -> 02 -> 03 -> 04 -> 05
```

## Arquitectura de capas

- **RAW**: datos originales tal como llegan, sin transformación.
- **STAGE**: datos limpios (sin duplicados, sin nulos totales, tipos 
  correctos, fechas normalizadas, valores inválidos tratados).
- **ANALYTICS**: tablas finales DIM_CLIENTE, DIM_PRODUCTO y FACT_VENTAS, 
  listas para consumo directo.

## Decisiones de limpieza relevantes

- **Fechas con separadores mixtos**: el dataset usa un mismo orden de fecha 
  (año-mes-día) pero con separadores inconsistentes (`-`, `.`, `/`). Se 
  normalizó reemplazando los separadores antes de parsear con un formato 
  único, evitando pérdida de datos válidos.
- **País único (Colombia)**: la columna `country` tenía variantes ("Col.", 
  "Colombia") representando el mismo valor; se estandarizó a "COLOMBIA".
- **Supplier con formato flexible**: se reconoce el patrón "PROVEEDOR 
  [LETRA]" sin importar mayúsculas, espacios o guiones bajos (ej: 
  "ProveedorA", "proveedor_a" → "PROVEEDOR A").
- **Quantity inválido recalculado**: cuando `quantity` era ≤0 o nulo, se 
  recalculó como `total_amount_usd / unit_price_usd`, en lugar de 
  descartar el registro.
- **Corrección de ship_date**: se interpretó que un `ship_date` anterior al 
  `order_date` es la condición lógicamente inválida (no se puede enviar 
  algo antes de pedirlo), y se marcó como NULL en ese caso.
- **Integridad referencial**: los pedidos cuyo `customer_id` o `product_id` 
  no existen en las tablas limpias de clientes/productos fueron excluidos.

## Esquema de la capa ANALYTICS

### DIM_CLIENTE
| Columna | Tipo | Descripción |
|---|---|---|
| customer_id | INTEGER | Identificador único del cliente |
| first_name | VARCHAR | Nombre del cliente |
| last_name | VARCHAR | Apellido del cliente |
| email | VARCHAR | Correo electrónico |
| phone | VARCHAR | Teléfono de contacto |
| city | VARCHAR | Ciudad de residencia |
| country | VARCHAR | País (único valor: Colombia) |
| age | INTEGER | Edad del cliente |
| registration_date | DATE | Fecha de registro |
| loyalty_tier | VARCHAR | Nivel de fidelidad |

### DIM_PRODUCTO
| Columna | Tipo | Descripción |
|---|---|---|
| product_id | INTEGER | Identificador único del producto |
| product_name | VARCHAR | Nombre del producto |
| category | VARCHAR | Categoría del producto |
| price_usd | DOUBLE | Precio de venta en USD |
| cost_usd | DOUBLE | Costo del producto en USD |
| stock_units | DOUBLE | Unidades en stock |
| supplier | VARCHAR | Proveedor (formato "PROVEEDOR [LETRA]") |
| active | BOOLEAN | Indica si el producto está activo |

### FACT_VENTAS
| Columna | Tipo | Descripción |
|---|---|---|
| order_id | INTEGER | Identificador único del pedido |
| customer_id | INTEGER | FK a DIM_CLIENTE |
| product_id | INTEGER | FK a DIM_PRODUCTO |
| quantity | INTEGER | Cantidad de unidades pedidas |
| unit_price_usd | DOUBLE | Precio unitario al momento de la venta |
| total_amount_usd | DOUBLE | Monto total del pedido |
| discount_pct | DOUBLE | Porcentaje de descuento aplicado |
| order_date | DATE | Fecha del pedido |
| ship_date | DATE | Fecha de envío |
| status | VARCHAR | Estado del pedido |
| payment_method | VARCHAR | Método de pago |

## Protección de datos sensibles (PII)

Columnas identificadas como datos personales: `first_name`, `last_name`, 
`email`, `phone`, `age` (en DIM_CLIENTE), y `credit_card_last4` (asociado 
a las transacciones en FACT_VENTAS).

- **Hashing (SHA-256)** aplicado a `email`, disponible en la tabla 
  `secure_cliente`.
- **Enmascaramiento** aplicado a `credit_card_last4` (formato 
  `****-****-****-XXXX`), disponible en la tabla `secure_ventas`.

## Re-procesamiento e idempotencia

El pipeline usa `CREATE OR REPLACE TABLE` en cada capa, permitiendo 
re-ejecutar el proceso completo sin generar duplicados. Si se agregan 
registros nuevos a los CSV de origen, el siguiente `./run.sh` los 
incorpora automáticamente.

## Autor

Aldhair Valenzuela Huillcaya