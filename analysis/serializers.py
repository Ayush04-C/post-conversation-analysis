from rest_framework import serializers
from .models import Conversation, Message, ConversationAnalysis

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender', 'text']

class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True)

    class Meta:
        model = Conversation
        fields = ['id', 'created_at', 'messages']

    def create(self, validated_data):
        messages_data = validated_data.pop('messages')
        conversation = Conversation.objects.create(**validated_data)
        for message_data in messages_data:
            Message.objects.create(conversation=conversation, **message_data)
        return conversation

class ConversationAnalysisSerializer(serializers.ModelSerializer):
    conversation_id = serializers.IntegerField(source='conversation.id', read_only=True)

    class Meta:
        model = ConversationAnalysis
        fields = [
            'id', 'title', 'conversation_id', 'sentiment', 'clarity', 'empathy',
            'relevance', 'resolution', 'fallback_count', 'overall', 'created_at'
        ]
