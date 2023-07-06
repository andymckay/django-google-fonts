import logging
import os

import requests
import tinycss2
from django.apps import AppConfig
from django.conf import settings

logger = logging.getLogger(__name__)
# pylint: disable=logging-fstring-interpolation invalid-name
# pylint: disable=missing-class-docstring missing-function-docstring
# Google Fonts produces a different CSS based on the user agent, using the Chrome user agent seems to give us a nice CSS compatible with browsers.
# But in case you can override this by setting the GOOGLE_FONTS_USER_AGENT setting.
user_agent = getattr(
    settings,
    "GOOGLE_FONTS_USER_AGENT",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
)
css_url = "https://fonts.googleapis.com/css2"
css_prefix = "https://fonts.gstatic.com/s/"
log_prefix = "django_google_fonts"
# Requests timeout in seconds.
timeout = 10
fonts = []


class Font:
    __slots__ = ["name", "dest", "slug", "dest_css"]

    def __init__(self, name, dest):
        self.name = name
        self.slug = self.name.replace(" ", "").lower()
        self.dest = dest
        self.dest_css = os.path.join(dest, self.slug + ".css")

    def cached(self):
        return os.path.exists(self.dest_css)

    def get(self):
        if self.cached():
            return

        res = requests.get(
            css_url,
            params={"family": self.name},
            headers={"User-Agent": user_agent},
            timeout=timeout,
        )
        if res.status_code != 200:
            logger.error(
                f"{log_prefix}: Failed to get font: {self.name}, got status code: {res.status_code}"
            )
            return

        output_css = []

        input_css = res.content.decode("utf-8")
        rules = tinycss2.parse_stylesheet(input_css)

        for rule in rules:
            if rule.type == "at-rule":
                for line in rule.content:
                    if line.type == "url":
                        res = requests.get(line.value, timeout=timeout)
                        if res.status_code != 200:
                            logger.error(
                                f"{log_prefix}: Failed to get font: {self.name}, got status code: {res.status_code}"
                            )
                            return

                        # Convert https://fonts.gstatic.com/s/opensans/v35/memSYaGs126MiZpBA-UvWbX2vVnXBbObj2OVZyOOSr4dVJWUgsjZ0B4gaVc.ttf
                        # To: /static/fonts/opensans/v35/memSYaGs126MiZpBA-UvWbX2vVnXBbObj2OVZyOOSr4dVJWUgsjZ0B4gaVc.ttf
                        # And save it to the right place.
                        target = line.value.split(css_prefix)[1]
                        dest = os.path.join(self.dest, *target.split("/"))
                        if not os.path.exists(os.path.dirname(dest)):
                            os.makedirs(os.path.dirname(dest))

                        with open(dest, "wb") as f:
                            f.write(res.content)

                        # STATIC_URL must have a trailing slash.
                        path = getattr(settings, "GOOGLE_FONTS_URL", f"{settings.STATIC_URL}fonts/")
                        line.representation = line.representation.replace(
                            "https://fonts.gstatic.com/s/", path
                        )
                        output_css.append(rule)

        with open(self.dest_css, "w", encoding="utf-8") as f:
            f.write(tinycss2.serialize(output_css))


class DjangoGoogleFontsConfig(AppConfig):
    name = log_prefix

    def ready(self):
        if not getattr(settings, "GOOGLE_FONTS", None):
            logger.error(f"{log_prefix}: Either STATIC_URL or GOOGLE_FONTS_URL must be set.")
            return

        if (
            getattr(settings, "STATIC_URL", None) is None
            and getattr(settings, "GOOGLE_FONTS_URL", None) is None
        ):
            logger.error(f"{log_prefix}: Either STATIC_URL or GOOGLE_FONTS_URL must be set.")
            return

        dest = getattr(settings, "GOOGLE_FONTS_DIR", None)
        if not dest:
            if not getattr(settings, "STATICFILES_DIRS", None):
                logger.error(f"{log_prefix}: STATICFILES_DIRS is required but not set.")
                return

            dest = settings.STATICFILES_DIRS[0]

        dest = os.path.join(dest, "fonts")
        if not os.path.exists(dest):
            os.makedirs(dest)

        self.fonts = []
        fonts = getattr(settings, "GOOGLE_FONTS", [])
        for font in fonts:
            if any([word.islower() for word in font.split(" ")]):
                logger.warning(
                    f"{self.name}: Font families usually have capitalized first letters, check the spelling of {font}."
                )

        for name in fonts:
            font = Font(name, dest)
            font.get()
            self.fonts.append(font)

        return True
