import pytest
import requests
import json
import time
import os

def test_remote_afc():

    for i in range(10):
        response = requests.get('http://localhost:5000/api/resources/settings/afc')
        assert response.status_code == 200

        response = requests.get('http://localhost:5000/api/resources/settings/date/PLATEAUTOFOCUSCOMPENSATION/BSOT_s2_SBPCN480_G147')
        assert response.status_code == 200

        response = requests.post('http://localhost:5000/api/analysis/remote/PLATEAUTOFOCUSCOMPENSATION/BSOT_s2_SBPCN480_G147', data={'period':'2021-05-11~2021-09-05'})
        assert response.status_code == 200

        response = requests.get('http://localhost:5000/api/analysis/lists/PLATEAUTOFOCUSCOMPENSATION/request_20210604_123956128826')
        assert response.status_code == 200

        response = requests.get('http://localhost:5000/api/analysis/summaries/PLATEAUTOFOCUSCOMPENSATION/request_20210604_123956128826?start=2021-05-12%2000:00:00&end=2021-05-12%2023:59:59&jobname=SCAN3X2/SCANDBG')
        assert response.status_code == 200

        response = requests.get('http://localhost:5000/api/analysis/details/PLATEAUTOFOCUSCOMPENSATION/request_20210604_123956128826?group_by=column&group_value=lot_id&start=2021-05-12%2000:00:00&end=2021-05-12%2023:59:59&jobname=SCAN3X2/SCANDBG&group_selected=-Lot1-&group_selected=-Lot3-&group_selected=-Lot4-&group_selected=-Lot5-')
        assert response.status_code == 200

        time.sleep(3)