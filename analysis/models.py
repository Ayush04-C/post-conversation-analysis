from django.db import models

class Conversation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.CharField(max_length=10)
    text = models.TextField()

class ConversationAnalysis(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    conversation = models.OneToOneField(Conversation, on_delete=models.CASCADE)
    sentiment = models.CharField(max_length=10, null=True)
    clarity = models.FloatField(null=True)
    empathy = models.FloatField(null=True)
    accuracy = models.FloatField(null=True)
    relevance = models.FloatField(null=True)
    escalation_need = models.BooleanField(default=False)
    completeness = models.FloatField(null=True)
    resolution = models.BooleanField(default=False)
    fallback_count = models.IntegerField(default=0)
    overall = models.FloatField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
