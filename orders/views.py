from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.conf import settings
from django.utils.http import urlencode
from decimal import Decimal
from products.models import Product
from .models import ShippingZone, Order, OrderItem
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from inventory.models import SiteConfiguration
from .cart import Cart

# --- FUNCIONES DE AYUDA ---

def _get_shipping_cost(total_after_discount, shipping_opts):
    """Calcula el costo de envío basado en reglas de negocio."""
    method = shipping_opts.get('method', 'delivery')
    if method == 'pickup':
        return Decimal("0")
    
    config = SiteConfiguration.objects.first()
    default_cost = config.default_shipping_cost if config else getattr(settings, "DEFAULT_SHIPPING_COST", 10000)
    free_threshold = config.free_shipping_threshold if config else getattr(settings, "FREE_SHIPPING_OVER", 100000)
    
    zone_id = shipping_opts.get('zone_id')
    cost = Decimal(str(default_cost))
    
    if zone_id:
        try:
            zone = ShippingZone.objects.get(id=int(zone_id), active=True)
            cost = Decimal(str(zone.cost))
        except (ShippingZone.DoesNotExist, ValueError, TypeError):
            pass
            
    # Umbral de envío gratis
    if total_after_discount >= Decimal(str(free_threshold)):
        return Decimal("0")
        
    return cost

from .cart import Cart

# --- VISTAS PÚBLICAS ---

def cart_view(request):
    """Vista principal del carrito con toda la lógica de cálculo y persistencia en sesión."""
    cart = Cart(request)
    items = list(cart)
    total = cart.get_total_price()
    
    # Descuento (opcional, configurable en settings)
    discount_pct = Decimal(str(getattr(settings, "DISCOUNT_PERCENT", 0)))
    discount = (total * (discount_pct / Decimal("100"))).quantize(Decimal("1."))
    
    # Configuración
    shipping_opts = request.session.get("shipping", {"method": "delivery", "zone_id": None, "address": ""})
    shipping_cost = _get_shipping_cost(total - discount, shipping_opts)
    
    grand_total = total - discount + shipping_cost
    
    ctx = {
        "items": items,
        "total": total,
        "discount": discount,
        "shipping": shipping_cost,
        "grand_total": grand_total,
        "shipping_opts": shipping_opts,
        "zones": ShippingZone.objects.filter(active=True),
    }
    return render(request, "orders/cart.html", ctx)

@require_POST
def checkout_whatsapp(request):
    """Crea la orden en la base de datos y redirige a WhatsApp."""
    cart = Cart(request)
    items = list(cart)
    if not items:
        return redirect('catalog')

    # 1. Calcular totales
    total = cart.get_total_price()
    discount_pct = Decimal(str(getattr(settings, "DISCOUNT_PERCENT", 0)))
    discount = (total * (discount_pct / Decimal("100"))).quantize(Decimal("1."))
    shipping_opts = request.session.get("shipping", {"method": "delivery", "zone_id": None, "address": ""})
    shipping_cost = _get_shipping_cost(total - discount, shipping_opts)
    grand_total = total - discount + shipping_cost

    # 2. Manejo de usuario
    if request.user.is_authenticated:
        user = request.user
    else:
        user, _ = User.objects.get_or_create(username='cliente_web', defaults={'is_active': False})

    # 3. Crear la Orden
    order = Order.objects.create(
        customer=user,
        status='pending',
        total=grand_total,
        delivery_method=shipping_opts.get('method', 'delivery'),
        address=shipping_opts.get('address', '')
    )

    # 4. Crear los Items de la Orden
    for item in items:
        OrderItem.objects.create(
            order=order,
            product=item['product'],
            quantity=item['quantity'],
            price=item['price']
        )

    # 5. Configuración de WhatsApp y Mensaje
    config = SiteConfiguration.objects.first()
    wa_number = config.whatsapp_number if config else getattr(settings, "WHATSAPP_NUMBER", "")
    wa_prefix = config.order_wa_prefix if config else "Hola!, quiero hacer este pedido"
    
    wa_msg = f"{wa_prefix}:\n\n"
    for i in items:
        wa_msg += f"- {i['quantity']} {i['product'].get_unit_display()} x {i['product'].name} = ${i['total_price']}\n"
    wa_msg += f"\nTotal: ${grand_total}\n"
    
    delivery_label = "Domicilio" if shipping_opts.get('method') == 'delivery' else "Recoger"
    wa_msg += f"Entrega: {delivery_label}\n"
    
    if shipping_opts.get('method') == 'delivery':
        zone_id = shipping_opts.get('zone_id')
        if zone_id:
            try:
                zone = ShippingZone.objects.get(id=int(zone_id))
                wa_msg += f"Zona: {zone.name} (+${zone.cost})\n"
            except (ShippingZone.DoesNotExist, ValueError, TypeError):
                pass
        if shipping_opts.get('address'):
            wa_msg += f"Dirección: {shipping_opts['address']}\n"
    
    wa_msg += f"\n(Orden: #{order.id})"
    
    wa_link = f"https://wa.me/{wa_number}?{urlencode({'text': wa_msg})}" if wa_number else ""

    # 6. Limpiar carrito y sesión de orden
    cart.clear()
    if 'active_order_id' in request.session:
        del request.session['active_order_id']

    if wa_link:
        return redirect(wa_link)
    return redirect('catalog')

@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, available=True)
    cart = Cart(request)
    try:
        qty = int(request.POST.get("qty", 1))
    except (ValueError, TypeError):
        qty = 1
    
    cart.add(product, quantity=qty)
    return redirect("cart_view")

