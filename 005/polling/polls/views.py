# polls/views.py
from django.shortcuts import render, get_object_or_404
from .models import Poll, Option, Vote
from .forms import PollForm
import json
from django.http import JsonResponse

def create_poll(request):
    if request.method == 'POST':
        form = PollForm(request.POST)
        if form.is_valid():
            poll = form.save()
            for option_text in request.POST.getlist('options'):
                Option.objects.create(poll=poll, text=option_text)
            return JsonResponse({'poll_id': poll.id})
    else:
        form = PollForm()
    return render(request, 'create_poll.html', {'form': form})

def poll_detail(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    return render(request, 'poll.html', {'poll': poll})

def vote(request, option_id):
    option = get_object_or_404(Option, id=option_id)
    # Buat vote dengan mengisi poll secara eksplisit
    Vote.objects.create(option=option, poll=option.poll)
    return JsonResponse({'status': 'success'})