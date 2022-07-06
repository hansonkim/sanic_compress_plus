# sanic_compress_plus

sanic_compress_plus 는 Sanic 프레임워크의 응답을 gzip 또는 brotli 를 통해 압축해주는 확장 프로그램입니다.
[sanic_compress](https://github.com/subyraman/sanic_compress)를 fork 하였으며, sanic_compress는 [Flask-Compress](https://github.com/libwilliam/flask-compress) 를 포팅하였습니다.

Read this in other languages: [English](README.md), [한국어](README.ko.md)


## Installation

Install with `pip`:

`pip install sanic_compress_plus`

## Usage

사용법은 쉽습니다. Compress에 sanic app 객체를 전달하여 생성하면 됩니다.

```python
from sanic import Sanic
from sanic_compress_plus import Compress

app = Sanic(__name__)
Compress(app)
```

## Options

Within the Sanic application config you can provide the following settings to control the behavior of sanic_compress. None of the settings are required.
Sanic application config 로 아래와 sanic_compress_plus 를 설정할 수 있습니다. 설정은 필수가 아닙니다.   


`COMPRESS_MIMETYPES`: mimetype 과 지원하는 encoding 의 우선순위에 따라 list 로 설정가능합니다.
- Default: `{
    "text/csv": ["br", "gzip"],
    "text/html": ["br", "gzip"],
    "application/json": ["br", "gzip"],
}`

`COMPRESS_LEVEL`: gzip 압축 레벨 (1-9).
- Default: `6`

`COMPRESS_MIN_SIZE`: min_size 이상일 경우에만 압축합니다. bytes 단위 입니다.
- Default: `500`

`COMPRESS_LEVEL` 값을 높일 수록 압축된 결과물은 작아지지만, 응답속도는 느려집니다.

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

Sanic 을 파일 서버로 사용하는 것은 적절하지 않습니다. 정적 파일을 제공은 nginx 와 같은 파일 서버를 사용하세요.
