import json
import pprint

from django.conf import settings
from django.http import HttpResponse

from plantit.feedback.models import Feedback
from plantit.sns import SnsClient


def submit_feedback(request):
    body = json.loads(request.body.decode('utf-8'))
    anon = body['anonymous']
    feedback = Feedback.objects.create(used=body['used'],
                                       wanted=body['wanted'],
                                       ease=body['ease'],
                                       features=body['features']) if anon \
        else Feedback.objects.create(user=request.user,
                                     used=body['used'],
                                     wanted=body['wanted'],
                                     ease=body['ease'],
                                     features=body['features'])

    # push email notification
    SnsClient.get().publish_message(settings.AWS_FEEDBACK_ARN,
                                    "PlantIT feedback" + ('' if anon else f" from {request.user.username}"), pprint.pprint(feedback),
                                    {})

    # TODO send Slack messages to a feedback channel
    return HttpResponse()


# def download_tutorials(request):
#     return FileResponse(open(settings.TUTORIALS_FILE, 'rb'))
#
#
# def download_feedback_form(request):
#     return FileResponse(open(settings.FEEDBACK_FILE, 'rb'))
