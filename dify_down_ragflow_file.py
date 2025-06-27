import requests
import json
import os
from typing import Dict, List


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

    # List datasets
    # GET /api/v1/datasets?page={page}&page_size={page_size}&orderby={orderby}&desc={desc}&name={dataset_name}&id={dataset_id}
    def list_dataset(self):
        url = f"{self.base_url}/api/v1/datasets"
        # 发送GET请求
        response = requests.get(url, headers=self.headers)
        return response.json()

    def download_document(self, dataset_id: str, document_id: str):
        url = f"{self.base_url}/api/v1/datasets/{dataset_id}/documents/{document_id}"
        print(url)
        # 发送GET请求
        response = requests.get(url, headers=self.headers)
        return response


def main(API_KEY: str, BASE_URL: str, dataset_id: str, retrieve_msg: str) -> dict:
    ragflow=RagFlow(api_key=API_KEY, base_url=BASE_URL)
    retrieve_msg_dict: Dict = json.loads(retrieve_msg)
    file_dict: Dict[str, List[str]] = {}
    file_url_list=[]
    for chunk_msg in retrieve_msg_dict["result"]:
        title = chunk_msg["title"]
        dif_dataset_id = chunk_msg["metadata"]["dataset_id"]
        if dif_dataset_id not in file_dict:
            file_dict[dif_dataset_id] = []
        file_dict[dif_dataset_id].append(title)
    for key in file_dict.keys():
        # 去重
        file_dict[key] = list(set(file_dict[key]))
        for file in file_dict[key]:
            document_id = ragflow.list_document(dataset_id=dataset_id,document_name=file)['data']['docs'][0]['id']
            # 优化：应该增加dify dataset_id 到 ragflow dataset_id的映射，当前使用的是一个固定的ragflow dataset_id
            url = f"{BASE_URL}/api/v1/datasets/{dataset_id}/documents/{document_id}"
            file_url_list.append(url)
    print(file_url_list)
    # get_file(file_name=title,dataset_id=rag_dataset_id)
    return {
        "result": file_url_list,
    }
