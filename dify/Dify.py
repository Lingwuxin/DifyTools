import requests
import json
import logging
from typing import List, Dict, Any, Optional
from requests.exceptions import RequestException

class Dify:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {self.api_key}'
        }
        
        # 初始化日志记录器
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)
        
        # 避免重复添加处理器
        if not self.logger.handlers:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            ch = logging.StreamHandler()
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

    def upload_file(self, file_path: str, user: str) -> Optional[str]:
        """上传文件到Dify平台"""
        upload_url = f"{self.base_url}/files/upload"
        try:
            self.logger.info("开始上传文件: %s", file_path)
            with open(file_path, 'rb') as file:
                # 根据文件后缀名判断文件类型
                file_extension = file_path.split('.')[-1].lower()
                if file_extension not in ['xlsx', 'xls',"csv","docx","doc","txt"]:
                    self.logger.error("不支持的文件类型: %s", file_extension)
                    return None
                files = {
                    'file': (file_path, file, 'text/plain')
                }
                data = {
                    "user": user,
                    "type": file_extension
                }

                response = requests.post(
                    upload_url,
                    headers=self.headers,
                    files=files,
                    data=data,
                    timeout=30
                )
                
                if response.status_code == 201:
                    file_id = response.json().get("id")
                    self.logger.info("文件上传成功，文件ID: %s", file_id)
                    return file_id
                
                self.logger.error(
                    "文件上传失败，状态码: %d，响应内容: %s",
                    response.status_code,
                    response.text
                )
                return None

        except FileNotFoundError:
            self.logger.error("文件不存在: %s", file_path)
            return None
        except RequestException as e:
            self.logger.error("网络请求异常: %s", str(e))
            return None
        except Exception as e:
            self.logger.exception("上传文件时发生未预期异常")
            return None
    def run_agent(self):
        pass
    def run_chatflow(
        self,
        response_mode: str = "streaming",
        query: str = ""
        ) -> Dict[str, Any]:
        """运行聊天工作流"""
        chatflow_url = f"{self.base_url}/chat-messages"
        data={
            'inputs':{},
            'query': query,
            'response_mode': response_mode,
            'user':"AyuanTest"
        }
        self.logger.info("开始运行对话流")
        stream_mode = (response_mode == "streaming")
        response = requests.post(
            chatflow_url,
            headers=self.headers,
            json=data,
            stream=stream_mode,
            timeout=60
        )

        if response.status_code != 200:
            self.logger.error(
                "对话流请求失败，状态码: %d，响应内容: %s",
                response.status_code,
                response.text
            )
            return {"status": "error", "message": response.text}

        result_text = ""
        self.logger.info("开始处理流式响应...")
        message_id = None
        conversation_id = None
        files = []
        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue
            if line.startswith("data: "):
                json_str = line[6:].strip()
                try:
                    json_data = json.loads(json_str)
                except Exception as e:
                    self.logger.warning(f"解析JSON失败: {e}, 内容: {json_str}")
                    continue
                event = json_data.get("event")
                # 处理 LLM 文本块
                if event == "message":
                    answer = json_data.get("answer", "")
                    result_text += answer
                    print(answer, end="", flush=True)
                    message_id = json_data.get("message_id")
                    conversation_id = json_data.get("conversation_id")
                # 处理文件块
                elif event == "message_file":
                    files.append({
                        "id": json_data.get("id"),
                        "type": json_data.get("type"),
                        "url": json_data.get("url"),
                        "belongs_to": json_data.get("belongs_to"),
                        "conversation_id": json_data.get("conversation_id")
                    })
                # 处理消息替换
                elif event == "message_replace":
                    answer = json_data.get("answer", "")
                    result_text = answer
                    print(f"\n[内容被替换]: {answer}", flush=True)
                # 处理消息结束
                elif event == "message_end":
                    self.logger.info("对话流执行完成")
                    return {
                        "status": "success",
                        "result": result_text,
                        "message_id": json_data.get("message_id"),
                        "conversation_id": json_data.get("conversation_id"),
                        "files": files,
                        "metadata": json_data.get("metadata"),
                        "usage": json_data.get("usage"),
                        "retriever_resources": json_data.get("retriever_resources")
                    }
                # 处理 TTS 音频流
                elif event == "tts_message":
                    # 如需处理音频可在此处实现
                    pass
                elif event == "tts_message_end":
                    pass
                # 处理 ping
                elif event == "ping":
                    continue
                # 处理异常
                elif event == "error":
                    self.logger.error(f"流式输出异常: {json_data.get('message')}")
                    return {"status": "error", "message": json_data.get("message")}
                # 其他事件可按需扩展
        return {"status": "success", "result": result_text, "files": files}

    def run_workflow(
        self,
        files: Optional[Any] = None,
        response_mode: str = "streaming",
        **args
    ) -> Dict[str, Any]:
        """运行工作流，支持自定义inputs参数"""
        workflow_url = f"{self.base_url}/workflows/run"
        inputs = dict(args) if args else {}
        if files is not None:
            inputs["files"] = files
        data = {
            "inputs": inputs,
            "response_mode": response_mode,
            "user": "user"
        }
        self.logger.info("开始运行工作流，inputs: %s", inputs)
        stream_mode = (response_mode == "streaming")
        response = requests.post(
            workflow_url,
            headers=self.headers,
            json=data,
            stream=stream_mode,
            timeout=60
        )

        if response.status_code != 200:
            self.logger.error(
                "工作流请求失败，状态码: %d，响应内容: %s",
                response.status_code,
                response.text
            )
            return {"status": "error", "message": response.text}

        result_text = ""
        final_outputs = None
        run_id = None
        self.logger.info("等待工作流执行...")
        if response_mode == "blocking":
            # blocking模式直接获取完整响应
            try:
                resp_json = response.json()
                self.logger.info("工作流执行完成(blocking)")
                return {
                    "raw": resp_json
                }
            except Exception as e:
                self.logger.error(f"blocking模式解析失败: {e}")
                return {"status": "error", "message": str(e)}
        else:
            self.logger.info("开始处理流式响应...")
            # streaming模式
            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue
                if line.startswith("data: "):
                    json_str = line[6:].strip()
                    json_data = json.loads(json_str)
                    # 处理工作流进度信息
                    if json_data.get("event") == "workflow_started":
                        self.logger.info("工作流开始执行")
                    # 处理中间结果
                    elif json_data.get("event") == "workflow_step_executing":
                        step_data = json_data.get("data", {})
                        self.logger.debug(
                            "步骤执行中: %s",
                            step_data.get("node_id")
                        )
                    # 处理最终结果
                    elif json_data.get("event") == "workflow_finished":
                        outputs = json_data.get("data", {}).get("outputs", {})
                        self.logger.info("工作流执行完成(streaming)")
                        return {
                            "raw": json_data
                        }
                    # 显示文本输出
                    if "text" in json_data.get("data", {}):
                        print(json_data["data"]["text"], end="", flush=True)
            return {
                "status": "failed",
            }
if __name__ == "__main__":
    # 示例用法
    import json
    load_config = json.load(open("./dify/config.json","r",encoding="utf-8"))
    api_key = load_config['api_key']
    base_url = load_config['base_url']
    dify = Dify(api_key, base_url)
    query='你好'
    
    print(dify.run_workflow(response_mode='blocking',query='阿克苏哪些水果好吃？'))