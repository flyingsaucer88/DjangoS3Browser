import json

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .operations import create_folder_item, delete, generate_download_url, generate_upload_post, get_folder_with_items, move, paste, rename

"fetch the directories within the selected folder"


def get_folder_items(request, main_folder, sort_a_z):
    bucket_name = request.GET.get('bucket')
    json_string = get_folder_with_items(main_folder, sort_a_z, bucket_name=bucket_name)
    return HttpResponse(json.dumps(json_string), content_type="application/json")


@csrf_exempt
def upload(request):
    bucket_name = request.POST.get('bucket')
    file_name = request.POST.get('file_name')
    upload_data = generate_upload_post(request.POST['loc'], file_name, bucket_name, request.POST.get('content_type'))
    return JsonResponse(upload_data, status=200)


@csrf_exempt
def create_folder(request):
    bucket_name = request.POST.get('bucket')
    create_folder_item(request.POST['loc'], request.POST['folder_name'], bucket_name=bucket_name)
    return HttpResponse(json.dumps("OK"), content_type="application/json", status=200)


@csrf_exempt
def download(request):
    file = request.GET.get('file')
    bucket_name = request.GET.get('bucket')
    url = generate_download_url(file, bucket_name=bucket_name)
    return JsonResponse({"url": url})


@csrf_exempt
def rename_file(request):
    bucket_name = request.POST.get('bucket')
    file_name = rename(request.POST['loc'], request.POST['file'], request.POST['new_name'], bucket_name=bucket_name)
    return HttpResponse(json.dumps(file_name), content_type="application/json", status=200)


@csrf_exempt
def paste_file(request):
    bucket_name = request.POST.get('bucket')
    paste(request.POST['loc'], request.POST.getlist('file_list[]'), bucket_name=bucket_name)
    return HttpResponse(json.dumps("OK"), content_type="application/json", status=200)


@csrf_exempt
def move_file(request):
    bucket_name = request.POST.get('bucket')
    move(request.POST['loc'], request.POST.getlist('file_list[]'), bucket_name=bucket_name)
    return HttpResponse(json.dumps("OK"), content_type="application/json", status=200)


@csrf_exempt
def delete_file(request):
    bucket_name = request.POST.get('bucket')
    delete(request.POST.getlist('file_list[]'), bucket_name=bucket_name)
    return HttpResponse(json.dumps("OK"), content_type="application/json", status=200)
