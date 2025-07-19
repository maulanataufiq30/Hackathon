# polls/migrations/0002_populate_vote_poll.py
from django.db import migrations

def populate_vote_poll(apps, schema_editor):
    Vote = apps.get_model('polls', 'Vote')
    for vote in Vote.objects.all():
        vote.poll = vote.option.poll
        vote.save()

class Migration(migrations.Migration):
    dependencies = [
        ('polls', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_vote_poll),
    ]