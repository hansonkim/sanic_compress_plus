import uuid

import pytest
from sanic import Sanic
from sanic.response import html, json, HTTPResponse
from sanic_compress_plus import Compress

OTHER_COMPRESSIBLE_TYPES = set(["text/csv", "application/json"])

BUNCH_OF_TYPES = OTHER_COMPRESSIBLE_TYPES.union(
    [
        "image/png",
        "application/pdf",
        "image/jpeg",
    ]
)

ENCODINGS = ["br", "gzip"]

CONTENT_LENGTHS = [100, 499, 500]
HEADERS = [
    {"Accept-Encoding": "gzip"},
    {"Accept-Encoding": "br"},
    {"Accept-Encoding": "br, gzip"},
]

STATUSES = [200, 201, 400, 401, 500]

VARY_HEADERS = ["Accept-Encoding", "Referer", "Cookie"]


@pytest.mark.parametrize("headers", HEADERS)
@pytest.mark.parametrize("content_length", CONTENT_LENGTHS)
def test_sets_gzip_for_html(app: Sanic, headers: dict, content_length: int):
    request, response = app.test_client.get(f"/html/{content_length}", headers=headers)

    if (
            "br" in headers.get("Accept-Encoding")
            and content_length >= app.config["COMPRESS_MIN_SIZE"]
    ):
        assert response.headers["Content-Encoding"] == "br"
        assert response.headers["Content-Length"] < str(content_length)
    elif (
            "gzip" in headers.get("Accept-Encoding")
            and content_length >= app.config["COMPRESS_MIN_SIZE"]
    ):
        assert response.headers["Content-Encoding"] == "gzip"
        assert response.headers["Content-Length"] < str(content_length)
    else:
        assert response.headers["Content-Length"] == str(content_length)
        assert "Content-Encoding" not in response.headers


@pytest.fixture
def app():
    app = Sanic(name="compressed")
    Compress(app)

    @app.route("/json/<length>")
    async def j(request, length):
        data = {"a": "".join(["b"] * (int(length) - 8))}
        return json(data)

    @app.route("/html/<length>")
    async def h(request, length):
        res = "".join(["h" for i in range(int(length))])
        return html(res)

    @app.route("/html/status/<status>")
    async def h_with_status(request, status):
        res = "".join(["h" for i in range(501)])
        return html(res, status=int(status))

    @app.route("/html/vary/<vary>")
    async def h_with_vary(request, vary):
        res = "".join(["h" for i in range(501)])
        return html(res, headers={"Vary": vary})

    @app.route("/other/<length>")
    async def other(request, length):
        content_type = request.args.get("content_type")
        body = "".join(["h" for i in range(int(length))])
        return HTTPResponse(body, content_type=content_type)

    return app


@pytest.mark.parametrize("headers", HEADERS)
@pytest.mark.parametrize("content_length", CONTENT_LENGTHS)
def test_gzip_for_json(app: Sanic, headers: dict, content_length: int):
    request, response = app.test_client.get(f"/json/{content_length}", headers=headers)

    if (
            "br" in headers.get("Accept-Encoding")
            and content_length >= app.config["COMPRESS_MIN_SIZE"]
    ):
        assert response.headers["Content-Encoding"] == "br"
        assert response.headers["Content-Length"] < str(content_length)
    elif (
            "gzip" in headers.get("Accept-Encoding")
            and content_length >= app.config["COMPRESS_MIN_SIZE"]
    ):
        assert response.headers["Content-Encoding"] == "gzip"
        assert response.headers["Content-Length"] < str(content_length)
    else:
        assert response.headers["Content-Length"] == str(content_length)
        assert "Content-Encoding" not in response.headers


@pytest.mark.parametrize("headers", HEADERS)
@pytest.mark.parametrize("content_length", CONTENT_LENGTHS)
@pytest.mark.parametrize("content_type", BUNCH_OF_TYPES)
def test_gzip_for_others(
        app: Sanic, content_type: str, headers: dict, content_length: int
):
    request, response = app.test_client.get(
        "/other/{}".format(content_length),
        headers=headers,
        params={"content_type": content_type},
    )

    if (
            "br" in headers.get("Accept-Encoding")
            and content_length >= app.config["COMPRESS_MIN_SIZE"]
            and content_type in OTHER_COMPRESSIBLE_TYPES
    ):
        assert response.headers["Content-Encoding"] == "br"
        assert response.headers["Content-Length"] < str(content_length)
    elif (
            "gzip" in headers.get("Accept-Encoding")
            and content_length >= app.config["COMPRESS_MIN_SIZE"]
            and content_type in OTHER_COMPRESSIBLE_TYPES
    ):
        assert response.headers["Content-Encoding"] == "gzip"
        assert response.headers["Content-Length"] < str(content_length)
    else:
        assert response.headers["Content-Length"] == str(content_length)
        assert "Content-Encoding" not in response.headers


@pytest.mark.parametrize("status", STATUSES)
@pytest.mark.parametrize("encodings", ENCODINGS)
def test_no_gzip_for_invalid_status(app: Sanic, status: int, encodings: str):
    request, response = app.test_client.get(
        "/html/status/{}".format(status), headers={"Accept-Encoding": "gzip"}
    )

    if status < 200 or status >= 300:
        assert "Content-Encoding" not in response.headers
    else:
        assert response.headers["Content-Encoding"] == "gzip"


def test_gzip_levels_work(app: Sanic):
    prev = None
    for i in range(1, 10):
        app.config["COMPRESS_LEVEL"] = i

        request, response = app.test_client.get(
            "/html/501", headers={"Accept-Encoding": "gzip"}
        )

        if prev:
            print(response.headers["Content-Length"])
            assert (
                    response.headers["Content-Length"] < prev
            ), "compression level {} should be smaller than {}".format(i, i - 1)


@pytest.mark.parametrize("vary", VARY_HEADERS)
def test_vary_header_modified(app: Sanic, vary: str):
    request, response = app.test_client.get(
        f"/html/vary/{vary}",
        headers={
            "Accept-Encoding": "gzip",
        },
    )

    if vary:
        if "accept-encoding" not in vary.lower():
            assert response.headers["Vary"] == f"{vary}, Accept-Encoding"
    else:
        assert response.headers["Vary"] == "Accept-Encoding"