@require_POST
def update_cart_item(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart(request)
    try:
        qty = int(request.POST.get("qty", 1))
        if qty > 0:
            cart.add(product, quantity=qty, override_quantity=True)
        else:
            cart.remove(product)
    except (ValueError, TypeError):
        pass
    return redirect("cart_view")

def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart(request)
    cart.remove(product)
    return redirect("cart_view")

@require_POST
def set_shipping_options(request):
    method = request.POST.get("method", "delivery")
    zone_id = request.POST.get("zone_id")
    address = request.POST.get("address", "")
    request.session["shipping"] = {
        "method": method, 
        "zone_id": zone_id, 
        "address": address
    }
    request.session.modified = True
    return redirect("cart_view")

@staff_member_required(login_url='login')
def admin_shipping_zones(request):
    zones = ShippingZone.objects.all()
    if request.method == "POST":
        name = request.POST.get("name")
        cost = request.POST.get("cost", 0)
        notes = request.POST.get("notes", "")
        if name:
            ShippingZone.objects.create(name=name, cost=cost, notes=notes)
            return redirect("admin_shipping_zones")
            
    return render(request, "orders/admin_shipping_zones.html", {"zones": zones})

@staff_member_required(login_url='login')
def admin_delete_zone(request, zone_id):
    zone = get_object_or_404(ShippingZone, id=zone_id)
    zone.delete()
    return redirect("admin_shipping_zones")

@staff_member_required(login_url='login')
def admin_toggle_zone(request, zone_id):
    zone = get_object_or_404(ShippingZone, id=zone_id)
    zone.active = not zone.active
    zone.save()
    return redirect("admin_shipping_zones")

def quick_buy_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, available=True)
    config = SiteConfiguration.objects.first()
    wa_number = config.whatsapp_number if config else ""
    text = f"Hola, quiero comprar 1 x {product.name} por ${product.price}"
    link = f"https://wa.me/{wa_number}?{urlencode({'text': text})}" if wa_number else "/"
    return redirect(link)

# --- VISTAS ADMINISTRATIVAS ---

@staff_member_required(login_url='login')
def admin_orders_list(request):
    query = request.GET.get('q')
    orders = Order.objects.all().order_by('-created_at')
    
    if query:
        if query.startswith('#'):
            query = query[1:]
        try:
            orders = orders.filter(id=int(query))
        except ValueError:
            # Si no es un número, podríamos buscar por cliente o teléfono si fuera necesario
            pass
            
    return render(request, 'orders/admin_orders_list.html', {'orders': orders, 'search_query': query})

@staff_member_required(login_url='login')
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    items = OrderItem.objects.filter(order=order)
    return render(request, 'orders/admin_order_detail.html', {'order': order, 'items': items})

@staff_member_required(login_url='login')
@require_POST
def admin_update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    status = request.POST.get('status')
    if status in dict(Order.STATUS_CHOICES):
        order.status = status
        order.save()
    return redirect('admin_order_detail', order_id=order.id)

@staff_member_required(login_url='login')
def order_invoice_pdf(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    items = OrderItem.objects.filter(order=order).select_related("product")
    try:
        from fpdf import FPDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, f"Factura MANJARES DEL CAMPO - Pedido #{order.id}", ln=True)
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 8, f"Fecha: {order.created_at.strftime('%Y-%m-%d %H:%M')}", ln=True)
        pdf.cell(0, 8, f"Cliente: {order.customer.username}", ln=True)
        if order.address:
            pdf.multi_cell(0, 8, f"Dirección: {order.address}")
        pdf.ln(2)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(100, 8, "Producto", 1)
        pdf.cell(30, 8, "Cantidad", 1, align="R")
        pdf.cell(60, 8, "Subtotal", 1, ln=True, align="R")
        pdf.set_font("Arial", "", 11)
        for it in items:
            subtotal = it.quantity * it.price
            pdf.cell(100, 8, it.product.name, 1)
            pdf.cell(30, 8, str(it.quantity), 1, align="R")
            pdf.cell(60, 8, f"${subtotal}", 1, ln=True, align="R")
        pdf.ln(2)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(130, 8, "Total", 1)
        pdf.cell(60, 8, f"${order.total}", 1, ln=True, align="R")
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="factura_{order.id}.pdf"'
        response.write(pdf.output(dest='S').encode('latin-1'))
        return response
    except Exception:
        return render(request, "orders/invoice_fallback.html", {"order": order, "items": items})

@staff_member_required
def admin_orders_reports_monthly(request):
    from django.db.models import Sum
    now = timezone.now()
    month_orders = Order.objects.filter(created_at__year=now.year, created_at__month=now.month)
    total_sales = month_orders.aggregate(total=Sum('total'))['total'] or Decimal("0")
    
    top_products = (
        OrderItem.objects.filter(order__created_at__year=now.year, order__created_at__month=now.month)
        .values("product__name")
        .annotate(qty=Sum("quantity"))
        .order_by("-qty")[:10]
    )

    try:
        from fpdf import FPDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, f"REPORTE MENSUAL - {now.strftime('%B %Y').upper()}", ln=True, align='C')
        pdf.ln(10)
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(160, 10, "TOTAL VENTAS DEL MES", 0)
        pdf.cell(30, 10, f"${total_sales}", 0, ln=True, align="R")
        
        pdf.ln(10)
        pdf.cell(0, 10, "PRODUCTOS MÁS VENDIDOS", ln=True)
        pdf.set_font("Arial", "", 11)
        for p in top_products:
            pdf.cell(130, 8, p["product__name"], 1)
            pdf.cell(60, 8, str(p["qty"]), 1, ln=True, align="C")

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="Reporte_{now.strftime("%m_%Y")}.pdf"'
        response.write(pdf.output(dest='S').encode('latin-1'))
        return response
    except Exception:
        return render(request, "orders/report_fallback.html", {"orders": month_orders, "total": total_sales, "now": now})
