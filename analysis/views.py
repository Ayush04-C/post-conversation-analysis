from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Conversation, ConversationAnalysis
from .serializers import ConversationSerializer, ConversationAnalysisSerializer
from .utils import analyze_conversation

@api_view(['POST'])
def create_conversation(request):
    serializer = ConversationSerializer(data=request.data)
    if serializer.is_valid():
        conversation = serializer.save()
        return Response({"conversation_id": conversation.id}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def analyse_conversation(request):
    conversation_id = request.data.get('conversation_id')
    try:
        conversation = Conversation.objects.get(id=conversation_id)
    except Conversation.DoesNotExist:
        return Response({"error": "Conversation not found"}, status=status.HTTP_404_NOT_FOUND)

    messages = [{"text": m.text} for m in conversation.messages.all()]
    result = analyze_conversation(messages)

    analysis, created = ConversationAnalysis.objects.update_or_create(
        conversation=conversation,
        defaults=result
    )

    serializer = ConversationAnalysisSerializer(analysis)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_reports(request):
    analyses = ConversationAnalysis.objects.all().order_by('-created_at')
    serializer = ConversationAnalysisSerializer(analyses, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
