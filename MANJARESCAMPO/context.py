from .mock_data import MOCK_SITE_CONFIG, get_mock_categories

def app_context(request):
    """Context processor global para toda la aplicación (MOCK MODE)."""
    
    # 1. Configuración del Sitio Mock
    config_data = {
        "WHATSAPP_NUMBER": MOCK_SITE_CONFIG["WHATSAPP_NUMBER"],
        "BUSINESS_HOURS": MOCK_SITE_CONFIG["BUSINESS_HOURS"],
        "SOCIAL_FACEBOOK_URL": MOCK_SITE_CONFIG["SOCIAL_FACEBOOK_URL"],
        "SOCIAL_INSTAGRAM_URL": MOCK_SITE_CONFIG["SOCIAL_INSTAGRAM_URL"],
        "WELCOME_MESSAGE": MOCK_SITE_CONFIG["WELCOME_MESSAGE"],
        "ORDER_WA_PREFIX": MOCK_SITE_CONFIG["ORDER_WA_PREFIX"],
        "DEFAULT_SHIPPING_COST": MOCK_SITE_CONFIG["DEFAULT_SHIPPING_COST"],
        "FREE_SHIPPING_OVER": MOCK_SITE_CONFIG["FREE_SHIPPING_OVER"],
    }

    # 2. Resumen del Carrito
    try:
        from orders.cart import Cart
        cart = Cart(request)
        cart_count = len(cart)
        cart_total = cart.get_total_price()
    except Exception:
        cart_count = 0
        cart_total = 0
    
    # 3. Datos Globales Mock
    ctx = {
        "cart_count": cart_count,
        "cart_total": cart_total,
        "categories": get_mock_categories(),
        "today_now": True
    }
    
    ctx.update(config_data)
    return ctx
