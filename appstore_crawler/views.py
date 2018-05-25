from django.shortcuts import render
from .models import *

def show_app_list(request) :
    res = AppInfo.objects.all()
    return render(request,'app_list.html', {'apps':res})

def show_detail(request, app_id) :
    res = AppInfo.objects.filter(app_id=app_id)
    img = AppImage.objects.filter(app_id=app_id)
    review = AppReview.objects.filter(app_id=app_id)
    return render(request,'list_detail.html', {'app':res, 'img':img, 'review':review })

def show_app_icon(request) :
    res = AppInfo.objects.all()
    return render(request,'app_icon.html', {'icons':res})

def show_app_img(request) :
    res = AppImage.objects.all()
    return render(request,'app_img.html', {'imgs':res})

def show_app_review(request) :
    res = AppReview.objects.all()
    print(res)
    return render(request,'app_review.html', {'reviews':res})

