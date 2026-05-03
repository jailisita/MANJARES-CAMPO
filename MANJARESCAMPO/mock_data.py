from django.contrib.auth.models import User
from products.models import Category, Product
from inventory.models import SiteConfiguration
from orders.models import ShippingZone
from decimal import Decimal

def load_mock_data():
    from django.db import connection
    from django.core.management import call_command
    
    # Crear tablas si no existen
    from django.core.management import execute_from_command_line
    from django.conf import settings
    
    # Verificar si ya hay datos
    if Category.objects.exists():
        return
    
    # Crear superusuario
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@manjares.com',
            password='admin123'
        )
    
    # Crear usuario de prueba
    if not User.objects.filter(username='cliente_web').exists():
        User.objects.create_user(
            username='cliente_web',
            email='cliente@test.com',
            is_active=False
        )
    
    # Crear configuración del sitio
    if not SiteConfiguration.objects.exists():
        SiteConfiguration.objects.create(
            whatsapp_number="573001234567",
            business_hours="Lun-Sáb 8:00-18:00 · Dom 8:00-13:00",
            facebook_url="https://facebook.com/manjarescampo",
            instagram_url="https://instagram.com/manjarescampo",
            welcome_message="¡Hola! Bienvenido a MANJARES DEL CAMPO. ¿En qué podemos ayudarte?",
            order_wa_prefix="Hola!, quiero hacer este pedido de Manjares del Campo",
            default_shipping_cost=10000,
            free_shipping_threshold=100000
        )
    
    # Crear categorías
    categorias = [
        ("Frutas Frescas",),
        ("Verduras",),
        ("Huevos y Lácteos",),
        ("Granos y Cereales",),
        ("Miel y Artesanales",),
        ("Combos y Canastas",),
    ]
    
    cats = {}
    for nome in categorias:
        cat, _ = Category.objects.get_or_create(name=nome[0])
        cats[nome[0]] = cat
    
    # Productos de prueba
    productos = [
        {"name": "Fresas Frescas", "description": "Fresas orgánicas cultivadas en la región", "price": 8000, "unit": "kg", "stock": 50, "category": cats["Frutas Frescas"]},
        {"name": "Mango Tommy", "description": "Mango maduro listo para consumir", "price": 5000, "unit": "kg", "stock": 30, "category": cats["Frutas Frescas"]},
        {"name": "Banano Criollo", "description": "Banano orgánico de_platanera local", "price": 2500, "unit": "kg", "stock": 100, "category": cats["Frutas Frescas"]},
        {"name": "Papaya", "description": "Papaya madura, rica en vitaminas", "price": 4500, "unit": "kg", "stock": 25, "category": cats["Frutas Frescas"]},
        {"name": "Aguacate Hass", "description": "Aguacate premium de alta calidad", "price": 6000, "unit": "kg", "stock": 40, "category": cats["Frutas Frescas"]},
        
        {"name": "Lechuga Romana", "description": "Lechuga fresca de nuestra Huerta", "price": 3500, "unit": "unidad", "stock": 60, "category": cats["Verduras"]},
        {"name": "Tomate Chonto", "description": "Tomate fresco de行者", "price": 4000, "unit": "kg", "stock": 45, "category": cats["Verduras"]},
        {"name": "Zanahoria", "description": "Zanahorias frescas y crujientes", "price": 3000, "unit": "kg", "stock": 70, "category": cats["Verduras"]},
        {"name": "Cebolla Cabezona", "description": "Cebolla fresca de行者", "price": 3500, "unit": "kg", "stock": 55, "category": cats["Verduras"]},
        {"name": "Pimentón", "description": "Pimentón verde fresco", "price": 4500, "unit": "kg", "stock": 35, "category": cats["Verduras"]},
        
        {"name": "Huevos Campestres", "description": "Huevos de gallinas criadas en campo", "price": 500, "unit": "unidad", "stock": 200, "category": cats["Huevos y Lácteos"]},
        {"name": "Leche Fresca", "description": "Leche directamente de la Finca", "price": 4500, "unit": "l", "stock": 30, "category": cats["Huevos y Lácteos"]},
        {"name": "Queso Fresco", "description": "Queso campesino artesanal", "price": 12000, "unit": "kg", "stock": 20, "category": cats["Huevos y Lácteos"]},
        {"name": "Yogurt Natural", "description": "Yogurt sin preservantes", "price": 6000, "unit": "l", "stock": 25, "category": cats["Huevos y Lácteos"]},
        
        {"name": "Arroz Integral", "description": "Arroz integral orgánico", "price": 5500, "unit": "kg", "stock": 80, "category": cats["Granos y Cereales"]},
        {"name": "Lentejas", "description": "Lentejas selected de行者", "price": 6000, "unit": "kg", "stock": 50, "category": cats["Granos y Cereales"]},
        {"name": "Frijol Cabecero", "description": "Frijol colombiano selecto", "price": 7000, "unit": "kg", "stock": 45, "category": cats["Granos y Cereales"]},
        
        {"name": "Miel de Abeja", "description": "Miel 100% pura de行者", "price": 18000, "unit": "kg", "stock": 15, "category": cats["Miel y Artesanales"]},
        {"name": "Jalea Real", "description": "Jalea real orgánica", "price": 25000, "unit": "kg", "stock": 10, "category": cats["Miel y Artesanales"]},
        
        {"name": "Canasta Familiar", "description": "Canasta con productos selected para 4 personas", "price": 85000, "unit": "combo", "stock": 10, "category": cats["Combos y Canastas"], "is_on_offer": True, "discount_percentage": 10},
        {"name": "Combo Frutas", "description": "Variedad de frutas de temporada", "price": 45000, "unit": "combo", "stock": 15, "category": cats["Combos y Canastas"]},
    ]
    
    for p in productos:
        prod = Product.objects.create(
            name=p["name"],
            description=p.get("description", ""),
            price=Decimal(str(p["price"])),
            unit=p.get("unit", "unidad"),
            stock=p.get("stock", 10),
            min_stock=5,
            category=p.get("category"),
            available=True,
            is_on_offer=p.get("is_on_offer", False),
            discount_percentage=p.get("discount_percentage", 0)
        )
        if prod.is_on_offer:
            prod.save()  # Calcula el offer_price
    
    # Zonas de envío
    zonas = [
        ("Centro", 5000, "Zona céntrica de la ciudad"),
        ("Norte", 8000, "Barrios del norte"),
        ("Sur", 8000, "Barrios del sur"),
        ("Occidente", 10000, "Zona occidental"),
        ("Arena", 12000, "Zona de arena y periferia"),
    ]
    
    for nome, costo, notas in zonas:
        ShippingZone.objects.get_or_create(
            name=nome,
            defaults={"cost": costo, "notes": notas, "active": True}
        )
    
    print("Datos de prueba cargados correctamente")