from flask import Response
import simplejson as json
import numpy as np

import datetime
import decimal


class DataTypeJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return str(obj)
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, np.int32):
            return int(obj)
        if isinstance(obj, np.int64):
            return int(obj)
        return json.JSONEncoder.default(self, obj)


def make_json_response(status=200, encoding='utf-8', **kwargs):
    doc = dict()

    if len(kwargs) > 0:
        for key, val in kwargs.items():
            doc[key] = val

    return Response(
        response=json.dumps(doc, cls=DataTypeJSONEncoder, separators=(',', ':'), encoding=encoding, ignore_nan=True),
        status=status,
        mimetype="application/json"
    )


class ResponseForm:
    def __init__(self, res=True, msg='', data=None, status=200):
        self.res = res
        self.msg = msg
        self.data = data
        self.status = status
