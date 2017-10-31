import uuid
import json
from django.shortcuts import render, redirect
from server.models import Room, SchoolAccount
from server.util import get_account, get_token, send_fcm, get_sha512, is_login
from django.views.decorators.csrf import csrf_exempt


def list_view(req):
    if req.method == 'GET':
        if is_login(req) == 2:
            return redirect('/login?error=no_email')
        elif is_login(req) == 3:
            return redirect('/login?error=no_login')
        if not Room.objects.exists(name=req.GET.get('room', '')):
            return redirect('/error?error=no_room')
        room = Room.objects.get(name=req.GET.get('room', ''))
        if get_account('sch', req.session.get('token'), True) != Room.owner:
            return redirect('/error?error=no_access')
        data = json.loads(room.wait_members)
        w_list = []
        for key in data.keys():
            w_list.append({"name": data[key].name, "number": data[key].student_number})
        return render(req, 'list.html', {'wait': w_list})
    else:
        name = req.POST['name']
        num = req.POST['number']
        types = req.POST['type']
        room = Room.objects.get(name=req.POST.get('room', ''))
        if get_account('sch', req.session.get('token'), True) != Room.owner:
            return redirect('/error?error=no_access')
        data = json.loads(room.wait_members)
        d = json.loads(room.members)
        for i in data.keys():
            if data[i].name == name and data[i].student_number == num:
                if types != "del":
                    d[data[i]] = data[i]
                del data[i]
        room.wait_members = data
        room.members = d
        room.save()
        return redirect('./')


def signup(req):
    if req.method == 'GET':
        if is_login(req) == 1:
            return redirect('/send')
        return render(request=req, template_name='signup.html', context={}, content_type='text/html')
    uid = uuid.uuid4().urn.__str__()
    print(req.POST)
    if get_account(acoount_type='sch', email=req.POST['email']) is not None:
        return redirect('./?error=existent_account')
    school = SchoolAccount.objects.create(email=req.POST['email'], password=uid + ":" + get_sha512(uid + req.POST['pw']), name=req.POST['name'])
    Room.objects.create(name=req.POST['name'], owner=school)
    return redirect('/send')


def send(req):
    if req.method == 'GET':
        if is_login(req) == 2:
            return redirect('/login?error=no_email')
        elif is_login(req) == 3:
            return redirect('/login?error=no_login')
        if not Room.objects.exists(name=req.GET.get('room', '')):
            return redirect('/login?error=no_room')
        return render(request=req, template_name='send.html', context={}, content_type='text/html')
    if not Room.objects.exists(name=req.POST['room']):
        room = Room.objects.get(name=req.POST['room'])
        data = json.loads(room.members)
        for key in data.keys():
            send_fcm(get_account('st', key).fcm, req.POST['title'], req.POST['msg'], {"year": req.POST['year'], "month": req.POST['month'], "date": req.POST['date']})
    return redirect('./?type=requested')


def room(req):
    if req.method == 'GET':
        render(req, 'create.html', {})
    return redirect('./?query=finish')


@csrf_exempt
def register_check(req):
    if req.method == 'GET':
        token = req.GET.get('query', '')
        account = get_account(req.GET.get('type', ''), token, True)
        if account is not None:
            account.token = get_token(account.password.split(":")[0])
            account.level = 1
            account.save()
            return render(request=req, template_name='verify.html', context={}, content_type='text/html')
    return error(req, head="잘못된 접근")


def error(req, head="원인을 알 수 없습니다.", link="https://jaeheon.com:/8000"):
    return render(req, 'error.html', {"error": head, "link": link})


def error404(req):
    return error(req=req, head="잘못된 주소 입니다.")


def error500(req):
    return error(req=req, head="내부 서버에러입니다. 다시 시도하세요.")


def error403(req):
    return error(req=req, head="접근할 수 없는 주소입니다.")


def error400(req):
    return error(req=req, head="잘못된 요청입니다.")
