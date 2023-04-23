
# 使用ChatGPT做军事文档问答
本项目使用LangChain框架做文档类型文档。  
包括两种请求方式，streaming和非streaming，其中streaming方式参考了chat-langchain项目。


---
## 重要参数
1. 用户ID
2. 文档类型
3. stream回答


## 流程
### 文档准备
1. 读取文档或者文件夹下的文档
2. 对文档进行切块
3. 对文档块进行embedding
4. 存储到向量数据库
5. 允许增量更新
6. 允许多个主题（多个表或者文件存储路径）

### 问答
1. 读取向量数据库数据
2. 对query进行embedding
3. 抽取向量数据库中和query最相似的候选文档块
4. 将query和候选文档块组合，调用llm生成答案


### note
temperature=0.0

---
## 运行
### 创建环境，然后安装依赖库
``` pip install -r requirements.txt ```

### 修改配置
按需修改``config.py``文件

### 创建文档向量数据库
``python data_prepare.py``

### 非streaming
``` python documents_qa_api.py```

### streaming
``` 
cd streaming
python main.py
```
---
## 请求

### 参数说明
**query**：请求的问题  
**chat_history**：历史消息，是一个list，[[question, answer], [question, answer], ……]，默认为[]  
**category**：文档类别，默认为strategy  
**stream**：是否为流式返回结果，默认为False  



### 非streaming
```angular2html
curl -H "Content-Type: application/json" -X POST "http://192.168.0.1:50001/documents_qa" -d '
{
    "query": "朝鲜军队有多少人服役",
    "chat_history": [],
    "category": "strategy",
    "stream": "true"
}
'
```

### streaming



