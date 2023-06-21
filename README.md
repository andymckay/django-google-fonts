`django-google-fonts` lets you use Google fonts in Django easily, by downloading, rewriting and caching the font and CSS files locally. 

This means that you can have all the benefits of using Google Fonts, but with added privacy, security and speed for your users, because all the requests for the fonts will be on your domain and not hitting Google servers.

When the server restarts it will check if any fonts are missing locally and load them if they are. So there is no impact or performance considerations. After that initial download of the fonts, `django-google-fonts` does not need to make any more requests to Google servers, working totally offline from the Google servers.

### Installing

```bash
pip install django-google-fonts
```

Then add to your Django settings file:

```python
INSTALLED_APPS = [
    ...
    `django_google_fonts`
]
```

### Using

Tell Django which fonts you'd like:

```python
GOOGLE_FONTS = ["Kablammo", "Roboto"]
```

When Django starts it will grab the fonts from Google and store them in the `GOOGLE_FONTS_DEST`. It will rewrite the CSS that Google Fonts provides, so all you have to do is load the font like normal. For example:

```html
<link rel="stylesheet" href="{% static 'fonts/pathwayextreme.css' %}">
<style>
    body {
        font-family: 'Pathway Extreme';
    }
</style>
```

There is also a `font` tag that will return the raw CSS:

```html
    {% load google_fonts %}
    {% font_css "Pathway Extreme" %}
```

#### Optional settings

By default `django-google-fonts` will store fonts in the first directory specified in `STATICFILES_DIRS`. That might not be where you want, so you can set a `GOOGLE_FONTS_DIR` setting if you'd like it be somewhere else:

```python
GOOGLE_FONT_DIR = BASE_DIR / "fonts"
STATICFILES_DIRS = [BASE_DIR / "static", BASE_DIR / "fonts"]
```

The CSS file contains the path to the font and `django-google-fonts` tries to calculate what the path to the font should be by using the value of `STATIC_URL`. If that's wrong and you need it be something else, you can set that value:

```python
GOOGLE_FONT_URL = "my-exotic-static/url/to-the-fonts"
```

### Names

Google fonts normally have title cased names, with capitalized first names [^1]. For example `Pathway Extreme`. Google normalises this too: `pathwayextreme` and this is used in file names. So in the case of `Pathway Extreme`

|Where|Name|
|-|-|
|Settings file|`Pathway Extreme`|
|Font tag|`Pathway Extreme`|
|Static tag|`pathwayextreme`|

[^1]: Font's like `IBM Plex Sans` have more capital letters than just the first letter.

If you are unsure you can get at the fonts programatically, for example:

```python
>>> from django.apps import apps
>>> for font in apps.get_app_config("django_google_fonts").fonts:
...   print(font.name, font.slug, font.dest)
...
Kablammo kablammo /Users/a/c/examplefonts/static/fonts/kablammo
Roboto roboto /Users/a/c/examplefonts/static/fonts/roboto
```
