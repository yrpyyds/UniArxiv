from get_one_paper import get_one_paper
from get_papers import get_papers
import gradio as gr
import os
from config import *
from utils.log import get_logs

def update_log():
    return get_logs()

with gr.Blocks(title="文献检索") as demo:
    gr.Markdown("<center><strong><p style='font-size: 32px;'>文献检索</p></strong></center>")
    gr.Markdown("**GitHub地址**: [GitHub](https://github.com/yrpyyds/UniArxiv)")
    with gr.Row():
        domain = gr.Textbox(
            label="领域", value='classification-computer_science', interactive=False)
        sub_domain = gr.Textbox(
            label="子领域", value='Image Super Resolution', interactive=True)
        keyword = gr.Textbox(label="关键词(;分隔)", interactive=True)
    with gr.Row():
        per_number = gr.Radio(
            choices=[25, 50, 100, 200], 
            label="单次获取数量", 
            value=100,  # 默认值
            interactive=True,
        )
        # per_number.change(lambda x: x, per_number)
        start_page = gr.Number(label="起始页数(从0开始)", value=START_PAGE, interactive=True)
        submit = gr.Button("获取大批文献")
    with gr.Row():
        notion_flag = gr.Checkbox(label="是否使用Notion", value=True, interactive=True)
        notion_token = gr.Textbox(label="Notion token", value=NOTION_API_KEY, interactive=True)
        dataset_api = gr.Textbox(label="Dataset API", value=DATABASE_ID, interactive=True)
        imgmur_client_id = gr.Textbox(label="Imgur Client ID", value=IMGUR_CLIENT_ID, interactive=True)
    with gr.Row():
        log = gr.TextArea(label="日志", interactive=False)
        with gr.Column():
            arxiv_code = gr.Textbox(
                label="如需指定某一论文,请输入Arxiv Code", interactive=True)
            submit_one_arxiv = gr.Button("获取单篇文献")
            
            with gr.Row():
                api = gr.Textbox(label="百炼API", value=BAILIAN_API,
                                interactive=True)
                system_role = gr.Textbox(label="LLM角色", value=SYSTEM_ROLE, interactive=True)
                system_role_english = gr.Textbox(label="LLM角色(英文)", value=SYSTEM_ROLE_ENGLISH, interactive=True)
            proxy = gr.Textbox(label="代理IP", value=PROXY, interactive=True)
            with gr.Row():
                retries = gr.Number(label="重试次数", value=RETRIES, minimum=0, maximum=10, interactive=True)
                delay = gr.Slider(label="延时(秒)", value=DELAY, minimum=0, maximum=5, interactive=True)

            with gr.Row():
                save_flag = gr.Checkbox(label="是否保存到本地", value=True, interactive=True)
                save_path = gr.Textbox(
                label="保存路径", value=SAVE_PATH, interactive=True)
            

    submit.click(get_papers, [domain, sub_domain, per_number,
                 start_page, keyword, save_path, save_flag, proxy, api, system_role, 
                 system_role_english, notion_flag, notion_token, dataset_api, imgmur_client_id,
                 retries, delay], [log])
    submit_one_arxiv.click(get_one_paper, [arxiv_code, save_path, save_flag, 
                                           proxy, api, system_role, system_role_english, 
                                           notion_flag, notion_token, dataset_api, imgmur_client_id, 
                                           retries, delay], [log])
    demo.load(fn=update_log, outputs=log, every=0.05)

    if __name__ == "__main__":
        demo.launch(server_name='127.1.1.2')
