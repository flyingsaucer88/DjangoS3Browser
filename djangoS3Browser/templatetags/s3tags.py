from django import template
from django.conf import settings

from djangoS3Browser.s3_browser.operations import _configured_buckets, _resolve_bucket

register = template.Library()


@register.inclusion_tag("index.html")
def load_s3():
    buckets = _configured_buckets()
    return {
        "buckets": buckets,
        "default_bucket": _resolve_bucket(None) if buckets else getattr(settings, "AWS_STORAGE_BUCKET_NAME", ""),
    }


@register.inclusion_tag("header.html")
def load_s3_header():
    return {}
