# AI论文检索工具
本repo旨在利用该大语言模型在Arxiv快速检索相关领域论文，总结并上传至Notion。同时也可选择本地保存，会额外提取PDF中重要内容的缩略图（测试阶段）。
无论在教室、寝室、食堂或是厕所，掏出手机打开Notion即可快速浏览所需领域论文。
**一天读100篇论文不是梦~**
![image](https://github.com/user-attachments/assets/1ea23d67-7d4e-44e0-80b0-6fa7568d490d)



## Environment
* Python3
* gradio, beautifulsoup4, lxml, openai, pymupdf

## 所需接口
**以下用到的接口均免费，可自行注册。注册后可添加进config中的user_info_config.py**
* ~~**imgur api** 注册imgur，并获取api，用于上传图像并转发至notion。(上传存在限制，强烈不推荐，可使用SM.MS)~~
* **SM.MS api** 注册SM.MS，并获取api，用于上传图像并转发至notion
* **百炼api** 注册阿里的百炼，并获取api，提供N个大模型，每个都有100W个token。可在llm_model文件中选择所需大模型，默认为qwen-plus
* **NOTION api** 注册notion并获取api及database api，一款好用的多端在线笔记软件
* **NOTION database补充说明** 需提前将Notion database的属性更改为如下形式。(如需其他名称属性，可在notion.py中自行修改notion_data)
![image](https://github.com/user-attachments/assets/9395478e-0ca5-4f9a-b935-3e94876e3991)

## 使用方法
* 可以直接启用，在GUI界面中修改配置信息(较繁琐，且每次使用启用都要填写，**不推荐**)
* 首次使用可以对config中的serch_config.py和user_info_config.py进行修改，再启动GUI界面(**推荐**)
* 可以通过在llm_model添加以访问更多大模型，目前默认为百炼(免费)
* 如有公网IP或内网穿透，可以在launch中映射

## 支持作者
本工具没有经过大量测试，如遇bug欢迎批评指正。如果想支持作者，给篇一作吧~
