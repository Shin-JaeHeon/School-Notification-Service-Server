import json
import uuid
from ..util import create_response, register_email, get_sha512, get_token, get_account, is_login
from django.views.decorators.csrf import csrf_exempt
from ..models import StudentAccount, Room, TeacherAccount
from django.shortcuts import redirect, render


@csrf_exempt
def register(req):
    if req.method == 'POST':
        uid = uuid.uuid4()
        print(req.body.decode("utf-8"))
        json_data = json.loads(req.body.decode("utf-8"))
        if Room.objects.filter(name=json_data['room']).exists():
            return create_response('response,register_failed:nonexistent_room')
        if get_account('st', json_data['email']) is None:
            account = StudentAccount.objects.create(email=json_data['email'])
            account.password = uid.__str__() + ":" + get_sha512(uid.__str__() + json_data['password'])
            account.student_number = json_data['stnumber']
            account.name = json_data['name']
            account.rome_name = json_data['room']
            account.token = register_email(json_data['email'], get_token(uid.urn.__str__()), json_data['name'], 'st')
            account.school
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
        account = get_account('st', json_data['id'], False if '@' in json_data['id'] else True)
        if account is None:
            return create_response('response,login_failed:nonexistent')
        elif account.password != get_sha512(account.password.split(":")[0] + json_data['password'] if 'password' in json_data else ''):
            return create_response('response,login_failed:password')
        elif account.token != json_data['password'] if 'password' in json_data else '':
            return create_response('response,login_failed:token')
        return create_response('response,login_success,token,' + get_token(account.password.split(":")[0]) + ",code," + account.school)
    else:
        if is_login(req) == 1:
            return redirect('/send')
        return render(request=req, template_name='login.html', context={}, content_type='text/html')


def lg(req):
    if req.method == 'POST':
        account = get_account('tch', req.POST['id'])
        if account is None:
            return redirect('/error/')
        elif account.password != get_sha512(account.password.split(":")[0] + req.POST['password']):
            return redirect('/error/')
        token = get_token(account.password.split(":")[0])
        account.token = token
        req.session['token'] = token
        return redirect('/send')
    return redirect('/error/')


def fcm(req):
    if req.method == 'POST':
        json_data = json.loads(req.body.decode("utf-8"))
        account = get_account('st', json_data['token'], True)
        if account is None:
            return create_response('response,fcm_failed:nonexistent')
        account.fcm = json_data['fcm']
    return redirect('/error/')


def alarm(req):
    if req.method == 'POST':
        json_data = json.loads(req.body.decode("utf-8"))
        account = get_account('st', json_data['token'], True)
        if account is None:
            return create_response('response,alarm_failed:nonexistent')
        account.fcm = json_data['fcm']
    return redirect('/error/')
