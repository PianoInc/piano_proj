from django.shortcuts import render
from datetime import datetime
from django.http import HttpResponseRedirect
from .models import *

def show_vis_list(request):
    res_custom = Jobs.objects.filter(vis=True, fav=False, site='custom').order_by('due')
    result = Jobs.objects.filter(vis=True, fav=False, contents=0).order_by('due')
    res_cnt = len(result) + len(res_custom)
    print("vis_list")
    return render(request, 'out_list.html', {'result':result, 'res_custom':res_custom, 'res_cnt':res_cnt})

def show_detail(request,idx):
    result = Jobs.objects.get(idx=idx)
    return render(request, 'out_detail.html', {'result':result } )

def show_fav_list(request):
    favs = Jobs.objects.filter(fav=True).order_by('due')
    print("vis_list")
    return render(request, 'out_fav_list.html', {'favs':favs, 'fav_cnt':len(favs)})

def show_sort_list(request, sort):
    print(sort)
    if sort=='dn':
        favs = Jobs.objects.filter(fav=True).order_by('due')
        result = Jobs.objects.filter(vis=True, fav=False).order_by('due')
        sort = 'up'
    else :
        favs = Jobs.objects.filter(fav=True).order_by('-due')
        result = Jobs.objects.filter(vis=True, fav=False).order_by('-due')
        sort = 'dn'
    print(sort)
    return render(request, 'out_sort_list.html', {'favs':favs, 'result':result, 'sort':sort, 'fav_cnt':len(favs) })

def show_invis_list(request):
    result = Jobs.objects.filter(vis=False).order_by('-save_date')
    print("invis_list")
    return render(request, 'out_invis_list.html', {'result':result, 'res_cnt':len(result)})

def make_fav(request, idx):
    print("fav")
    print(idx)
    if idx :
        result = Jobs.objects.get(idx=idx)
        result.fav = True
        result.vis = True
        result.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def make_nomal(request, idx):
    print("fav")
    print(idx)
    if idx :
        result = Jobs.objects.get(idx=idx)
        result.fav = False
        result.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def make_invis(request, idx):
    if idx :
        result = Jobs.objects.get(idx=idx)
        result.vis = False
        result.fav = False
        result.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def make_sel_fav(request):
    indexs = request.POST.getlist("checks[]")
    for idx in indexs :
        if idx != 'on' :
            result = Jobs.objects.get(idx=idx)
            result.fav = True
            result.vis = True
            result.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def make_sel_invis(request):
    indexs = request.POST.getlist("checks[]")
    for idx in indexs :
        if idx :
            if idx != 'on' :
                result = Jobs.objects.get(idx=idx)
                result.vis = False
                result.fav = False
                result.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def make_sel_nomal(request):
    indexs = request.POST.getlist("checks[]")
    for idx in indexs :
        if idx :
            if idx != 'on' :
                result = Jobs.objects.get(idx=idx)
                result.fav = False
                result.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def invis_past_biz(request):
    now = datetime.now()
    now_date = now.strftime('%Y-%m-%d')
    data = Jobs.objects.filter(vis=True).values()
    if(data) :
        data_cnt = len(data)
        for n in range(data_cnt):
            if len(data[n]['due']) == 10:
                try :
                    due = datetime.strptime(data[n]['due'], '%Y-%m-%d')
                except :
                    continue
                due_date = due.strftime('%Y-%m-%d')
                if now_date > due_date:
                    res = Jobs.objects.get(identify=data[n]['identify'])
                    res.vis = False
                    res.fav = False
                    while True :
                        try :
                            res.save()
                            print("save", due)
                            break
                        except :
                            print("retry")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def write_job(request):
    return render(request, 'write_job.html')

def edit_job(request, idx):
    result = Jobs.objects.get(idx=idx)
    return render(request, 'edit_job.html',{'result':result})

def add_job(request):
    idx = Jobs.objects.all().count() + 1

    data = Jobs(title = request.POST.get("title"),
                url = "/outsourcing_crawler/show_detail/%d" % idx,
                due = '게시물 참조',
                price= request.POST.get("price"),
                period= request.POST.get("period"),
                contents= request.POST.get("contents"),
                due_flag= 'blu',
                identify = "custom_%d" % idx,
                site = 'custom',
                save_date = datetime.now(),
                vis = True,
                fav = False)
    data.save()
    result = Jobs.objects.filter(vis=True, fav=False).order_by('due')
    return render(request, 'out_list.html', {'result':result, 'res_cnt':len(result)} )

def modify_job(request, idx):
    result = Jobs.objects.get(idx=idx)
    result.title = request.POST.get("title")
    result.price= request.POST.get("price")
    result.period= request.POST.get("period")
    result.contents= request.POST.get("contents")
    result.save_date = datetime.now()
    result.save()
    return render(request, 'out_detail.html', {'result':result } )

