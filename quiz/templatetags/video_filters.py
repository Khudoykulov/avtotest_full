from django import template
import re

register = template.Library()

@register.filter
def youtube_embed_url(url):
    """
    YouTube URL ni embed URL ga o'zgartiradi
    """
    if not url:
        return ""
    
    # YouTube video ID ni topish - barcha formatlar uchun
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|m\.youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})',
        r'youtube\.com.*[?&]v=([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            # Har doim www.youtube.com/embed/ format ishlatamiz
            return f"https://www.youtube.com/embed/{video_id}?rel=0&modestbranding=1&fs=1"
    
    return url

@register.filter
def youtube_video_id(url):
    """
    YouTube URL dan video ID ni ajratib oladi
    """
    if not url:
        return ""
    
    # Barcha YouTube format uchun ID topish
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|m\.youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})',
        r'youtube\.com.*[?&]v=([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return ""

@register.filter
def youtube_thumbnail_url(url):
    """
    YouTube video thumbnail URL ini qaytaradi
    """
    video_id = youtube_video_id(url)
    if video_id:
        return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
    return ""

@register.filter
def is_youtube(url):
    """
    URL YouTube ekanligini tekshiradi
    """
    if not url:
        return False
    return any(domain in url.lower() for domain in ['youtube.com', 'youtu.be', 'm.youtube.com'])