from django.contrib import admin
from .models import Poll, Option, Vote


class OptionInline(admin.TabularInline):
    """Inline admin untuk Option dalam Poll"""
    model = Option
    extra = 2
    fields = ['text']


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    """Admin interface untuk Poll"""
    list_display = ['title', 'is_active', 'total_votes', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [OptionInline]
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'is_active')
        }),
        ('Info', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    """Admin interface untuk Option"""
    list_display = ['text', 'poll', 'vote_count', 'vote_percentage', 'created_at']
    list_filter = ['poll', 'created_at']
    search_fields = ['text', 'poll__title']
    readonly_fields = ['id', 'created_at']


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    """Admin interface untuk Vote"""
    list_display = ['option', 'poll', 'ip_address', 'created_at']
    list_filter = ['option__poll', 'created_at']
    search_fields = ['option__text', 'option__poll__title', 'ip_address']
    readonly_fields = ['id', 'created_at']
    
    def poll(self, obj):
        return obj.option.poll.title
    poll.short_description = 'Poll'

