from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import textstat, re

def analyze_conversation(messages):
    analyzer = SentimentIntensityAnalyzer()
    title = messages[0]["text"][:50] if messages else "Untitled Conversation"
    all_text = " ".join([m["text"] for m in messages])
    sentiment_score = analyzer.polarity_scores(all_text)["compound"]
    sentiment_label = "positive" if sentiment_score > 0.05 else "negative" if sentiment_score < -0.05 else "neutral"

    # Accuracy: Based on presence of concrete answers vs vague responses
    definitive_patterns = len(re.findall(r'\b(yes|no|correct|exactly|specifically|precisely)\b', all_text.lower()))
    vague_patterns = len(re.findall(r'\b(maybe|perhaps|possibly|might|could be|not sure)\b', all_text.lower()))
    total_responses = len(messages)
    accuracy = max(0, min(1, (definitive_patterns - vague_patterns) / max(total_responses, 1) + 0.5))
    
    # Completeness: Based on conversation length, back-and-forth, and conclusion indicators
    word_count = len(all_text.split())
    has_greeting = any(word in all_text.lower() for word in ['hello', 'hi', 'hey', 'greetings'])
    has_closing = any(word in all_text.lower() for word in ['thanks', 'thank you', 'goodbye', 'bye', 'appreciate'])
    completeness = min(1, (word_count / 500) * 0.6 + (0.2 if has_greeting else 0) + (0.2 if has_closing else 0))
    
    # Escalation Need: Check for frustration, requests for human help, or unresolved issues
    escalation_keywords = ['human agent', 'speak to someone', 'escalate', 'manager', 'supervisor', 
                          'not helping', 'frustrated', 'angry', 'unacceptable', 'complaint']
    escalation_need = any(keyword in all_text.lower() for keyword in escalation_keywords)
    
    # Clarity: Based on readability score (lower grade = clearer)
    try:
        fk_grade = textstat.flesch_kincaid_grade(all_text)
        clarity = max(0, min(1, 1 - (fk_grade / 20)))
    except:
        clarity = 0.5
    
    # Empathy: Detect empathetic language and expressions
    empathy_patterns = re.findall(r'\b(understand|sorry|apologize|appreciate|help|support|concern|'
                                 r'unfortunate|regret|certainly|happy to|glad to)\b', all_text.lower())
    empathy = min(1, len(empathy_patterns) / max(total_responses * 2, 1))
    
    # Relevance: Check if responses stay on topic (less repetition = more relevant)
    unique_words = len(set(all_text.lower().split()))
    total_words = len(all_text.split())
    word_diversity = unique_words / max(total_words, 1)
    question_marks = all_text.count('?')
    relevance = min(1, word_diversity * 1.2 + (0.1 if question_marks > 0 else 0))
    
    # Resolution: Check for explicit resolution indicators
    resolution_keywords = ['resolved', 'solved', 'fixed', 'working now', 'issue resolved', 
                          'problem solved', 'all set', 'good to go']
    resolution = any(keyword in all_text.lower() for keyword in resolution_keywords)
    
    # Fallback Count: Count instances of fallback/uncertain responses
    fallback_count = len(re.findall(r"don'?t know|can'?t help|cannot assist|not sure|"
                                   r"sorry.{0,20}(understand|help)|unable to", all_text.lower()))
    
    # Overall Score: Weighted average of all metrics
    overall = (
        accuracy * 0.2 +
        completeness * 0.15 +
        clarity * 0.15 +
        empathy * 0.15 +
        relevance * 0.15 +
        (1 if resolution else 0) * 0.2 -
        (fallback_count * 0.05)
    )
    overall = max(0, min(1, overall))

    return {
        "title": title,
        "accuracy": accuracy,
        "completeness": completeness,
        "escalation_need": escalation_need,
        "sentiment": sentiment_label,
        "clarity": round(clarity, 2),
        "empathy": empathy,
        "relevance": relevance,
        "resolution": resolution,
        "fallback_count": fallback_count,
        "overall": round(overall, 2)
    }
