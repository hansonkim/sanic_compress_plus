# sanic_compress_plus

sanic_compress_plus is an extension which allows you to easily gzip and brotli your Sanic responses. It is a fork of the [sanic_compress](https://github.com/subyraman/sanic_compress) package which is a port of the [Flask-Compress](https://github.com/libwilliam/flask-compress) extension.

Read this in other languages: [English](README.md), [한국어](README.ko.md)

## Installation

Install with `pip`:

`pip install sanic_compress_plus`

## Usage

Usage is simple. Simply pass in the Sanic app object to the `Compress` class, and responses will be gzipped.

```python
from sanic import Sanic
from sanic_compress_plus import Compress

app = Sanic(__name__)
Compress(app)
```

## Options

Within the Sanic application config you can provide the following settings to control the behavior of sanic_compress. None of the settings are required.


`COMPRESS_MIMETYPES`: Set the list of mimetypes and support encodings to compress here.
- Default: `{
    "text/csv": ["br", "gzip"],
    "text/html": ["br", "gzip"],
    "application/json": ["br", "gzip"],
}`

`COMPRESS_LEVEL`: Specifies the gzip compression level (1-9).
- Default: `6`

`COMPRESS_MIN_SIZE`: Specifies the minimum size (in bytes) threshold for compressing responses.
- Default: `500`

A higher `COMPRESS_LEVEL` will result in a gzipped response that is smaller, but the compression will take longer.

Example of using custom configuration:

```python
from sanic import Sanic
from sanic_compress_plus import Compress

app = Sanic(__name__)
app.config['COMPRESS_MIMETYPES'] = {'text/html': ["gzip", "br"], 'application/json': ["br", "gzip"]}
app.config['COMPRESS_LEVEL'] = 4
app.config['COMPRESS_MIN_SIZE'] = 300
Compress(app)
```

### Note about gzipping static files:

Sanic is not at heart a file server. You should consider serving static files with nginx or on a separate file server.
