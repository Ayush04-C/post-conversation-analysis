from django.contrib import admin

from .models import Conversation, Message, ConversationAnalysis

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')
    search_fields = ('id',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'sender', 'text')
    search_fields = ('text', 'sender')

@admin.register(ConversationAnalysis)
class ConversationAnalysisAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'sentiment', 'overall', 'created_at')
    search_fields = ('sentiment',)
