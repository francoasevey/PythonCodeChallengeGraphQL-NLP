import pandas as pd

from data_service.config import settings

_df_cache: pd.DataFrame | None = None


def load_dataframe() -> pd.DataFrame:
    global _df_cache
    if _df_cache is None:
        _df_cache = pd.read_csv(settings.csv_path, dtype=str)
        _df_cache = _df_cache.fillna("")
    return _df_cache


def build_nlp_context(df: pd.DataFrame) -> str:
    brands = (
        df[~df["desc_ga_marca_producto"].isin(["", "No Aplica"])]
        ["desc_ga_marca_producto"]
        .value_counts()
        .head(8)
        .to_dict()
    )
    categories = (
        df[df["desc_categoria_prod_principal"] != ""]
        ["desc_categoria_prod_principal"]
        .value_counts()
        .head(8)
        .to_dict()
    )
    top_products = (
        df[~df["desc_ga_nombre_producto_1"].isin(["", "No Aplica"])]
        ["desc_ga_nombre_producto_1"]
        .value_counts()
        .head(5)
        .index
        .tolist()
    )
    date_min = df["id_tie_fecha_valor"].min()
    date_max = df["id_tie_fecha_valor"].max()

    sample = df[
        ["id_tie_fecha_valor", "desc_ga_nombre_producto_1",
         "desc_ga_marca_producto", "desc_categoria_prod_principal",
         "fc_agregado_carrito_cant", "fc_producto_cant",
         "fc_ingreso_producto_monto"]
    ].head(5).to_markdown(index=False)

    return f"""
Eres un asistente que responde preguntas sobre un dataset de interacciones de e-commerce.

DESCRIPCIÓN DEL DATASET
- Total de filas: {len(df):,}
- Total de columnas: {len(df.columns)}
- Rango de fechas: {date_min} a {date_max} (formato YYYYMMDD)
- Clientes únicos: {df["id_cli_cliente"].nunique()}

COLUMNAS PRINCIPALES
- id_tie_fecha_valor: fecha del evento
- id_cli_cliente: ID del cliente
- desc_ga_nombre_producto_1: nombre del producto
- desc_ga_marca_producto: marca del producto
- desc_ga_sku_producto: SKU del producto
- desc_categoria_prod_principal: categoría principal del producto
- fc_agregado_carrito_cant: cantidad de veces que se agregó al carrito
- fc_retirado_carrito_cant: cantidad de veces que se retiró del carrito
- fc_producto_cant: cantidad de producto comprado
- fc_ingreso_producto_monto: monto de ingreso por producto
- fc_detalle_producto_cant: vistas de detalle del producto
- fc_visualizaciones_pag_cant: visualizaciones de página

TOP MARCAS (por frecuencia de aparición)
{brands}

TOP CATEGORÍAS (por frecuencia de aparición)
{categories}

TOP PRODUCTOS MÁS FRECUENTES
{top_products}

MUESTRA DE DATOS (5 filas)
{sample}

Respondé siempre en español, de forma clara y concisa. Si la pregunta no puede responderse con estos datos, indicalo.
""".strip()
