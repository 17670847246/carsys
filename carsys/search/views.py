from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from search.models import Record


def show_index(request: HttpRequest) -> HttpResponse:
    return render(request, 'index.html')


def search_records(request: HttpRequest) -> HttpResponse:
    try:
        page = int(request.GET.get('page', '1'))
        page = page if page >= 1 else 1
        size = int(request.GET.get('size', '5'))
        size = size if 0 < size <= 50 else 5
        queryset = Record.objects.filter(is_deleted=False)
        carinfo = request.POST.get('carinfo', '').strip().upper()
        if carinfo:
            queryset = queryset.filter(
                Q(car__carno__startswith=carinfo) | Q(car__owner__contains=carinfo)
            )
        total_page = (queryset.count() -1) // size + 1
        queryset = queryset.order_by('-makedate')[(page-1) * size: page * size]
        return render(request, 'index.html', {
            'records': queryset,
            'carinfo': carinfo,
            'new_page': page,
            'total_page': total_page,
            'page_size': size,
            'has_prev': page > 1,
            'has_next': page < total_page,
        })
    except ValueError:
        return redirect('/')