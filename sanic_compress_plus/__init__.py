"""
sanic compress 참조하여 brotli 도 지원하도록 수정함
https://github.com/subyraman/sanic_compress/blob/master/sanic_compress/__init__.py
"""

import gzip

import brotli

# mime type : [compressor...] index가 낮을 수록 우선순위가 높다.
DEFAULT_MIME_TYPES_AND_COMPRESS = {
    "text/csv": ["br", "gzip"],
    "text/html": ["br", "gzip"],
    "application/json": ["br", "gzip"],
}


class Compress(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        defaults = [
            ("COMPRESS_MIMETYPES", DEFAULT_MIME_TYPES_AND_COMPRESS),
            ("GZIP_COMPRESS_LEVEL", 6),
            ("COMPRESS_MIN_SIZE", 500),
        ]

        for k, v in defaults:
            app.config.setdefault(k, v)

        @app.middleware("response")
        async def compress_response(request, response):
            return await self._compress_response(request, response)

    async def _compress_response(self, request, response):
        accept_encoding = request.headers.get("Accept-Encoding", "")
        content_length = len(response.body)
        content_type = response.content_type
        mime_compressor_pairs = self.app.config["COMPRESS_MIMETYPES"]

        compressive_type = set()
        available_encoding = set()
        for k, v in mime_compressor_pairs.items():
            compressive_type.add(k)
            available_encoding = available_encoding | set(v)

        if ";" in response.content_type:
            content_type = content_type.split(";")[0]

        if (
            content_type not in compressive_type
            or not any([enc in accept_encoding for enc in available_encoding])
            or not 200 <= response.status < 300
            or (
                content_length is not None
                and content_length < self.app.config["COMPRESS_MIN_SIZE"]
            )
            or "Content-Encoding" in response.headers
        ):
            return response

        encoding = self.negotiate_contents(accept_encoding, content_type)
        compressed = self.compress(response, encoding)
        response.body = compressed

        response.headers["Content-Encoding"] = encoding
        response.headers["Content-Length"] = len(response.body)

        vary = response.headers.get("Vary")
        if vary:
            if "accept-encoding" not in vary.lower():
                response.headers["Vary"] = "{}, Accept-Encoding".format(vary)
        else:
            response.headers["Vary"] = "Accept-Encoding"

        return response

    def compress(self, response, encoding: str):
        if "gzip" == encoding:
            out = gzip.compress(
                response.body, compresslevel=self.app.config["GZIP_COMPRESS_LEVEL"]
            )
        else:  # "br" == encoding
            out = brotli.compress(response.body)

        return out

    def negotiate_contents(self, accept_encoding: str, content_type: str):
        # ex) br, gzip
        encoding_priorities = self.app.config["COMPRESS_MIMETYPES"][content_type]

        # ex) br, deflate, gzip
        accept_encodings = [i.strip() for i in accept_encoding.split(",")]
        for encoding in encoding_priorities:
            if encoding in accept_encodings:
                return encoding

        return "br"  # default encoding
