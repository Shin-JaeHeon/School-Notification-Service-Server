import json
import uuid
from ..util import create_response, get_sha512, get_token, get_account, is_login
from django.views.decorators.csrf import csrf_exempt
from ..models import StudentAccount, Meal, Room
from django.shortcuts import redirect, render


@csrf_exempt
def register(req):
    if req.method == 'POST':
        uid = uuid.uuid4()
        print(req.body.decode("utf-8"))
        json_data = json.loads(req.body.decode("utf-8"))
        if not Room.objects.filter(name=json_data['room']).exists():
            return create_response('response,register_failed:nonexistent_room')
        if get_account('st', json_data['email']) is None:
            f = open("jeonguk.json", 'r')
            data = json.loads(f.read())
            f.close()
            if json_data['school'] in data:
                school_code = data[json_data['school']]
            else:
                school_code = ''
            account = StudentAccount.objects.create(email=json_data['email'])
            account.password = uid.__str__() + ":" + get_sha512(uid.__str__() + json_data['password'])
            account.student_number = json_data['stnumber']
            account.name = json_data['name']
            account.rome_name = json_data['room']
            account.school = school_code
            account.token = get_token(uid.urn.__str__())
            account.save()
            return create_response('response,register_success')
        return create_response('response,register_failed:existent_account')
    return redirect('/error/')


@csrf_exempt
def school(req):
    if req.method == "POST":
        json_data = json.loads(req.body.decode("utf-8"))
        f = open("jeonguk.json", 'r')
        data = json.loads(f.read())
        f.close()
        if json_data['school'] in data:
            return create_response('response,success,code,' + data[json_data['school']])
        else:
            return create_response('response,failed')
    return redirect('/error/')


@csrf_exempt
def login(req):
    if req.method == 'POST':
        json_data = json.loads(req.body.decode("utf-8"))
        print(json_data)
        account = get_account('st', json_data['id'])
        if account is None:
            return create_response('response,login_failed:nonexistent')
        elif account.password.split(":")[1] == get_sha512(account.password.split(":")[0] + json_data['password']):
            return create_response('response,login_success,school,' + account.school)
        return create_response('response,login_failed:password')
    else:
        if is_login(req) == 1:
            return redirect('/send')
        return render(request=req, template_name='login.html', context={}, content_type='text/html')


@csrf_exempt
def lg(req):
    if req.method == 'POST':
        account = get_account('sch', req.POST['id'])
        if account is None:
            return redirect('/error/')
        elif account.password.split(":")[1] != get_sha512(account.password.split(":")[0] + req.POST['password']):
            return redirect('/error/')
        token = get_token(account.password.split(":")[0])
        account.token = token
        req.session['token'] = token
        account.save()
        return redirect('/send')
    return redirect('/error/')


@csrf_exempt
def fcm(req):
    if req.method == 'POST':
        json_data = json.loads(req.body.decode("utf-8"))
        print(json_data)
        account = get_account('st', json_data['id'])
        if account is None:
            return create_response('response,fcm_failed:nonexistent')
        if account.password.split(":")[1] != get_sha512(account.password.split(":")[0] + json_data['pw']):
            return create_response('response,fcm_failed:password')
        account.fcm = json_data['fcm']
        account.save()
        return create_response('response,fcm_success')
    return redirect('/error/')


@csrf_exempt
def alarm(req):
    if req.method == 'POST':
        json_data = json.loads(req.body.decode("utf-8"))
        print(json_data)
        account = get_account('st', json_data['id'])
        if account is None:
            return create_response('response,alarm_failed:nonexistent')
        if account.password.split(":")[1] != get_sha512(account.password.split(":")[0] + json_data['pw']):
            return create_response('response,alarm_failed:password')
        Meal.objects.create(owner=account, hour=json_data['hour'], m=json_data['min'], type=json_data['type']).save()
        return create_response('response,alarm_success')
    return redirect('/error/')


@csrf_exempt
def alarm_remove(req):
    if req.method == 'POST':
        json_data = json.loads(req.body.decode("utf-8"))
        print(json_data)
        account = get_account('st', json_data['id'])
        if account is None:
            return create_response('response,alarm_remove_failed:nonexistent')
        if account.password.split(":")[1] != get_sha512(account.password.split(":")[0] + json_data['pw']):
            return create_response('response,alarm_yu k,l.remove_failed:password')
        Meal.objects.get(owner=account, type=json_data['type']).delete()
        return create_response('response,alarm_remove_success')
    return redirect('/error/')
