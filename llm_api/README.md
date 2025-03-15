# Liz记录
## Open Router API 代码调用
Step1: 设置open router api key
```
export OPENAI_API_KEY=xxx
```
Step2: 更改model和prompt
```
model = 'qwen/qwen-2-7b-instruct:free'
prompt = 'jupyter怎么debug'
```

## open-webui使用 (页面版使用LLM API)

1. 命令行进入用户home路径
```
cd ~
```
2. 每次使用前需要激活虚拟环境
```
source webui-env/bin/activate
```
3. 开启服务
```
open-webui serve
```
4. 访问网址：http://localhost:8080

5. 使用完后可以退出虚拟环境
```
deactivate
```

# Reference
- OpenRouter：https://openrouter.ai/
- OpenWebUI Github：https://github.com/open-webui/open-webui