import os
import requests

def use_proxy(flag, proxy_url):
    if flag and proxy_url:
        os.environ["http_proxy"] = proxy_url  # 代理设置
        os.environ["https_proxy"] = proxy_url  # 代理设置
        requests.Session().trust_env = True

    else:
        os.environ.pop("http_proxy", None)  # 移除 http_proxy 环境变量
        os.environ.pop("https_proxy", None)  # 移除 https_proxy 环境变量
        requests.Session().trust_env = False