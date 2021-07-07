import json

from django.http import HttpResponse

from plantit.feedback.models import Feedback


def submit_feedback(request):
    body = json.loads(request.body.decode('utf-8'))
    feedback = Feedback.objects.create(used=body['used'], wanted=body['wanted'], ease=body['ease'], features=body['features']) if body['anonymous'] else Feedback.objects.create(user=request.user, used=body['used'], wanted=body['wanted'], ease=body['ease'], features=body['features'])
    # TODO send AWS notification to admin emails (configured in .env)
    # TODO send Slack messages to a feedback channel
    return HttpResponse()