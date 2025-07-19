# polls/migrations/0002_add_poll_to_vote.py
from django.db import migrations, models
import django.db.models.deletion

def populate_vote_poll(apps, schema_editor):
    Vote = apps.get_model('polls', 'Vote')
    Option = apps.get_model('polls', 'Option')
    
    # Update dalam batch untuk efisiensi
    batch_size = 1000
    votes = Vote.objects.filter(poll__isnull=True).select_related('option')
    for i in range(0, votes.count(), batch_size):
        batch = votes[i:i+batch_size]
        for vote in batch:
            if vote.option:
                vote.poll = vote.option.poll
        Vote.objects.bulk_update(batch, ['poll'], batch_size)

class Migration(migrations.Migration):
    dependencies = [
        ('polls', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='vote',
            name='poll',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='votes',
                to='polls.poll',
            ),
        ),
        migrations.RunPython(populate_vote_poll),
        migrations.AlterField(
            model_name='vote',
            name='poll',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='votes',
                to='polls.poll',
            ),
        ),
    ]