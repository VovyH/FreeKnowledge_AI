# 🔍FreeKnowledge AI
![GitHub License](https://img.shields.io/github/license/VovyH/FreeKnowledge_AI?tab=MIT-1-ov-file)
![PyPI - Format](https://img.shields.io/pypi/format/FreeKnowledge-AI)
![GitHub stars](https://img.shields.io/github/stars/VovyH/FreeKnowledge_AI)
![PyPI - License](https://img.shields.io/pypi/l/FreeKnowledge-AI?color=purple)
![书生·铺语大模型](https://img.shields.io/badge/书生·浦语大模型-蓝色?color=blue)

✨An agent that provides **free** and **flexible** access to external knowledge！！
<div align="center">
     <img src="https://github.com/user-attachments/assets/df699fb5-8682-4b5a-97d4-c66c45a324af"/>
</div>


### 1. 📖Introduction

Currently, there are only a few interfaces such as DuckDuckGO that can be used to obtain external knowledge for free. These interfaces are **difficult to obtain complete external knowledge** and are very cumbersome and **cannot obtain external knowledge related to the original problem**. Most of the interfaces with better effects are **relatively expensive**, such as Bocha, Google and other APIs. Therefore, we open-source a **free** and **flexible** external knowledge interface - **FreeKnowledge AI** 。

### 2. 😀Simple & Free

- You only need to download the knowledge_AI dependency to use it, which is very convenient！！
```shell
pip install FreeKnowledge-AI==0.2.0
```

- A **simple** example of acquiring external knowledge:
Before using it, we recommend that you read the **Flexible section** to better understand the flexibility of **FreeKnowledge AI** .
```python
from FreeKnowledge_AI import knowledge_center

# 1.Initialize the knowledge agent
center = knowledge_center.Center()
question = "2024年上海工程技术大学研究生复试分数线"
flag = False # Flag indicates whether a large model is needed, and the output content will be more beautiful and standard.
mode = "BAIDU" # Currently only supports "BAIDU" and "DUCKDUCKGO"。
# 2.Respond to external knowledge
results = center.get_response(question, flag, mode)
print(results)
```

- **Log** of External knowledge obtained from the website:
<div align="center">
     <img src="https://github.com/user-attachments/assets/88632553-a275-4836-a3b5-3bf66485f54a"/>
</div>

- **Console** Output:
<div align="center">
     <img src="https://github.com/user-attachments/assets/751c351f-9e9e-4959-ba92-4b3b1f811411"/>
</div>

### 3. ⚡Flexible

We allow passing in a variety of parameters to better control the output, including:
- `question`: Question entered by the user (Required)。
- `flag`: Whether to use a large model to extract the core content of crawled external knowledge (Default True)。
- `mode`: "BAIDU", "DUCKDUCKGO" (Default "DUCKDUCKGO")，or "URL_SPECIFIC"。
  > You need to use VPN when using "DUCKDUCKGO", but not "BAIDU". We recommend using "DUCKDUCKGO" because the crawled results are more accurate, but Baidu's response speed will be faster.
- `specific_url` :This specifies the exact URL(s) to crawl directly. Example: "https://docs.python.org/3/tutorial/
- `model`: You can choose the large model you want to use (Default "internlm/internlm2_5-7b-chat").
- `base_url`: The base_url of the model (Default "https://api.siliconflow.cn/v1/chat/completions").
- `key`: Pass in your own key。
- `max_web_results`: Get the amount of crawled external knowledge (Default 5)。
- `save_format`: Specify the format to save results. Set to "json" to automatically save results to a file named after your question (e.g., "your_question.json").

**Report errors:**
> When you fail to obtain website content, don't worry, just wait a little longer, because some websites require verification. Another solution is to increase the number of retries and thread sleep time.

### 4. 📋Complete Example

```python
from FreeKnowledge_AI import knowledge_center

center = knowledge_center.Center()
question = "2025年EMNLP会议的主题是什么?"
flag = True 
mode = "DUCKDUCKGO"

results = center.get_response(question, flag, mode, model="internlm/internlm2_5-7b-chat", 
                              base_url="https://api.siliconflow.cn/v1/chat/completions", key = "xxx", max_web_results = 2)
print(results) 
```

<div align="center">
     <img src="https://github.com/user-attachments/assets/c7cd31bf-1732-476b-a4ca-d4c33529f644"/>
</div>

## 5. 👇Citation
If you think this project is useful to you, please click star and cite this project。

```bibtex
@misc{Wu2024FreeKnowledge_AI,
    title={FreeKnowledge_AI: An agent that provides free and flexible access to external knowledge,
    author={Yuhang Wu and Henghua Zhang},
    year={2025},
    url=[{<url id="cuqmhcd43355nsg2o9dg" type="url" status="parsed" title="GitHub -VovyH/FreeKnowledge_AI" wc="6723">https://github.com/VovyH/FreeKnowledge_AI</url>}](https://github.com/VovyH/FreeKnowledge_AI/),
}
```
  
