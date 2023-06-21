import logging

from django import template
from django.apps import apps
from django.core.cache import cache

from django_google_fonts.apps import log_prefix

logger = logging.getLogger(__name__)
register = template.Library()


@register.simple_tag
def font_css(name):
    fonts = apps.get_app_config("django_google_fonts").fonts
    cache_key = f"{log_prefix}:font:{name}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    for font in fonts:
        if font.name == name:
            try:
                data = open(font.dest_css, "r", encoding="utf-8").read()
                cache.set(cache_key, data)
                return data
            except FileNotFoundError:
                logger.error(f"{log_prefix}: Failed to get find css for font: {name}")
