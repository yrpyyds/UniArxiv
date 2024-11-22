import requests
import time
from .log import add_log
import os
from io import BytesIO
from notion_client import Client

def upload_image_to_imgur(image_content,imgmur_client_id,retries=3, delay=1):
    """上传本地图片到 Imgur 并获取 URL"""
    retrie = 0
    imgur_headers = {"Authorization": f"Client-ID {imgmur_client_id}"}
    
    data = {"image": BytesIO(image_content)}
    while True:
        try:
            response = requests.post("https://api.imgur.com/3/image", headers=imgur_headers, files=data)
            response.raise_for_status()
            return response.json()["data"]["link"]
        except requests.exceptions.RequestException as e:
            retrie += 1
            if retrie <= retries:
                add_log(f"上传到 Imgur 失败，重试次数：{retrie}")
                time.sleep(delay)
                return upload_image_to_imgur(image_content, imgmur_client_id, retries - 1, delay * 2)
            else:
                add_log(f"上传到 Imgur 失败，重试次数：{retries}，放弃上传")
                return None

def post_notion(notion_token, database_id, title, arxiv_id, conclusion, all_text, ai_abstract, img_list, imgmur_client_id, retries=3 ,delay=1):
    image_urls = []
    if img_list:     
        for j,img_file in enumerate(img_list):
            img_url = upload_image_to_imgur(img_file,imgmur_client_id)
            # time.sleep(1)
            if img_url:
                image_urls.append(img_url)
            else:
                add_log(f"图片 {j} 上传失败，跳过该图片")
    notion_headers = {
    # "Accept": "application/json",
    "Authorization": f"Bearer {notion_token}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
    }
    notion_data = {
            "parent": {"database_id": database_id},
            "properties": {
                "Title": {
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                },
                "Arxiv ID": {
                    "rich_text": [
                        {
                            "text": {
                                "content": arxiv_id
                            }
                        }
                    ]
                },
                "摘要总结": {
                    "rich_text": [
                        {
                            "text": {
                                "content": ai_abstract
                            }
                        } if ai_abstract else {
                            "text": {
                                "content": "无"
                            }
                        }
                    ]
                },
                "方法总结": {
                    "rich_text": [
                        {
                            "text": {
                                "content": conclusion
                            }
                        } if conclusion else {
                            "text": {
                                "content": "无"
                            }
                        }
                    ]
                },
                "方法分析": {
                    "rich_text": [
                        {
                            "text": {
                                "content": all_text
                            }
                        } if all_text else {
                            "text": {
                                "content": "无"
                            }
                        }
                    ]
                },
            },
            "children": [
                {
                    "object": "block",
                    "type": "image",
                    "image": {
                        "type": "external",
                        "external": {
                            "url": image_url
                        }
                    }
                } for image_url in image_urls  # 添加所有图片块
            ]
        }
    # print(notion_data)
    for attempt in range(retries):
        try:
            response = requests.post("https://api.notion.com/v1/pages", headers=notion_headers, json=notion_data)
            response.raise_for_status()
            add_log(f"文章{title}已成功上传到Notion")
            break
        except requests.exceptions.ConnectionError as e:
            add_log(f"ConnectionError: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
        except Exception as e:
            add_log(f"An error occurred: {e}")
            break

def get_notion_arxiv_ids(notion_token,database_id):
    add_log(f"开始获取notion已有论文")
    # 初始化 Notion 客户端
    notion = Client(auth=notion_token)

    arxiv_ids = []
    start_cursor = None  # 初始分页游标
    while True:
        # 查询数据库内容，支持分页
        query_result = notion.databases.query(
            database_id=database_id,
            start_cursor=start_cursor,
        )
        for page in query_result.get("results", []):
            # 获取每页的 "Arxiv ID" 属性值
            properties = page.get("properties", {})
            arxiv_id_property = properties.get("Arxiv ID", {})
            
            if arxiv_id_property.get("type") == "rich_text":
                arxiv_id = "".join([text.get("text", {}).get("content", "") 
                                    for text in arxiv_id_property.get("rich_text", [])])
                arxiv_ids.append(arxiv_id)
        if not query_result.get("has_more"):
            break
        start_cursor = query_result.get("next_cursor")
    add_log(f"从Notion获取到{len(arxiv_ids)}个已有的arXiv ID")
    
    return arxiv_ids