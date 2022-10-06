from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

# from events.api_views import ConferenceListEncoder
from common.json import ModelEncoder
from .models import Attendee, ConferenceVO, AccountVO
# from events.models import Conference


## TODO WHY ISN'T CONFERENCEVO_ID ALIGNING WITH CONFERENCE ID
## (I ASSUME SAME IS HAPPENING WITH ATTENDEEVO_ID NOW)
## I ASSUME IT'S FROM DELETING ROWS IN TABLES BUT I DON'T KNOW HOW TO FIX NOW

class ConferenceVODetailEncoder(ModelEncoder):
    model = ConferenceVO
    properties = [
        "name",
        "import_href",
        ]


class AttendeeListEncoder(ModelEncoder):
    model = Attendee
    properties = ["name"]


class AttendeeDetailEncoder(ModelEncoder):
    model = Attendee
    properties = [
        "email",
        "name",
        "company_name",
        "created",
        "conference",
    ]
    encoders = {
        "conference": ConferenceVODetailEncoder(),
    }
    # encoders = {
    #     "conference": ConferenceListEncoder(),
    # }
    def get_extra_data(self, o):
        # Get the count of AccountVO objects with email equal to o.email
        count = (AccountVO.objects.filter(email=o.email)).count()
        # Return a dictionary with "has_account": True if count > 0
        if count > 0:
            return {"has_account": True}
        # Otherwise, return a dictionary with "has_account": False
        else:
            return {"has_account": False}

@require_http_methods(["GET", "POST"])
def api_list_attendees(request, conference_vo_id=None):
    """
    Lists the attendees names and the link to the attendee
    for the specified conference id.

    Returns a dictionary with a single key "attendees" which
    is a list of attendee names and URLS. Each entry in the list
    is a dictionary that contains the name of the attendee and
    the link to the attendee's information.

    {
        "attendees": [
            {
                "name": attendee's name,
                "href": URL to the attendee,
            },
            ...
        ]
    }
    """
    if request.method == "GET":
        if conference_vo_id is not None:
            conference_href = f'/api/conferences/{conference_vo_id}/'
            conference = ConferenceVO.objects.get(import_href=conference_href)
            attendees = Attendee.objects.filter(conference=conference)
        else:
            attendees = Attendee.objects.all()
        return JsonResponse(
            {"attendees": attendees},
            encoder=AttendeeDetailEncoder,
        )
    else:
        content = json.loads(request.body)

        # Get the Conference object and put it in the content dict
        try:
            print(conference_vo_id)
            conference_href = f'/api/conferences/{conference_vo_id}/'
            conference = ConferenceVO.objects.get(import_href=conference_href)
            content["conference"] = conference
        except ConferenceVO.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid conference id"},
                status=400,
            )

        attendee = Attendee.objects.create(**content)
        return JsonResponse(
            attendee,
            encoder=AttendeeDetailEncoder,
            safe=False,
        )


def api_show_attendee(request, pk):
    """
    Returns the details for the Attendee model specified
    by the pk parameter.

    This should return a dictionary with email, name,
    company name, created, and conference properties for
    the specified Attendee instance.

    {
        "email": the attendee's email,
        "name": the attendee's name,
        "company_name": the attendee's company's name,
        "created": the date/time when the record was created,
        "conference": {
            "name": the name of the conference,
            "href": the URL to the conference,
        }
    }
    """
    attendee = Attendee.objects.get(id=pk)
    return JsonResponse(
        attendee,
        encoder=AttendeeDetailEncoder,
        safe=False,
    )
