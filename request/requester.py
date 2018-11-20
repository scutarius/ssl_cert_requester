import http.client
import ssl
import urllib

import json as _json


class SessionHTTPS(object):

    @staticmethod
    def _create_ssl_context(cert, passphrase):
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        context.load_cert_chain(cert, password=passphrase)
        context.verify_mode = ssl.CERT_NONE
        return context

    @staticmethod
    def _get_response(connection):
        response = connection.getresponse()
        data = response.read().decode()
        if data.startswith('xml', 2, 5):
            return data
        if data.startswith('html', 1, 5):
            return data
        return _json.loads(data)

    def __init__(self, host, port, cert, passphrase, timeout=30):
        context = self._create_ssl_context(cert, passphrase)
        self.connection = http.client.HTTPSConnection(host, port=port, context=context, timeout=timeout)

    def __enter__(self):
        return self

    def __exit__(self, _type, _value, _traceback):
        self.close()

    def __call__(self, method, url_path, params=None, body=None, json=None, headers=None):
        if body and json:
            raise "You must send json or body, not both"
        if json:
            body = _json.dumps(json)
        if params:
            url_path += '?%s' % urllib.parse.urlencode(params)
        if not method.isupper():
            method = method.upper()

        self.connection.request(method, url_path, body=body, headers=headers)
        return self._get_response(self.connection)

    def close(self):
        self.connection.close()


class Requester(object):

    @staticmethod
    def __request(method, url, params=None, body=None, json=None, headers=None, cert=None, passphrase=None, timeout=15):
        parse = urllib.parse.urlparse(url)
        (host, port) = urllib.parse.splitport(parse.netloc)
        if parse.scheme == 'https':
            with SessionHTTPS(host, port, cert, passphrase, timeout) as session:
                return session(method, parse.path, params, body, json, headers)

    @classmethod
    def get(cls, url, params=None, **kwargs):
        return cls.__request('GET', url, params=params, **kwargs)

    @classmethod
    def post(cls, url, data=None, json=None, **kwargs):
        return cls.__request('POST', url, body=data, json=json, **kwargs)

    @classmethod
    def put(cls, url, **kwargs):
        return cls.__request('PUT', url, **kwargs)

    @classmethod
    def delete(cls, url, **kwargs):
        return cls.__request('DELETE', url, **kwargs)
