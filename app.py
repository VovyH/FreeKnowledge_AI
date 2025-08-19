import gradio as gr
import json
from sues_center import SuesCenter

def format_output(results):
    """Format the search results for display in Gradio"""
    if not results:
        return "未找到相关结果"
    
    formatted_results = []
    for result in results:
        # Format content with markdown for better display
        content = result.get('content', '')
        while '**' in content:
            content = content.replace('**', '<b>', 1)
            content = content.replace('**', '</b>', 1)
        content = content.replace('\n', '<br>')
        
        formatted_result = f"""
        <div style='border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin-bottom: 20px;'>
            <h3>{result.get('title', '无标题')}</h3>
            <p><b>问题:</b> {result.get('question', '')}</p>
            <p><b>链接:</b> <a href='{result.get('url', '')}' target='_blank'>{result.get('url', '')}</a></p>
            <p><b>内容:</b><br>{content}</p>
        </div>
        """
        formatted_results.append(formatted_result)
    
    return "".join(formatted_results)

def search_knowledge(question, mode, specific_url=None, save_json=False):
    """Search for knowledge using the SuesCenter"""
    center = SuesCenter()
    save_format = "json" if save_json else None
    
    if mode == "URL_SPECIFIC":
        if not specific_url:
            return "请提供特定URL"
        results = center.get_response(
            prompt=question,
            flag=True,
            mode=mode,
            specific_url=specific_url,
            save_format=save_format
        )
    else:
        results = center.get_response(
            prompt=question,
            flag=True,
            mode=mode,
            save_format=save_format
        )
    
    return format_output(results)


# Create Gradio interface
with gr.Blocks(
    title="FreeKnowledge AI",
    css="""
        #title { text-align: center; font-size: 28px; font-weight: bold; margin-bottom: 20px; }
        #result-box { 
            height: 600px; 
            overflow-y: auto; 
            border: 1px solid #e0e0e0; 
            padding: 10px; 
            border-radius: 8px;
            background-color: #fafafa;
        }
    """,
    fill_height=True
) as demo:
    
    # 主标题
    gr.Markdown("<div id='title'>FreeKnowledgeAI</div>")
    
    with gr.Row(equal_height=True):
        # 左边列
        with gr.Column(scale=1, min_width=350):
            gr.Markdown("[GitHub 项目地址](https://github.com/VovyH/FreeKnowledge_AI)")

            gr.Image("https://private-user-images.githubusercontent.com/113747888/463650377-df699fb5-8682-4b5a-97d4-c66c45a324af.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTU1MzM3MjMsIm5iZiI6MTc1NTUzMzQyMywicGF0aCI6Ii8xMTM3NDc4ODgvNDYzNjUwMzc3LWRmNjk5ZmI1LTg2ODItNGI1YS05N2Q0LWM2NmM0NWEzMjRhZi5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwODE4JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDgxOFQxNjEwMjNaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT00ZDQ0YzJjN2E0YmYxNmE0OTRlNDQ0MmZmM2ZkYmRhMzk1NjRiNDM1OGI0MmIyODNkMzIwMTViZGIyYmQ4ZDM0JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.edVl3CABBGo5pNV0sGMeH9Dck_Gpdnmg9mhs_5KwSdM", show_label=False, show_download_button=False, container=False, height=200, width=700)
            gr.Image("https://img.remit.ee/api/file/BQACAgUAAyEGAASHRsPbAAKPmWijUvzFVnnTw0s_I4ZtcNYCp339AAKlHwACX7UYVQ51BsJrx1ACNgQ.png", show_label=False, show_download_button=False, container=False, height=180, width=650)
            question = gr.Textbox(
                label="问题",
                placeholder="请输入您要搜索的问题..."
            )
            mode = gr.Radio(
                choices=["BAIDU", "DUCKDUCKGO", "URL_SPECIFIC"],
                value="BAIDU",
                label="搜索模式"
            )
            specific_url = gr.Textbox(
                label="特定URL (仅在URL_SPECIFIC模式下使用)",
                placeholder="https://example.com"
            )
            search_btn = gr.Button("搜索")
        
        # 右边列（带滚动条的结果区）
        with gr.Column(scale=1):
            output = gr.HTML(label="搜索结果", elem_id="result-box")

    # 点击事件绑定
    search_btn.click(
        fn=search_knowledge,
        inputs=[question, mode, specific_url],
        outputs=output
    )

if __name__ == "__main__":
    demo.launch()
