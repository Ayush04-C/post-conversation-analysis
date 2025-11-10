from celery import shared_task
from analysis.models import Conversation, ConversationAnalysis
from analysis.utils import analyze_conversation

@shared_task
def run_daily_analysis():
    conversations = Conversation.objects.filter(conversationanalysis__isnull=True)
    for convo in conversations:
        messages = [{"text": m.text} for m in convo.messages.all()]
        result = analyze_conversation(messages)
        ConversationAnalysis.objects.create(conversation=convo, **result)
    return f"Analyzed {conversations.count()} conversations"
