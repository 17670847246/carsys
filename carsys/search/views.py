from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.utils import timezone

from search.models import Record


def show_index(request: HttpRequest) -> HttpResponse:
    return render(request, 'index.html')


def search_records(request: HttpRequest) -> HttpResponse:
    try:
        page = int(request.GET.get('page', '1'))
        page = page if page >= 1 else 1
        size = int(request.GET.get('size', '5'))
        size = size if 0 < size <= 50 else 5
        queryset = Record.objects.filter(is_deleted=False)\
            .select_related('car').order_by('-makedate')
        carinfo = request.POST.get('carinfo', '').strip().upper()
        if carinfo:
            queryset = queryset.filter(
                Q(car__carno__startswith=carinfo) | Q(car__owner__contains=carinfo)
            )
        # total_page = (queryset.count() -1) // size + 1
        # queryset = queryset.order_by('-makedate')[(page-1) * size: page * size]
        paginator = Paginator(queryset, size)
        page_obj = paginator.get_page(page)
        return render(request, 'index.html', {
            'page_obj': page_obj,
            'carinfo': carinfo,
            'total_page': paginator.num_pages,
            'page_size': size,
        })
    except ValueError:
        return redirect('/')




def handle_record(request: HttpRequest) -> HttpResponse:
    try:
        rno = int(request.GET.get('rno'))
    except ValueError:
        data = {'code': 30002, 'mesg': '违章记录编号无效'}
    else:
        record = Record.objects.filter(no=rno, dealt=False).first()
        if record:
            record.dealt = True
            record.updated_time = timezone.now()
            record.save()
            data = {'code': 30000, 'mesg': '受理成功'}
        else:
            data = {'code': 30001, 'mesg': '受理失败'}
    return JsonResponse(data)

def delete_record(request: HttpRequest) -> HttpResponse:
    try:
        rno = request.GET.get('rno')
    except ValueError:
        data = {'code': 30002, 'mesg': '违章记录编号无效'}
    else:
        record = Record.objects.filter(no=rno, is_deleted=False).first()
        if record:
            record.is_deleted = True
            record.deleted_time = timezone.now()
            record.save()
            data = {'code': 40000, 'mesg': '删除成功'}
        else:
            data = {'code': 40001, 'mesg': '删除失败'}
    return JsonResponse(data)