import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from quiz.ai_analytics import get_ai_insights_for_user

User = get_user_model()

# Test uchun birinchi foydalanuvchini olish
user = User.objects.first()

if user:
    print(f"Testing AI Analytics for user: {user.username}")
    print("-" * 50)
    
    try:
        insights = get_ai_insights_for_user(user)
        
        print("AI Analysis:")
        print(insights['ai_analysis'][:200] + "..." if len(insights['ai_analysis']) > 200 else insights['ai_analysis'])
        print(f"\nConfidence: {insights['confidence']}%")
        print(f"Recommendations count: {len(insights['recommendations'])}")
        
        if insights['recommendations']:
            print("\nRecommendations:")
            for i, rec in enumerate(insights['recommendations'][:3], 1):
                print(f"{i}. {rec['title']} ({rec['type']})")
        
        print("\n✅ AI Analytics test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        
else:
    print("❌ No users found in database!")