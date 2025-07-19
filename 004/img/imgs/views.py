from django.shortcuts import render
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core import signing
from django.urls import reverse
from .models import UploadedImage
from .utils import compress_image
import os
import uuid

@csrf_exempt
def upload_view(request):
    if request.method == 'GET':
        return render(request, 'upload.html') 
        
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        
        # Validasi file
        if not image.content_type.startswith('image/'):
            return JsonResponse({'error': 'File bukan gambar'}, status=400)
        
        if image.size > 5 * 1024 * 1024:  # 5MB
            return JsonResponse({'error': 'Ukuran file maksimal 5MB'}, status=400)
        
        # Simpan file asli
        fs = FileSystemStorage()
        original_name = image.name
        original_ext = os.path.splitext(original_name)[1]
        unique_id = uuid.uuid4().hex
        original_filename = f'originals/{unique_id}{original_ext}'
        original_path = fs.save(original_filename, image)
        original_url = fs.url(original_path)
        
        # Kompres gambar
        compressed_image = compress_image(image)
        compressed_filename = f'compressed/{unique_id}_150px.jpg'
        compressed_path = fs.save(compressed_filename, compressed_image)
        compressed_url = fs.url(compressed_path)
        
        # Simpan metadata ke database
        uploaded_image = UploadedImage.objects.create(
            original_name=original_name,
            original_size=image.size,
            compressed_size=compressed_image.size,
            original_url=original_url,
            compressed_url=compressed_url
        )
        
        # Generate signed URLs (valid 1 jam)
        signed_original = signing.dumps({
            'type': 'original',
            'id': uploaded_image.id
        })
        signed_compressed = signing.dumps({
            'type': 'compressed',
            'id': uploaded_image.id
        })
        
        return JsonResponse({
            'success': True,
            'original_name': original_name,
            'original_size': image.size,
            'compressed_size': compressed_image.size,
            'signed_original': signed_original,
            'signed_compressed': signed_compressed
        })
    
    return render(request, 'upload.html')

def serve_signed_image(request, signed_data):
    try:
        data = signing.loads(signed_data, max_age=3600)  # Valid 1 jam
        image = UploadedImage.objects.get(id=data['id'])
        
        if data['type'] == 'original':
            return JsonResponse({'url': image.original_url})
        elif data['type'] == 'compressed':
            return JsonResponse({'url': image.compressed_url})
    except (signing.BadSignature, UploadedImage.DoesNotExist):
        return JsonResponse({'error': 'URL tidak valid'}, status=400)