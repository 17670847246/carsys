import io
from urllib.parse import quote

import xlwt
from django.core.paginator import Paginator
from django.db import connection
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.utils import timezone

from search.models import Record, Car


def show_index(request: HttpRequest) -> HttpResponse:
    return render(request, 'index.html')


def search_records(request: HttpRequest) -> HttpResponse:
    try:
        page = int(request.GET.get('page', '1'))
        page = page if page >= 1 else 1
        size = int(request.GET.get('size', '5'))
        size = size if 0 < size <= 50 else 5
        # 一对一、多对一外键关联可以通过QuerySet对象的select_related('关联对象')解决1+N查询问题
        # 多对多外键关联可以通过QuerySet对象的prefetch_related('关联对象')解决1+N查询问题
        # 可以通过QuerySet对象的only方法指定哪些字段需要投影
        # 可以通过QuerySet对象的defer方法指定哪些字段是不需要投影的
        queryset = Record.objects.filter(is_deleted=False) \
            .defer('is_deleted', 'deleted_time', 'updated_time') \
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
        record = Record.objects.filter(no=rno).first()
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
            if record.dealt:
                record.is_deleted = True
                record.deleted_time = timezone.now()
                record.save()
                data = {'code': 40000, 'mesg': '删除成功'}
            else:
                data = {'code': 40001, 'mesg': '请先受理再删除'}
    return JsonResponse(data)


def export_excel(request: HttpRequest) -> HttpResponse:
    queryset = Record.objects.filter(is_deleted=False) \
        .defer('is_deleted', 'deleted_time', 'updated_time') \
        .select_related('car').order_by('-makedate')
    wb = xlwt.Workbook()
    sheet = wb.add_sheet('违章记录表')
    titles = ('编号', '车牌号', '车主姓名', '违章原因', '违章时间', '处罚方式', '是否受理')
    for col_index, title in enumerate(titles):
        sheet.write(0, col_index, title)
    for row_index, record in enumerate(queryset):
        sheet.write(row_index + 1, 0, record.no)
        sheet.write(row_index + 1, 1, record.car.carno)
        sheet.write(row_index + 1, 2, record.car.owner)
        sheet.write(row_index + 1, 3, record.reason)
        sheet.write(row_index + 1, 4, record.makedate.strftime('%Y-%m-%d'))
        sheet.write(row_index + 1, 5, record.punish)
        sheet.write(row_index + 1, 6, '已受理' if record.dealt else '未受理')
    buffer = io.BytesIO()
    # str(不变) - 字符串 - 'hello' ---> io.StringIO(可变)
    # bytes(不变) - 字节串 - b '\xff\xe0\x9a' ---> io.BytesIO(可变) ---> 内存区域
    wb.save(buffer)
    # 创建HTTP响应对象并指定MIME类型（给浏览器的内容的类型)
    resp = HttpResponse(buffer.getvalue(), content_type='application/vnd.ms-excel')
    # 将中文处理成百分号编码
    filename = quote('违章记录汇总统计表.xlsx')
    # 设置HTTP响应头(设置下载文件并指定文件名)
    # resp['content_type']='application/vnd.ms-excel'
    resp['content-disposition'] = f'attachment; filename*=utf-8\'\'{filename}'
    return resp


def export_exce(request: HttpRequest) -> HttpResponse:
    queryset = Car.objects.all()
    print(queryset)
    wb = xlwt.Workbook()
    sheet = wb.add_sheet('人员与车牌号')
    titles = ('编号', '车牌号', '姓名', '车型')
    # style = xlwt.easyxf('font: height 720, color-index red')
    for co_index, title in enumerate(titles):
        sheet.write(0, co_index, title)
    for ro_index, car in enumerate(queryset):
        sheet.write(ro_index + 1, 0, car.no) # (style)
        sheet.write(ro_index + 1, 1, car.carno)
        sheet.write(ro_index + 1, 2, car.owner)
        sheet.write(ro_index + 1, 3, car.brand)
    buffer = io.BytesIO()
    wb.save(buffer)
    resp = HttpResponse(buffer.getvalue(), content_type='application/vnd.ms-excel')
    filename = quote('车表.xlsx')
    resp['content-disposition'] = f'attachment; filename*=utf8\'\'{filename}'
    return resp



def get_bar_data(request: HttpRequest) -> HttpResponse:
    xdata, ydata = [], []
    with connection.cursor() as cursor:
        cursor.execute('select carno, ifnull(total, 0) as total'
                       ' from tb_car t1 left outer join'
                       '(select car_id, count(no) as total '
                       'from tb_record group by car_id) t2'
                       ' on t1.no=t2.car_id')
        for row in cursor.fetchall():
            xdata.append(row[0])
            ydata.append(row[1])
    return JsonResponse({'xdata': xdata, 'ydata':ydata})
