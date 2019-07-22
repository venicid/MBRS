from django.shortcuts import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect # 重定向，跳转

# Create your views here.
from django.contrib import auth  # django自带的用户认证


def login(request):
    # 登录验证
    if request.method == "POST":
        user=request.POST.get("user")
        pwd=request.POST.get("pwd")

        # django用户认证判定
        user=auth.authenticate(username=user,password=pwd)
        if user:
            auth.login(request,user)  # request.user  # 注册下
            return redirect("/index/")
    return render(request,"login.html")


import datetime
from .models import Book,Room
def index(request):
    time_choices = Book.time_choices
    room_list = Room.objects.all()

    # 预定msg
    date=datetime.datetime.now().date()  # 当前日期
    book_date=request.GET.get("book_date",date)   #预定日期
    book_list=Book.objects.filter(date=book_date)  # 过滤出表中预定的msg

    # LowB版本
    htmls_lowb = """
            <tr>
                <td>401(12)</td>
                <td class="active_other item" room_id="1" time_id="13"></td>
                <td class="active_other item" room_id="2" time_id="13"></td>
                <td class="active_other item" room_id="3" time_id="13"></td>
                <td class="active_other item" room_id="4" time_id="13"></td>
                <td class="active_other item" room_id="5" time_id="13"></td>
                <td class="active_other item" room_id="6" time_id="13"></td>
                <td class="active_other item" room_id="7" time_id="13"></td>
                <td class="active_other item" room_id="7" time_id="13"></td>
                <td class="active_other item" room_id="7" time_id="13"></td>
                <td class="active_other item" room_id="7" time_id="13"></td>
                <td class="active_other item" room_id="7" time_id="13"></td>
                <td class="active_other item" room_id="7" time_id="13"></td>
                <td class="active_other item" room_id="7" time_id="13"></td>
            </tr>
            """

    # Nb版本
    htmls = ""
    for room in room_list:
        htmls += "<tr><td>{}({})</td>".format(room.caption,room.num)

        for time_choice in time_choices:
            book = None
            flag = False  # 是否已经被预定
            for book in book_list:
                if book.room.pk==room.pk and book.time_id==time_choice[0]:
                # 意味着这个单元格已经预定
                    flag=True
                    break

            if flag: # 被预定

                if request.user.pk == book.user.pk:
                    # 登录人不同显示颜色不同
                    htmls += "<td class='active item' room_id='{}' time_id='{}'>{}</td>".format(room.pk,time_choice[0],book.user.username)
                else:
                    htmls += "<td class='another_active item' room_id='{}' time_id='{}'>{}</td>".format(room.pk,time_choice[0],book.user.username)

            else:  # 没被预定
                htmls += "<td class='item' room_id='{}' time_id='{}'></td>".format(room.pk, time_choice[0])
        htmls += "</tr>"


    return render(request,"index.html",locals())


import json
from django.db.models import Q
def book(request):
    post_data=json.loads(request.POST.get('post_data'))
    # {'ADD': {'1': ['5', '7'], '3': ['4']}, 'DEL': {'2': ['9']}}

    choose_date=request.POST.get("choose_date")

    res={"state":True,"msg":None}
    try:
        #添加预定
        book_list = []
        for room_id,time_id_list in post_data["ADD"].items():
            for time_id in time_id_list:
                book_obj = Book(user=request.user,room_id=room_id,time_id=time_id,date=choose_date)
                book_list.append(book_obj)

        Book.objects.bulk_create(book_list)

        # 删除预订
        # post_data["DEL"]: {"2":["2","3"]}

        remove_book = Q()

        for room_id, time_id_list in post_data["DEL"].items():
            temp = Q()

            for time_id in time_id_list:
                temp.children.append(("room_id", room_id))
                temp.children.append(("time_id", time_id))
                temp.children.append(("user_id", request.user.pk))
                temp.children.append(("date", choose_date))
                remove_book.add(temp, "OR")
                temp=Q()   # 同一room的不同时间预定的不能删除,要temp重新置到0

        if remove_book:
            Book.objects.filter(remove_book).delete()


    except Exception as e:
        res["state"] = False
        res["msg"] = str(e)

    return HttpResponse(json.dumps(res))

# 链接: https://pan.baidu.com/s/1nzY8khXOrlvtFX2367E2sg 密码: qu3a








