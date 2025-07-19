from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
import json
import uuid
from .models import Poll, Option, Vote


def index(request):
    """Halaman utama dengan daftar poll"""
    polls = Poll.objects.filter(is_active=True).order_by('-created_at')[:10]
    return render(request, 'polls/index.html', {'polls': polls})


def create_poll(request):
    """View untuk membuat poll baru"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        options = request.POST.getlist('options')
        
        # Filter opsi yang tidak kosong
        options = [opt.strip() for opt in options if opt.strip()]
        
        if not title or len(options) < 2:
            messages.error(request, 'Poll harus memiliki judul dan minimal 2 opsi.')
            return render(request, 'polls/create.html')
        
        try:
            with transaction.atomic():
                # Buat poll baru
                poll = Poll.objects.create(
                    title=title,
                    description=description
                )
                
                # Buat opsi-opsi
                for option_text in options:
                    Option.objects.create(
                        poll=poll,
                        text=option_text
                    )
                
                messages.success(request, f'Poll "{title}" berhasil dibuat!')
                return redirect('polls:detail', poll_id=poll.id)
                
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
    
    return render(request, 'polls/create.html')


def poll_detail(request, poll_id):
    """View untuk menampilkan detail poll dan form voting"""
    poll = get_object_or_404(Poll, id=poll_id, is_active=True)
    
    # Cek apakah user sudah vote
    user_ip = get_client_ip(request)
    has_voted = Vote.objects.filter(
        option__poll=poll,
        ip_address=user_ip
    ).exists()
    
    context = {
        'poll': poll,
        'has_voted': has_voted,
        'user_ip': user_ip
    }
    
    return render(request, 'polls/detail.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def vote(request, poll_id):
    """API endpoint untuk voting"""
    try:
        poll = get_object_or_404(Poll, id=poll_id, is_active=True)
        
        # Parse JSON data
        data = json.loads(request.body)
        option_id = data.get('option_id')
        
        if not option_id:
            return JsonResponse({'error': 'Option ID diperlukan'}, status=400)
        
        option = get_object_or_404(Option, id=option_id, poll=poll)
        
        # Dapatkan IP address
        user_ip = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Cek apakah sudah vote
        existing_vote = Vote.objects.filter(
            option__poll=poll,
            ip_address=user_ip
        ).first()
        
        if existing_vote:
            return JsonResponse({'error': 'Anda sudah memberikan vote untuk poll ini'}, status=400)
        
        # Buat vote baru
        vote = Vote.objects.create(
            option=option,
            ip_address=user_ip,
            user_agent=user_agent
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Vote berhasil disimpan',
            'vote_id': str(vote.id)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def poll_results_api(request, poll_id):
    """API endpoint untuk mendapatkan hasil poll dalam format JSON"""
    poll = get_object_or_404(Poll, id=poll_id, is_active=True)
    
    results = []
    total_votes = poll.total_votes()
    
    for option in poll.options.all():
        vote_count = option.vote_count()
        percentage = option.vote_percentage()
        
        results.append({
            'id': str(option.id),
            'text': option.text,
            'votes': vote_count,
            'percentage': percentage
        })
    
    return JsonResponse({
        'poll_id': str(poll.id),
        'title': poll.title,
        'total_votes': total_votes,
        'results': results,
        'timestamp': timezone.now().isoformat()
    })


def poll_stream(request, poll_id):
    """Server-Sent Events endpoint untuk real-time updates"""
    poll = get_object_or_404(Poll, id=poll_id, is_active=True)
    
    def event_stream():
        """Generator untuk SSE"""
        import time
        
        while True:
            # Dapatkan data terbaru
            results = []
            total_votes = poll.total_votes()
            
            for option in poll.options.all():
                vote_count = option.vote_count()
                percentage = option.vote_percentage()
                
                results.append({
                    'id': str(option.id),
                    'text': option.text,
                    'votes': vote_count,
                    'percentage': percentage
                })
            
            data = {
                'poll_id': str(poll.id),
                'title': poll.title,
                'total_votes': total_votes,
                'results': results,
                'timestamp': timezone.now().isoformat()
            }
            
            yield f"data: {json.dumps(data)}\n\n"
            time.sleep(2)  # Update setiap 2 detik
    
    response = HttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['Connection'] = 'keep-alive'
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Headers'] = 'Cache-Control'
    
    return response


def get_client_ip(request):
    """Helper function untuk mendapatkan IP address client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

