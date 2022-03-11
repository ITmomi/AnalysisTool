import json
import logging
import os
import re
import traceback

import requests

from config import app_config
from service.converter.exception import RapidConnectionError

log = logging.getLogger(app_config.LOG)


class RapidConnector:

    def __init__(self, config, print_log=None):
        self.config = config
        self.context = dict()
        if not print_log:
            self.log = log.info
        else:
            self.log = print_log

    def get_plans(self):
        self.log('get_plans')
        if not self.get_access_token():
            self.log('failed to get access token')
            return None

        header = self.create_request_header()
        url = self.create_request_url() + '/rss/api/plans'
        response = requests.get(url, headers=header)
        if response.status_code != 200:
            self.log('failed to get plan list (response=%d)' % response.status_code)
            return None
        body = json.loads(response.text)
        return body['lists']

    def get_access_token(self):
        try:
            url = self.create_request_url() + '/rss/api/auths/login'
            url = url + '?username=%s&password=%s' % (self.config['user'], self.config['password'])
            response = requests.get(url)
            if response.status_code == 200:
                body = json.loads(response.text)
                if 'accessToken' in body:
                    self.context['access_token'] = body['accessToken']
                    return True
                elif 'refreshToken' in body:
                    url = self.create_request_url() + '/rss/api/auths/token'
                    response = requests.post(url, data={'refreshToken': body['refreshToken']})
                    if response.status_code == 200:
                        body = json.loads(response)
                        if 'accessToken' in body:
                            self.context['access_token'] = body['accessToken']
                            return True
            self.log('failed to login and get access token (code=%d)' % response.status_code)
        except Exception as msg:
            self.log(f'connection failed. {msg}')
            self.log(traceback.format_exc())
            raise RapidConnectionError('access token error')
        return False

    def get_download_list(self, plan_id):
        return self.io_bus(self._get_download_list, {'plan_id': plan_id})

    def download_file(self, url, dest):
        return self.io_bus(self._download_file, {'url': url, 'dest': dest})

    def get_machines(self):
        return self.io_bus(self._get_machines, {})

    def me(self):
        return self.io_bus(self._me, {})

    def _get_download_list(self, plan_id):
        self.log('get_download_list')
        header = self.create_request_header()
        url = self.create_request_url() + f"/rss/api/plans/{plan_id}/filelists"
        response = requests.get(url, headers=header)
        if response.status_code != 200:
            self.log(f'failed to get file list code={response.status_code}')
            return None
        body = json.loads(response.text)
        if 'lists' not in body:
            return None
        return body['lists']

    def _download_file(self, url, dest):
        self.log(f'download_file url={url} dest={dest}')
        header = self.create_request_header()
        url = self.create_request_url() + url
        with requests.get(url, headers=header, stream=True) as response:
            if response.status_code != 200:
                self.log(f'failed to download file ({url})')
                return None

            # Get file name
            if 'Content-Disposition' not in response.headers:
                self.log("not enough header 'Content-Disposition'")
                return None
            filename = re.findall('filename=(.+)', response.headers['Content-Disposition'])[0]
            filename = filename.replace('"', '')
            if len(filename) == 0:
                self.log("no file name in response header")
                return None

            # Store a file
            file_dest = os.path.join(dest, filename)
            with open(file_dest, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024*1024):
                    if chunk:
                        f.write(chunk)

            return os.path.abspath(file_dest)
        self.log(f'failed to request url {url}')
        return None

    def _get_machines(self):
        self.log('get_machines')
        header = self.create_request_header()
        url = self.create_request_url() + '/rss/api/system/machinesInfo'
        response = requests.get(url, headers=header)
        if response.status_code != 200:
            self.log(f'failed to get machines code={response.status_code}')
            return None
        body = json.loads(response.text)
        return body['lists']

    def _me(self):
        self.log('me')
        header = self.create_request_header()
        url = self.create_request_url() + '/rss/api/auths/me'
        response = requests.get(url, headers=header)
        if response.status_code == 200:
            return False
        return True

    # io_bus method executes common processes to connect rapid-collector server
    def io_bus(self, func, args):
        while True:
            try:
                if 'access_token' not in self.context:
                    raise GetAccessToken()
                return func(**args)
            except GetAccessToken:
                self.get_access_token()
                if 'access_token' not in self.context:
                    return None

    def create_request_header(self):
        if 'access_token' not in self.context:
            log('no access_token in context')
        return {
            'Authorization': 'Bearer ' + self.context['access_token']
        }

    def create_request_url(self):
        return 'http://%s:%d' % (self.config['host'], self.config['port'])


class GetAccessToken(Exception):
    pass
