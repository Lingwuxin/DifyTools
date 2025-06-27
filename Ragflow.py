import requests
import json
import os


class RagFlow:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            'content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

    def list_document(self, dataset_id: str, page: int = 1, page_size: int = 10, orderby: str = "create_time", desc: bool = True,
                      keywords: str = "", document_id: str = "", document_name: str = ""):
        url = f"{self.base_url}/api/v1/datasets/{dataset_id}/documents?page={page}&page_size={page_size}&orderby={orderby}&desc={desc}&keywords={keywords}&id={document_id}&name={document_name}"
        # 发送GET请求
        response = requests.get(url, headers=self.headers)
        return response.json()
    
    #List datasets
    #GET /api/v1/datasets?page={page}&page_size={page_size}&orderby={orderby}&desc={desc}&name={dataset_name}&id={dataset_id}
    def list_dataset(self):
        url = f"{self.base_url}/api/v1/datasets"
        # 发送GET请求
        response = requests.get(url, headers=self.headers)
        return response.json()
    def download_document(self, dataset_id: str, document_id: str):
        url = f"{self.base_url}/api/v1/datasets/{dataset_id}/documents/{document_id}"
        response = requests.get(url, headers=self.headers)
        return response