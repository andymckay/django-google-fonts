`django-google-fonts` lets you use Google fonts in Django easily, by downloading, rewriting and caching the font and CSS files locally. 
README.md
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
    'django_google_fonts'
]
```

### Using

Tell Django which fonts you'd like:

```python
GOOGLE_FONTS = ["Kablammo", "Roboto"]
```

When Django starts it will grab the fonts from Google and store them in your `STATICFILES_DIRS` directory. It will rewrite the CSS that Google Fonts provides, so all you have to do is load the font like normal. For example:

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

Custom font weights are available by specifying the font weights in the URL. The easy way to do this is visit a font page, for example [Robot](https://fonts.google.com/specimen/Roboto) and then selecting the weights and styles you'd like. Then click on `Selected Families` and copy the font definition in.

For example Google will suggest embedding the font using this URL:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,100;0,700;0,900;1,700&display=swap" rel="stylesheet">
```

Roboto with italic in weights 100, 700, 900. To use this in Django you would specify:

```python
GOOGLE_FONTS = ["Roboto:ital,wght@0,100;0,700;1,700"]
```

And you would reference it in a stylesheet:

```html
<link rel="stylesheet" href="{% static 'fonts/roboto:ital,wght@0,100;0,700;1,700.css' %}">
```

#### Optional settings

By default `django-google-fonts` will store fonts in the first directory specified in `STATICFILES_DIRS`. That might not be where you want, so you can set a `GOOGLE_FONTS_DIR` setting if you'd like it be somewhere else:

```python
GOOGLE_FONTS_DIR = BASE_DIR / "fonts"
STATICFILES_DIRS = [BASE_DIR / "static", BASE_DIR / "fonts"]
```

The CSS file contains the path to the font and `django-google-fonts` tries to calculate what the path to the font should be by using the value of `STATIC_URL`. If that's wrong and you need it be something else, you can set that value:

```python
GOOGLE_FONTS_URL = "my-exotic-static/url/to-the-fonts"
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
