from django.shortcuts import render
from .models import Product
from django.conf import settings
from django.utils.http import urlencode

def catalog(request):
    products = Product.objects.filter(available=True).order_by("-created_at")
    wa_number = getattr(settings, "WHATSAPP_NUMBER", "")
    items = []
    for p in products:
        text = f"Hola, quiero comprar 1 x {p.name} por ${p.price}"
        wa_link = f"https://wa.me/{wa_number}?{urlencode({'text': text})}" if wa_number else ""
        items.append(
            {
                "id": p.id,
                "name": p.name,
                "price": p.price,
                "description": p.description,
                "image": p.image.url if getattr(p, 'image', None) else "",
                "wa_link": wa_link,
            }
        )
    return render(request, "products/catalog.html", {"products": items})

# Create your views here.
