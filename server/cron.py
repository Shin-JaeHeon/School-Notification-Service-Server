import datetime

from server.models import Meal
from server.util import send_fcm_data


def my_scheduled_job():
    date = datetime.datetime.now()
    for i in Meal.objects.all().filter(hour=date.hour):
        print(i)
    for i in Meal.objects.all().filter(hour=date.hour, min=date.minute):
        send_fcm_data(i.owner.fcm, {"type": i.type})
        i.log = i.log+1
        i.save()
