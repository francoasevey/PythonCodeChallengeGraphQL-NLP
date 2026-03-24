import strawberry

from data_service.services.csv_service import load_dataframe


@strawberry.type(description="Una interacción de producto en el dataset de e-commerce")
class ProductInteraction:
    date: str = strawberry.field(description="Fecha del evento (YYYYMMDD)")
    client_id: str = strawberry.field(description="ID del cliente")
    product_name: str = strawberry.field(description="Nombre del producto")
    brand: str = strawberry.field(description="Marca del producto")
    sku: str = strawberry.field(description="SKU del producto")
    category: str = strawberry.field(description="Categoría principal del producto")
    cart_additions: str = strawberry.field(description="Cantidad de veces agregado al carrito")
    cart_removals: str = strawberry.field(description="Cantidad de veces retirado del carrito")
    quantity_sold: str = strawberry.field(description="Cantidad de producto comprado")
    revenue: str = strawberry.field(description="Monto de ingreso por producto")
    product_detail_views: str = strawberry.field(description="Vistas al detalle del producto")
    page_views: str = strawberry.field(description="Visualizaciones de página")


@strawberry.type(description="Marca con su frecuencia de aparición en el dataset")
class BrandCount:
    brand: str
    count: int


def _to_interaction(row: dict) -> ProductInteraction:
    return ProductInteraction(
        date=row.get("id_tie_fecha_valor", ""),
        client_id=row.get("id_cli_cliente", ""),
        product_name=row.get("desc_ga_nombre_producto_1", ""),
        brand=row.get("desc_ga_marca_producto", ""),
        sku=row.get("desc_ga_sku_producto", ""),
        category=row.get("desc_categoria_prod_principal", ""),
        cart_additions=row.get("fc_agregado_carrito_cant", ""),
        cart_removals=row.get("fc_retirado_carrito_cant", ""),
        quantity_sold=row.get("fc_producto_cant", ""),
        revenue=row.get("fc_ingreso_producto_monto", ""),
        product_detail_views=row.get("fc_detalle_producto_cant", ""),
        page_views=row.get("fc_visualizaciones_pag_cant", ""),
    )


@strawberry.type
class Query:
    @strawberry.field(description="Lista paginada de interacciones de productos")
    def product_interactions(self, limit: int = 10, offset: int = 0) -> list[ProductInteraction]:
        df = load_dataframe()
        slice_ = df.iloc[offset: offset + limit]
        return [_to_interaction(r) for r in slice_.to_dict(orient="records")]

    @strawberry.field(description="Interacciones filtradas por categoría (búsqueda parcial)")
    def products_by_category(self, category: str, limit: int = 20) -> list[ProductInteraction]:
        df = load_dataframe()
        mask = df["desc_categoria_prod_principal"].str.contains(category, case=False, na=False)
        return [_to_interaction(r) for r in df[mask].head(limit).to_dict(orient="records")]

    @strawberry.field(description="Marcas ordenadas por frecuencia de aparición")
    def top_brands(self, limit: int = 10) -> list[BrandCount]:
        df = load_dataframe()
        counts = (
            df[~df["desc_ga_marca_producto"].isin(["", "No Aplica"])]
            ["desc_ga_marca_producto"]
            .value_counts()
            .head(limit)
        )
        return [BrandCount(brand=b, count=int(c)) for b, c in counts.items()]

    @strawberry.field(description="Interacciones filtradas por rango de fechas (formato YYYYMMDD)")
    def interactions_by_date_range(
        self, date_from: str, date_to: str, limit: int = 20
    ) -> list[ProductInteraction]:
        df = load_dataframe()
        mask = (df["id_tie_fecha_valor"] >= date_from) & (df["id_tie_fecha_valor"] <= date_to)
        return [_to_interaction(r) for r in df[mask].head(limit).to_dict(orient="records")]
