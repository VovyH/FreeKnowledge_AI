# 🔍FreeKnowledge AI
![GitHub License](https://img.shields.io/github/license/VovyH/FreeKnowledge_AI?tab=MIT-1-ov-file)
![PyPI - Format](https://img.shields.io/pypi/format/FreeKnowledge-AI)
![GitHub stars](https://img.shields.io/github/stars/VovyH/FreeKnowledge_AI)
![PyPI - License](https://img.shields.io/pypi/l/FreeKnowledge-AI?color=purple)
![PyPI](https://img.shields.io/badge/PyPI-绿色??color=green)
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

### 5. 📈 Evaluation
##### 5.1 Benchmark:
We release the **Academy Search dataset** to serve as a unified academic-domain benchmark for search engine evaluation. All 200 queries are **non-open-ended** and **difficult**, collected exclusively from paper pages of top-tier conferences and journals, and uniformly stored in the dataset/ directory. Each query comes with a **verifiable** ground-truth answer on the source website and has been independently cross-checked by two master’s students in computer science. The dataset is further divided into **two categories**: fact-based judgment questions and fact-based short-answer question, and we will continue to expand the dataset to additional disciplines and open-source the updates.
We evaluate the search engines by feeding their outputs to InternLM3-8B, which then uniformly compares each response against the verifiable ground-truth answer to produce a consistent.
##### 5.2 characteristics:
- non-open-ended;
- difficult;
- verifiable;
- multi-categories;

**Academic Domain Examples:**
```json
Example 1:
{
 "query": "EMNLP 2024的投稿主题是否包括计算社会科学与文化分析？",
 "domain": "学术",
 "ground_truth": true,
 "answer_type": "boolean"
}
Example 2:
{
 "query": "ACL 2025主题轨道的核心内容是什么？",
 "domain": "学术",
 "ground_truth": "聚焦自然语言处理模型的泛化能力，包括如何增强模型在组合性、结构性、跨任务、跨语言、跨领域及鲁棒性等多维度的泛化能力，探究影响泛化的因素，评估泛化能力的有效方法，以及大语言模型在泛化方面的关键局限性等",
 "answer_type": "entity"
}
```

**Medical Domain Examples:**
```json
{
 "query": "派安普利单抗注射液是否获得FDA批准用于治疗复发或转移性鼻咽癌？",
 "domain": "医疗",
 "ground_truth": true,
 "answer_type": "boolean"
}

{
 "query": "根据共识，儿童脓毒性休克液体复苏的首剂液体选择是什么？推荐剂量是多少？",
 "domain": "医疗",
 "ground_truth": "首剂液体选择等渗晶体液，剂量为20ml/kg，于5-10分钟内静脉推注",
 "answer_type": "entity"
}
```

##### 5.3 Result:
**Medical Dataset:**
| Method | Correct Answers | Accuracy | Status |
|--------|----------------|----------|---------|
| DuckDuckGO API **(Free)** | - | - | Not evaluated |
| FreeKnowledge-AI **(Free)** | 138/200 | **69.00%** | ✅ Evaluated |
| BoCha API **(Business)** | 86/200 | 43.00% | ✅ Evaluated |
| Exa API **(Business)** | - | - | Not evaluated |

**Academy Search Dataset:**
| Method | Correct Answers | Accuracy | Status |
|--------|----------------|----------|-------------------|
| DuckDuckGO API **(Free)** | 3/200 | 1.5% | ✅ Evaluated  |
| FreeKnowledge-AI **(Free)** | 82/200 | **41.00%** | ✅ Evaluated |
| BoCha API **(Business)** | 14/200 | 7.00% | ✅ Evaluated |
| Exa API **(Business)** | - | - | Not evaluated |

**Note: ** FreeKnowledge AI takes 15–20 times longer than both DuckDuckGo and BoCha Search, and BoCha Search costs about 15 RMB for 200 queries—much more expensive than Exa—and delivers significantly worse results.

### 6. 🛠️ MCP Integration (New!)

FreeKnowledge AI now supports MCP (Model Control Protocol) integration, allowing you to use its search capabilities directly from MCP-compatible clients like Claude, ChatGPT, and other agents.

#### Setup MCP Server

1. Make sure you have the MCP client library installed:
```
pip install mcp
```

2. Create a `FreeKnowledgeMcp.json` configuration file:
```json
{
    "mcpServers": {
      "knowledge_search_server": {
        "command": "python",
        "args": ["path/to/your/FreeKnowledge_AI/MCP.py"],
        "transport": "stdio"
      }
    }
}
```

#### Available MCP Tools

- **baidu_search_with_summary**: Search using Baidu and summarize results with AI
- **duckduckgo_search_with_summary**: Search using DuckDuckGo and summarize results with AI
- **url_specific_with_summary**: Fetch and summarize content from a specific URL


### 7. 👇Citation
If you think this project is useful to you, please click star and cite this project。

```bibtex
@misc{Wu2024FreeKnowledge_AI,
    title={FreeKnowledge_AI: An agent that provides free and flexible access to external knowledge,
    author={Yuhang Wu and Henghua Zhang},
    year={2025},
    url=[{<url id="cuqmhcd43355nsg2o9dg" type="url" status="parsed" title="GitHub -VovyH/FreeKnowledge_AI" wc="6723">https://github.com/VovyH/FreeKnowledge_AI</url>}](https://github.com/VovyH/FreeKnowledge_AI/),
}
```
  
