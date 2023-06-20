`django-google-fonts` lets you use Google fonts in Django easily, with caching of the font files locally. 

This means that you can have all the benefits of using Google Fonts, but with added privacy and security for your users, because all the requests for the fonts will be on the same domain and not hitting Google servers.

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

Tell Django where to store the font files, usually this will be somewhere inside your `STATIC_DIRS` for example:

```python
GOOGLE_FONTS_DEST = BASE_DIR / "static" / "fonts"
STATICFILES_DIRS = [BASE_DIR / "static"]
```

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

There is also an optional `font` tag that will return the CSS:

```html
    {% load google_fonts %}
    {% font "Pathway Extreme" %}
```

### Names

Google fonts normally have title cased names, with capitalized first names [^1]. For example `Pathway Extreme`. Google normalises this too: `pathwayextreme` and this is used in file names. So in the case of `Pathway Extreme`

|Where|Name|
|-|-|
|Settings file|`Pathway Extreme`|
|Font tag|`Pathway Extreme`|
|Static tag|`pathwayextreme`|

[^1]: Font's like `IBM Plex Sans` have more capital letters than just the first letter.