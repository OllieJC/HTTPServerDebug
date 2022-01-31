#!/usr/bin/env python3

import os
import json
import base64
import time
import logging

from flask import Flask, redirect, request, make_response
from flask_cors import CORS

_jlir = os.getenv("JSON_LOG_INCLUDE_RESPONSE", default="t").lower()
JSON_LOG_INCLUDE_RESPONSE = True if _jlir.startswith("t") or _jlir == "1" else False
CONFIG_PATH = os.getenv("CONFIG_PATH", "./config.json")

app = Flask(__name__)
cors = CORS(app, resources={"*": {"origins": "*", "supports_credentials": True}})
log = logging.getLogger("werkzeug")
log.disabled = True


def config() -> dict:
    res = {}

    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as j:
                res = json.loads(j.read())
        except Exception as e:
            jprint({f"error with {CONFIG_PATH}": e})

    return res


def jprint(obj) -> None:
    if type(obj) != dict:
        obj = {"message": str(obj)}

    if "_time" not in obj:
        obj["_time"] = time.time()

    print(json.dumps(obj, sort_keys=True, default=str))


def add_default_headers(resp):
    resp.headers["X-Robots-Tag"] = "noindex, nofollow, noimageindex"
    resp.headers["Cache-Control"] = "max-age=0, no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp


def client_ip():
    if request.environ.get("HTTP_X_FORWARDED_FOR") is None:
        return request.environ["REMOTE_ADDR"]
    else:
        return request.environ["HTTP_X_FORWARDED_FOR"]


def dhttp_req():
    req = {
        "headers": {k: v for k, v in request.headers.items()},
        "body": None,
        "method": request.method,
        "client_ip": client_ip(),
        "url": request.url,
        "error": None,
    }

    try:
        base64_bytes = base64.b64encode(request.get_data())
        req["body"] = base64_bytes.decode("ascii")
    except Exception as e:
        req["error"] = str(e)

    return req


def jhttp_log(request=None, response=None):
    log_items = {"request": request}

    if JSON_LOG_INCLUDE_RESPONSE:
        resp_dict = None
        if response:
            # print(dir(response))
            resp_dict = {
                "headers": {k: v for k, v in response.headers.items()},
                "status_desc": response.status,
                "status_code": response.status_code,
                "body": None,
            }

        try:
            base64_bytes = base64.b64encode(response.get_data())
            resp_dict["body"] = base64_bytes.decode("ascii")
        except Exception as e:
            resp_dict["error"] = str(e)

        log_items["response"] = resp_dict

    jprint(log_items)


@app.route("/", methods=["POST", "GET"])
@app.route("/<path:path>", methods=["POST", "GET"])
def main(path=None):
    return response_from_config(
        path=request.path,
        method=request.method.upper(),
        headers=request.headers,
        host=request.host,
    )


def response_from_config(path: str, method: str, headers: str, host: str):
    c = config()
    res = None
    do_log = True

    req_dict = dhttp_req()

    this_path = None
    if path in c:
        this_path = path
    elif "*" in c:
        this_path = "*"

    if this_path:
        this_method = None
        if method in c[this_path]:
            this_method = method
        elif method.lower() in c[this_path]:
            this_method = method.lower()
        elif "*" in c[this_path]:
            this_method = "*"

        if this_method:
            t = c[this_path][this_method]

            body = ""
            if "body" in t:
                body = t["body"]
            elif "request_as_body" in t and t["request_as_body"]:
                body = f"<pre>{json.dumps(req_dict, indent=2, default=str)}</pre>"

            res = make_response(body)

            default_headers = True
            if "default_headers" in t and t["default_headers"] == False:
                default_headers = False
            if default_headers:
                res = add_default_headers(res)

            if "headers" in t:
                for header in t["headers"]:
                    res.headers[header] = str(t["headers"][header])

            if "status_code" in t:
                res.status = int(t["status_code"])

            res.autocorrect_location_header = False

            if "do_log_request" in t and t["do_log_request"] == False:
                do_log_request = False

    if not res:
        res = add_default_headers(make_response(""))

    if do_log:
        jhttp_log(req_dict, res)

    return res


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.getenv("PORT", 5000))
