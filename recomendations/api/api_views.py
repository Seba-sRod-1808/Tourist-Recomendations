from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json

from recomendations.queries import queries as neo4j

@login_required
def get_recommendations_api(request):
    limit = int(request.GET.get('limit', 6))
    try:
        recommendations = neo4j.get_recommendations(django_user_id=request.user.id, limit=limit)
        return JsonResponse({
            "success": True,
            "data": recommendations,
            "count": len(recommendations)
        })
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

@csrf_exempt
@login_required
def submit_review_api(request):
    if request.method != 'POST':
        return JsonResponse({"success": False, "error": "Only POST allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        place_uid = data.get('place_uid')
        rating = float(data.get('rating', 0))
        comment = data.get('comment', '')

        if not place_uid:
            return JsonResponse({"success": False, "error": "Missing place_uid"}, status=400)

        neo4j.add_review(
            django_user_id=request.user.id,
            place_uid=place_uid,
            rating=rating,
            comment=comment
        )
        
        return JsonResponse({"success": True, "message": "Review added successfully"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

@login_required
def explain_recommendation_api(request):
    place_uid = request.GET.get('place_uid')
    if not place_uid:
        return JsonResponse({"success": False, "error": "Missing place_uid"}, status=400)
    
    try:
        recommendations = neo4j.get_recommendations(django_user_id=request.user.id, limit=50)
        target = next((r for r in recommendations if r['uid'] == place_uid), None)
        
        if not target:
            return JsonResponse({"success": False, "error": "Destination not found in recommendations"}, status=404)
        
        return JsonResponse({
            "success": True,
            "data": {
                "name": target['name'],
                "score": target['score'],
                "details": target.get('details', {}),
                "match_reason": target['match_reason']
            }
        })
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
