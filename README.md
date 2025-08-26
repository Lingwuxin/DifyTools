# DifyTools

## 安装

1. 克隆仓库到本地：

   ```shell
   git clone https://github.com/Lingwuxin/DifyTools.git
   ```

2. 进入项目目录并安装依赖：

   ```shell
   cd DifyTools
   pip install -r requirements.txt
   ```

3. 配置 Dify API 信息  
   在 `dify/config.json` 文件中填写你的 `api_key` 和 `base_url`。

---

## 使用方法

### 1. 运行脚本示例

在 `dify/Dify.py` 中有示例代码：

```python
from dify.Dify import Dify

# 加载配置
import json
load_config = json.load(open("./dify/config.json", "r", encoding="utf-8"))
api_key = load_config['api_key']
base_url = load_config['base_url']

dify = Dify(api_key, base_url)

# 运行工作流
result = dify.run_workflow(response_mode='blocking', query='阿克苏哪些水果好吃？')
print(result)
```

### 2. 上传文件

```python
file_id = dify.upload_file('your_file.xlsx', user='your_user')
```

### 3. 自定义工作流输入

```python
result = dify.run_workflow(response_mode='blocking', query='你好', other_param='xxx')
```

---

## 热爱的 me

热爱是最好的老师，愿你在代码和生活中都能找到属于自己的热爱。
