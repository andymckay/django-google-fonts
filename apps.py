import logging
import os

import requests
import tinycss2
from django.apps import AppConfig
from django.conf import settings

logger = logging.getLogger(__name__)
# pylint: disable=logging-fstring-interpolation
# Google Fonts produces a different CSS based on the user agent, using the Chrome user agent seems to give us a nice CSS compatible with browsers.
# But in case you can override this by setting the GOOGLE_FONTS_USER_AGENT setting.
user_agent = getattr(
    settings,
    "GOOGLE_FONTS_USER_AGENT",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
)
css_url = "https://fonts.googleapis.com/css"
css_prefix = "https://fonts.gstatic.com/s/"
log_prefix = "django_google_fonts"

fonts = []


class Font:
    __slots__ = ["name", "dest", "slug"]

    def __init__(self, name, dest):
        self.name = name
        self.slug = self.name.replace(" ", "").lower()
        self.dest = os.path.join(dest, self.slug)

    def cached(self):
        return os.path.exists(self.dest)

    def get(self, name):
        res = requests.get(
            css_url,
            params={"family": name},
            headers={"User-Agent": user_agent},
            timeout=10,
        )
        if res.status_code != 200:
            logger.error(
                f"{log_prefix}: Failed to get font: {name}, got status code: {res.status_code}"
            )
            return

        output_css = []

        input_css = res.text
        rules = tinycss2.parse_stylesheet(input_css)

        for rule in rules:
            if rule.type == "at-rule":
                for line_number, line in enumerate(rule.content):
                    if line.type == "url":
                        res = requests.get(line.value)
                        if res.status_code != 200:
                            logger.error(
                                f"{log_prefix}: Failed to get font: {name}, got status code: {res.status_code}"
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

                        line.representation = line.representation.replace(
                            # Need to figure out what to do here? Just a setting change?
                            "https://fonts.gstatic.com/s/", "/static/fonts/"
                        )
                        output_css.append(rule)

        output_css_file = os.path.join(self.dest, f"{self.slug}.css")
        with open(output_css_file, "w", encoding="utf-8") as f:
            f.write(tinycss2.serialize(output_css))


class DjangoGoogleFontsConfig(AppConfig):
    name = "django_google_fonts"

    def ready(self):
        fonts = getattr(settings, "GOOGLE_FONTS", [])
        if not fonts:
            logger.error(f"{log_prefix}: No fonts specified in GOOGLE_FONTS setting.")
            return

        for k, font in enumerate(fonts):
            if any([word.islower() for word in font.split(" ")]):
                logger.warning(
                    f"{self.name}: Font families usually have capitalized first letters, check the spelling of {font}."
                )

        dest = getattr(settings, "GOOGLE_FONTS_DEST", None)
        if not dest:
            logger.error(
                f"{log_prefix}: No destination directory specified in GOOGLE_FONTS_DEST setting."
            )
            return

        if not os.path.exists(dest):
            logger.warning(
                f"{log_prefix}: The destination directory for the fonts: {dest} does not exist."
            )

        self.fonts = []
        for font in fonts:
            self.fonts.append(Font(font, dest))
