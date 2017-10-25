from django.http import HttpResponse
import json


class Util:
    @staticmethod
    def create_response(msg):
        return HttpResponse(content=json.dumps(msg), charset='utf-8')
