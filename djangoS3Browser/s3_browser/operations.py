import boto3
import sys
from typing import List, Optional

from django.conf import settings

s3 = boto3.resource('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
s3client = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
"""
Big Note: for [1:]
-starts with the default "-" sign for the selected file location.
"""

"fetch the directories within the selected folder"


def _configured_buckets() -> List[dict]:
    configured = getattr(settings, "S3_BROWSER_BUCKETS", getattr(settings, "AWS_STORAGE_BUCKET_NAME", None))
    if not configured:
        return []
    if isinstance(configured, dict):
        return [{"label": label, "name": name} for label, name in configured.items()]
    if isinstance(configured, (list, tuple, set)):
        return [{"label": name, "name": name} for name in configured]
    return [{"label": str(configured), "name": str(configured)}]


def _resolve_bucket(bucket_name: Optional[str]) -> str:
    buckets = _configured_buckets()
    if bucket_name and any(bucket_name == b["name"] for b in buckets):
        return bucket_name
    return buckets[0]["name"] if buckets else settings.AWS_STORAGE_BUCKET_NAME


def _bucket_region(bucket_name: str) -> str:
    location = s3client.get_bucket_location(Bucket=bucket_name)
    return location.get('LocationConstraint') or 'us-east-1'


def get_folder_with_items(main_folder, sort_a_z, bucket_name=None):
    try:
        bucket_name = _resolve_bucket(bucket_name)
        sort_a_z = True if sort_a_z == "true" else False  # sorted method a to z/ z to a
        bucket_region = _bucket_region(bucket_name)
        result = s3client.list_objects_v2(Bucket=bucket_name, Prefix=main_folder[1:], Delimiter="/")
        result_files = get_files(main_folder, result.get('Contents'), sort_a_z, bucket_name, bucket_region) if result.get(
            'Contents') else []
        result_folders = get_folders(main_folder, result.get('CommonPrefixes'), sort_a_z, bucket_name, bucket_region) if result.get(
            'CommonPrefixes') else []
        return result_folders + result_files  # return files and folders
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)


def get_files(main_folder, result, sort_a_z, bucket_name, bucket_region):
    try:
        files_list = []
        for obj in result:
            # main_folder[1:] exp; -folder1/folder2 => delete "-"
            if main_folder[1:] != obj.get('Key'):  # if obj is not folder item
                object_url = "https://s3-{0}.amazonaws.com/{1}/{2}".format(bucket_region, bucket_name, obj.get('Key'))
                # for template file icon
                icon_list = [
                    'ai.png', 'audition.png', 'avi.png', 'bridge.png', 'css.png', 'csv.png', 'dbf.png', 'doc.png',
                    'dreamweaver.png', 'dwg.png', 'exe.png', 'file.png', 'fireworks.png', 'fla.png', 'flash.png',
                    'folder_icon.png', 'html.png', 'illustrator.png', 'indesign.png', 'iso.png', 'javascript.png',
                    'jpg.png', 'json-file.png', 'mp3.png', 'mp4.png', 'pdf.png', 'photoshop.png', 'png.png',
                    'ppt.png', 'prelude.png', 'premiere.png', 'psd.png', 'rtf.png', 'search.png', 'svg.png',
                    'txt.png', 'xls.png', 'xml.png', 'zip.png', 'zip-1.png']
                img_file_list = ['ani', 'bmp', 'cal', 'fax', 'gif', 'img', 'jbg', 'jpg', 'jpe', 'mac', 'pbm',
                                 'pcd', 'pcx', 'pct', 'pgm', 'png', 'jpeg', 'ppm', 'psd', 'ras', 'tag', 'tif',
                                 'wmf']
                extension, icon = str(obj['Key'].split('.')[-1]).lower(), None
                if extension in img_file_list:
                    icon = object_url if extension in ['bmp', 'jpg', 'jpeg', 'png',
                                                       'gif'] else "/static/images/jpg.png"
                if not icon:
                    icon = "/static/images/" + extension + ".png" if extension + ".png" in icon_list else "/static/images/file.png"
                item_type = "folder" if obj.get('Key')[-1] == "/" else "other"  # for show template
                files_list.append(
                    {'key': obj.get('Key'), 'url': object_url, 'icon': icon,
                     'text': obj.get('Key')[len(main_folder) - 1:], 'type': item_type})
        return sorted(files_list, key=lambda k: str(k['key']).lower(), reverse=not sort_a_z)
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)


