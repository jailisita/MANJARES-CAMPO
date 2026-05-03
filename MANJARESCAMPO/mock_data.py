from decimal import Decimal

# Mock Categories
MOCK_CATEGORIES = [
    {"id": 1, "name": "Frutas y Verduras"},
    {"id": 2, "name": "Lácteos y Huevos"},
    {"id": 3, "name": "Cárnicos"},
    {"id": 4, "name": "Panadería"},
]

# Mock Products
# Attributes: id, name, description, price, unit, stock, min_stock, category_id, image_url, is_on_offer, discount_percentage, offer_price, available
MOCK_PRODUCTS = [
    {
        "id": 1,
        "name": "Tomate Chonto",
        "description": "Tomate fresco de la región, ideal para ensaladas.",
        "price": Decimal("3500.00"),
        "unit": "libra",
        "stock": 50,
        "category_id": 1,
        "image_url": "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?auto=format&fit=crop&q=80&w=400",
        "is_on_offer": False,
        "discount_percentage": 0,
        "offer_price": None,
        "available": True,
    },
    {
        "id": 2,
        "name": "Leche Entera",
        "description": "Leche fresca pasteurizada, bolsa de 1 litro.",
        "price": Decimal("4200.00"),
        "unit": "l",
        "stock": 20,
        "category_id": 2,
        "image_url": "https://images.unsplash.com/photo-1563636619-e910bd493996?auto=format&fit=crop&q=80&w=400",
        "is_on_offer": True,
        "discount_percentage": 10,
        "offer_price": Decimal("3780.00"),
        "available": True,
    },
    {
        "id": 3,
        "name": "Queso Campesino",
        "description": "Queso fresco artesanal, bloque de 500g.",
        "price": Decimal("8500.00"),
        "unit": "unidad",
        "stock": 15,
        "category_id": 2,
        "image_url": "https://images.unsplash.com/photo-1552767059-ce182ead6c1b?auto=format&fit=crop&q=80&w=400",
        "is_on_offer": False,
        "discount_percentage": 0,
        "offer_price": None,
        "available": True,
    },
    {
        "id": 4,
        "name": "Manzana Roja",
        "description": "Manzana dulce y crujiente, importada.",
        "price": Decimal("2500.00"),
        "unit": "unidad",
        "stock": 100,
        "category_id": 1,
        "image_url": "https://images.unsplash.com/photo-1560806887-1e4cd0b6bccb?auto=format&fit=crop&q=80&w=400",
        "is_on_offer": True,
        "discount_percentage": 15,
        "offer_price": Decimal("2125.00"),
        "available": True,
    },
    {
        "id": 5,
        "name": "Pechuga de Pollo",
        "description": "Pechuga fresca por kilogramo.",
        "price": Decimal("18000.00"),
        "unit": "kg",
        "stock": 10,
        "category_id": 3,
        "image_url": "https://images.unsplash.com/photo-1604503468506-a8da13d82791?auto=format&fit=crop&q=80&w=400",
        "is_on_offer": False,
        "discount_percentage": 0,
        "offer_price": None,
        "available": True,
    },
]

# Configuración del Sitio Mock
MOCK_SITE_CONFIG = {
    "WHATSAPP_NUMBER": "573001234567",
    "BUSINESS_HOURS": "Lun-Sáb 8:00-18:00 · Dom 8:00-13:00",
    "SOCIAL_FACEBOOK_URL": "https://facebook.com/manjaresdelcampo",
    "SOCIAL_INSTAGRAM_URL": "https://instagram.com/manjaresdelcampo",
    "WELCOME_MESSAGE": "¡Hola! Bienvenido a Manjares del Campo. ¿En qué podemos ayudarte?",
    "ORDER_WA_PREFIX": "Hola, vengo de la web y quiero hacer este pedido:",
    "DEFAULT_SHIPPING_COST": 10000,
    "FREE_SHIPPING_OVER": 100000,
}

class MockObject:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
    
    def __str__(self):
        return getattr(self, "name", "MockObject")

    @property
    def wa_link(self):
        from urllib.parse import urlencode
        wa_number = MOCK_SITE_CONFIG["WHATSAPP_NUMBER"]
        price = getattr(self, "offer_price", None) or getattr(self, "price", 0)
        text = f"Hola, quiero comprar 1 x {getattr(self, 'name', '')} por ${price}"
        return f"https://wa.me/{wa_number}?{urlencode({'text': text})}"

def get_mock_categories():
    return [MockObject(**c) for c in MOCK_CATEGORIES]

def get_mock_products():
    return [MockObject(**p) for p in MOCK_PRODUCTS]