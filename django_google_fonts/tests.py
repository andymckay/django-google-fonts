import os
import tempfile
from unittest.mock import ANY, patch

from django.conf import settings
from django.test import TestCase

from .apps import DjangoGoogleFontsConfig, Font


class Stub(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


roboto_css = """/* cyrillic-ext */
@font-face {
  font-family: 'Roboto';
  font-style: normal;
  font-weight: 400;
  src: url(https://fonts.gstatic.com/s/roboto/v30/KFOmCnqEu92Fr1Mu72xKKTU1Kvnz.woff2) format('woff2');
  unicode-range: U+0460-052F, U+1C80-1C88, U+20B4, U+2DE0-2DFF, U+A640-A69F, U+FE2E-FE2F;
}
"""

get_mock_params = {"params": {"family": "Roboto"}, "headers": {"User-Agent": ANY}, "timeout": 10}
get_mock_url = "https://fonts.googleapis.com/css"


class TestFont(TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.tempdir_path = self.tempdir.name
        self.font = Font("Roboto", self.tempdir_path)

    @patch("django_google_fonts.apps.requests")
    def test_cache(self, mock_requests):
        mock_requests.get.return_value = Stub(status_code=200, content="".encode("utf-8"))
        self.font.get()
        self.assertEqual(self.font.cached(), True)
        self.font.get()
        mock_requests.get.assert_called_once_with(get_mock_url, **get_mock_params)

    @patch("django_google_fonts.apps.requests")
    def test_rewrites(self, mock_requests):
        mock_requests.get.return_value = Stub(status_code=200, content=roboto_css.encode("utf-8"))
        self.font.get()
        with open(self.font.dest_css, "r", encoding="utf-8") as f:
            data = f.read()
            self.assertIn("url(/static/fonts/roboto/", data)
        mock_requests.get.assert_called_with(
            "https://fonts.gstatic.com/s/roboto/v30/KFOmCnqEu92Fr1Mu72xKKTU1Kvnz.woff2", timeout=10
        )

    @patch("django_google_fonts.apps.requests")
    def test_uses_google_fonts_url(self, mock_requests):
        mock_requests.get.return_value = Stub(status_code=200, content=roboto_css.encode("utf-8"))
        with self.settings(GOOGLE_FONTS_URL="blah/"):
            self.font.get()
        with open(self.font.dest_css, "r", encoding="utf-8") as f:
            data = f.read()
            self.assertIn("url(blah/roboto/", data)


class TestDjangoGoogleFontsConfig(TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.tempdir_path = self.tempdir.name
        self.obj = DjangoGoogleFontsConfig(
            "django_google_fonts", Stub(__path__=["a"], __file__="b/__init__.py")
        )
        super().setUp()

    @patch("django_google_fonts.apps.requests")
    def test_good_path(self, mock_requests):
        with self.settings(
            GOOGLE_FONTS=["Roboto"],
            STATIC_URL="static/",
            STATICFILES_DIRS=[os.path.join(self.tempdir_path, "static/"), "tmp"],
        ):
            mock_requests.get.return_value = Stub(status_code=200, content="".encode("utf-8"))
            res = self.obj.ready()
            self.assertEqual(res, True)
            self.assertEqual(len(self.obj.fonts), 1)
            self.assertEqual(self.obj.fonts[0].name, "Roboto")
            self.assertEqual(
                self.obj.fonts[0].dest, os.path.join(self.tempdir_path, "static/fonts")
            )
            self.assertEqual(
                self.obj.fonts[0].dest_css,
                os.path.join(self.tempdir_path, "static/fonts/roboto.css"),
            )
            self.assertEqual(self.obj.fonts[0].slug, "roboto")
            mock_requests.get.assert_called_once_with(get_mock_url, **get_mock_params)

    def test_no_staticfiles(self):
        with self.settings(
            GOOGLE_FONTS=["Roboto"],
            STATICFILES_DIRS=None,
        ):
            res = self.obj.ready()
            self.assertEqual(res, None)

    def test_no_google_fonts(self):
        with self.settings(
            GOOGLE_FONTS=None,
        ):
            res = self.obj.ready()
            self.assertEqual(res, None)

    def test_no_static_url(self):
        with self.settings(
            GOOGLE_FONTS=["Roboto"],
            GOOGLE_FONTS_URL=None,
            STATIC_URL=None,
        ):
            res = self.obj.ready()
            self.assertEqual(res, None)

    @patch("django_google_fonts.apps.requests")
    def test_no_staticfiles_but_google_fonts(self, mock_requests):
        with self.settings(
            GOOGLE_FONTS=["Roboto"],
            STATICFILES_DIRS=None,
            GOOGLE_FONTS_DIR=self.tempdir_path,
        ):
            mock_requests.get.return_value = Stub(status_code=200, content="".encode("utf-8"))
            res = self.obj.ready()
            self.assertEqual(res, True)
