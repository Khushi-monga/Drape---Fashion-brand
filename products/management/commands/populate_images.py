import requests
import random
from django.core.files.base import ContentFile
from products.models import Product
from decouple import config

UNSPLASH_ACCESS_KEY = config("UNSPLASH_ACCESS_KEY")

# Get all products without images
products_without_images = Product.objects.filter(image='')

count = 0
for product in products_without_images:
    try:
        # Search using PRODUCT NAME for more variety
        search_term = product.name.lower()  # e.g., "Relaxed Fit Cotton T-Shirt"
        
        url = "https://api.unsplash.com/search/photos"
        params = {
            "query": search_term,
            "per_page": 30,  # Get 30 results
            "client_id": UNSPLASH_ACCESS_KEY,
        }
        
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        
        if data["results"]:
            # Pick a RANDOM result from the 30 (not always first one)
            image_data = random.choice(data["results"])
            image_url = image_data["urls"]["regular"]
            img_response = requests.get(image_url)
            
            filename = f"{product.slug}.jpg"
            product.image.save(filename, ContentFile(img_response.content), save=True)
            count += 1
            print(f"✓ {product.name}")
        else:
            print(f"✗ No images found for {product.name}")
            
    except Exception as e:
        print(f"✗ Error for {product.name}: {str(e)}")

print(f"\nDone! Downloaded {count} images.")