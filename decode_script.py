import base64, pathlib
b64 = "… string from the response …"
pathlib.Path("aligned.jpg").write_bytes(base64.b64decode(b64))