"""
Script de seguridad: identifica y protege datos sensibles (PII).

Columnas PII identificadas:
- En DIM_CLIENTE: first_name, last_name, email, phone, age
- En FACT_VENTAS: credit_card_last4

Técnicas aplicadas:
- HASHING (SHA-256) sobre 'email' (dim_cliente): transformación irreversible.
- ENMASCARAMIENTO sobre 'credit_card_last4' (fact_ventas): se exponen
  solo los últimos 4 dígitos.
"""
import hashlib
import duckdb
import pandas as pd


def hashear_sha256(valor):
    if pd.isna(valor):
        return None
    return hashlib.sha256(str(valor).encode("utf-8")).hexdigest()


def enmascarar_tarjeta(valor):
    if pd.isna(valor):
        return None
    return "****-****-****-" + str(valor)[-4:]


def proteger_datos(con):
    # Clientes: hasheamos el email
    df_cli = con.execute("SELECT * FROM dim_cliente").df()
    df_cli["email_hash"] = df_cli["email"].apply(hashear_sha256)
    df_cli = df_cli.drop(columns=["email"])
    con.execute("CREATE OR REPLACE TABLE secure_cliente AS SELECT * FROM df_cli")

    # Ventas: enmascaramos la tarjeta (viene de stage_orders, no de fact_ventas)
    df_ventas = con.execute("SELECT order_id, customer_id, credit_card_last4 FROM stage_orders").df()
    df_ventas["credit_card_masked"] = df_ventas["credit_card_last4"].apply(enmascarar_tarjeta)
    df_ventas = df_ventas.drop(columns=["credit_card_last4"])
    con.execute("CREATE OR REPLACE TABLE secure_ventas AS SELECT * FROM df_ventas")

    print("Tablas 'secure_cliente' y 'secure_ventas' creadas con datos protegidos.")
    return df_cli, df_ventas


if __name__ == "__main__":
    con = duckdb.connect("notebooks/lakehouse.duckdb")
    proteger_datos(con)
    con.close()