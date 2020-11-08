from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

# Create your views here.
from search.models import Record


def show_index(request: HttpRequest) -> HttpResponse:
    return render(request, 'index.html')


def search_records(request: HttpRequest) -> HttpResponse:
    queryset = Record.objects.filter(is_deleted=False)
    carinfo = request.POST.get('carinfo', '').strip().upper()
    if carinfo:
        queryset = queryset.filter(
            Q(car__carno__startswith=carinfo) | Q(car__owner__contains=carinfo)
        )
    return render(request, 'index.html', {
        'records': queryset,
        'carinfo': carinfo
    })
