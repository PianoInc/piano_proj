from django.shortcuts import render
from datetime import datetime
from django.http import HttpResponseRedirect
from .models import *

def show_vis_list(request):
    result = Business.objects.filter(vis=True, fav=False).order_by('due')
    print("vis_list")
    return render(request, 'list.html', {'result':result, 'res_cnt':len(result)} )

def show_fav_list(request):
    favs = Business.objects.filter(fav=True).order_by('due')
    print("vis_list")
    return render(request, 'fav_list.html', {'favs':favs, 'fav_cnt':len(favs)})

def show_sort_list(request, sort):
    print(sort)
    if sort=='dn':
        favs = Business.objects.filter(fav=True).order_by('due')
        result = Business.objects.filter(vis=True, fav=False).order_by('due')
        sort = 'up'
    else :
        favs = Business.objects.filter(fav=True).order_by('-due')
        result = Business.objects.filter(vis=True, fav=False).order_by('-due')
        sort = 'dn'
    print(sort)
    return render(request, 'sort_list.html', {'favs':favs, 'result':result, 'sort':sort, 'fav_cnt':len(favs) })

def show_invis_list(request):
    result = Business.objects.filter(vis=False).order_by('-save_date')
    print("invis_list")
    return render(request, 'invis_list.html', {'result':result, 'res_cnt':len(result)})

def make_fav(request, idx):
    print("fav")
    print(idx)
    if idx :
        result = Business.objects.get(idx=idx)
        result.fav = True
        result.vis = True
        result.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def make_nomal(request, idx):
    print("fav")
    print(idx)
    if idx :
        result = Business.objects.get(idx=idx)
        result.fav = False
        result.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def make_invis(request, idx):
    if idx :
        result = Business.objects.get(idx=idx)
        result.vis = False
        result.fav = False
        result.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def make_sel_fav(request):
    indexs = request.POST.getlist("checks[]")
    for idx in indexs :
        if idx != 'on' :
            result = Business.objects.get(idx=idx)
            result.fav = True
            result.vis = True
            result.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def make_sel_invis(request):
    indexs = request.POST.getlist("checks[]")
    for idx in indexs :
        if idx :
            if idx != 'on' :
                result = Business.objects.get(idx=idx)
                result.vis = False
                result.fav = False
                result.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def make_sel_nomal(request):
    indexs = request.POST.getlist("checks[]")
    for idx in indexs :
        if idx :
            if idx != 'on' :
                result = Business.objects.get(idx=idx)
                result.fav = False
                result.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def invis_past_biz(request):
    now = datetime.now()
    now_date = now.strftime('%Y-%m-%d')
    data = Business.objects.filter(vis=True).values()
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
                    res = Business.objects.get(identify=data[n]['identify'])
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

