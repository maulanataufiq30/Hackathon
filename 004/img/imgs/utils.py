from PIL import Image
from io import BytesIO
import os
from django.core.files.uploadedfile import InMemoryUploadedFile

def compress_image(image, max_width=150):
    """Kompres gambar ke thumbnail 150px"""
    img = Image.open(image)
    
    # Konversi RGBA ke RGB jika perlu
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    
    # Hitung dimensi baru
    w_percent = max_width / float(img.width)
    h_size = int(float(img.height) * float(w_percent))
    
    # Resize gambar
    img = img.resize((max_width, h_size), Image.LANCZOS)
    
    # Simpan ke buffer
    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=70, optimize=True)
    buffer.seek(0)
    
    # Buat file in-memory
    compressed_file = InMemoryUploadedFile(
        buffer,
        'ImageField',
        os.path.splitext(image.name)[0] + '_compressed.jpg',
        'image/jpeg',
        buffer.getbuffer().nbytes,
        None
    )
    
    return compressed_file