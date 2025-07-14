from django.http import JsonResponse

def check_auth(request):
    secret_key = request.headers.get("X-Secret-Key")
    return secret_key == "Rahul@121005"  # Or move to env variable later

def unauthorized_response():
    return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=401)

def api_response(success=True, message="Success", data=None, status=200):
    return JsonResponse({
        'success': success,
        'message': message,
        'data': data
    }, status=status)