def get_folders(main_folder, result, sort_a_z, bucket_name, bucket_region):
    try:
        files_list = []
        for obj in result:
            icon = "/static/images/folder_icon.png"
            item_type = "folder"  # for show template
            url = obj.get('Prefix')
            files_list.append(
                {'key': obj.get('Prefix'), 'url': url, 'icon': icon,
                 'text': obj.get('Prefix')[len(main_folder) - 1:], 'type': item_type})
        return sorted(files_list, key=lambda k: str(k['key']).lower(), reverse=not sort_a_z)
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)


def generate_upload_post(location, file_name, bucket_name=None, content_type=None):
    try:
        bucket_name = _resolve_bucket(bucket_name)
        key = location[1:] + file_name
        params = {"Bucket": bucket_name, "Key": key}
        if content_type:
            params["Content-Type"] = content_type
        return s3client.generate_presigned_post(**params, ExpiresIn=900)
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        raise Exception('Upload Presign Failed! ', e)


def create_folder_item(location, folder_name, bucket_name=None):
    try:
        bucket_name = _resolve_bucket(bucket_name)
        if folder_name[-1] != "/":
            folder_name += "/"
        s3client.put_object(Bucket=bucket_name, Key=location[1:] + folder_name)
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        raise Exception('Create Folder Failed! ', e)


def generate_download_url(file, bucket_name=None):
    try:
        bucket_name = _resolve_bucket(bucket_name)
        return s3client.generate_presigned_url('get_object',
                                               Params={'Bucket': bucket_name, 'Key': file[1:]},
                                               ExpiresIn=900)
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        raise Exception('Download Failed! ', e)


def rename(location, file, new_name, bucket_name=None):
    try:
        bucket_name = _resolve_bucket(bucket_name)
        if file[-1] == "/" and new_name[-1] != "/":  # if file format exception
            new_name += "/"
        s3client.copy_object(Bucket=bucket_name,
                             CopySource={'Bucket': bucket_name, 'Key': location[1:] + file},
                             Key=new_name)
        s3client.delete_object(Bucket=bucket_name, Key=location[1:] + file)
        return location[1:] + new_name
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        raise Exception('Rename Failed! ', e)


def paste(location, file_list, bucket_name=None):
    try:
        bucket_name = _resolve_bucket(bucket_name)
        for file in file_list:
            s3client.copy_object(Bucket=bucket_name,
                                 CopySource={'Bucket': bucket_name, 'Key': file[1:]},
                                 Key=location[1:] + file[1:].rsplit('/', 1)[-1])
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        raise Exception('Paste Failed! ', e)


def move(location, file_list, bucket_name=None):
    try:
        bucket_name = _resolve_bucket(bucket_name)
        for file in file_list:
            s3client.copy_object(Bucket=bucket_name,
                                 CopySource={'Bucket': bucket_name, 'Key': file[1:]},
                                 Key=location[1:] + file[1:].rsplit('/', 1)[-1])
            s3client.delete_object(Bucket=bucket_name, Key=file[1:])
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        raise Exception('Move Failed! ', e)


def delete(file_list, bucket_name=None):
    try:
        bucket_name = _resolve_bucket(bucket_name)
        for file in file_list:
            s3.Bucket(bucket_name).objects.filter(Prefix=file[1:]).delete()
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        raise Exception('Delete Failed! ', e)
