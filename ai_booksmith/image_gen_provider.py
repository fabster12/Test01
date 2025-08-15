import requests
import time
from flask import g
from .config_manager import get_config

class LeonardoAPI:
    def __init__(self, api_key, ssl_cert_file=None):
        self.api_key = api_key
        self.base_url = "https://cloud.leonardo.ai/api/rest/v1"
        self.ssl_cert_file = ssl_cert_file

    def _get_headers(self):
        return {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {self.api_key}"
        }

    def generate(self, prompt, model_id=None):
        url = f"{self.base_url}/generations"
        payload = {
            "height": 768,
            "modelId": model_id,
            "prompt": prompt,
            "width": 1024
        }
        response = requests.post(url, json=payload, headers=self._get_headers(), verify=self.ssl_cert_file)
        response.raise_for_status()
        return response.json()['sdGenerationJob']['generationId']

    def poll_for_image(self, generation_id):
        url = f"{self.base_url}/generations/{generation_id}"
        for _ in range(20):  # Poll for a maximum of 100 seconds
            time.sleep(5)
            response = requests.get(url, headers=self._get_headers(), verify=self.ssl_cert_file)
            response.raise_for_status()
            job = response.json()['generations_by_pk']
            if job['status'] == 'COMPLETE':
                return job['generated_images'][0]['url']
        return None

def init_image_gen_client():
    if 'image_gen_client' not in g:
        config = get_config()
        g.image_gen_client = LeonardoAPI(
            api_key=config['leonardo_api_key'],
            ssl_cert_file=config.get('ssl_cert_file')
        )

def get_image_gen_client():
    return g.image_gen_client
