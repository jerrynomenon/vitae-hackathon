from django.http import HttpResponse
from django.http import JsonResponse
import re
from djangoserver.scripts import parser

def parseprofile(request):
    platformretriever = re.compile("platform=([a-zA-Z0-9]+)")
    userretriever = re.compile("reddit.com/u/(.*)")
    usernamebasis = request.GET.get("username")
    platform = request.GET.get("platform")
#    platform = platformretriever.findall(request)[0];
    if(len(platform) == 0):
        return JsonResponse({});
    if(platform == "reddit"):
        user = userretriever.findall(usernamebasis)[0]
        comments = parser.get_all_comments(user,100)
        submitted = parser.get_all_posts(user,100)
        items = parser.vt_relevant_items(comments + submitted, parser.sub_list)
        points = parser.vt_parse_items(items, {}, set(parser.sub_list))
        score = parser.vt_get_score(points)
        return JsonResponse({
            "score": score,
            "points": points,
        });
    else:
        return JsonResponse({"score": 666});

