import requests
from lxml import html
from bs4 import BeautifulSoup
import re
from .log import add_log

def get_total_results(url):
    """获取总结果数"""
    response = requests.get(url)
    tree = html.fromstring(response.content)
    result_string = ''.join(tree.xpath(
        '//*[@id="main-container"]/div[1]/div[1]/h1/text()')).strip()
    match = re.search(r'of ([\d,]+) results', result_string)
    if match:
        total_results = int(match.group(1).replace(',', ''))
        return total_results
    else:
        add_log("没有找到匹配的数字。")
        return 0
    
def get_paper_info(url):
    """根据URL爬取一页的论文信息"""
    response = requests.get(url)

    tree = html.fromstring(response.content)
    result_string = ''.join(tree.xpath(
        '//*[@id="main-container"]/div[1]/div[1]/h1/text()')).strip()
    match = re.search(r'of ([\d,]+) results', result_string)
    if match:
        total_results = int(match.group(1).replace(',', ''))
        add_log(f"共找到{total_results}篇论文")
    else:
        add_log("无法获取论文数量。")

    soup = BeautifulSoup(response.content, 'html.parser')
    papers = []

    for article in soup.find_all('li', class_='arxiv-result'):
        title = article.find('p', class_='title').text.strip()
        authors_text = article.find(
            'p', class_='authors').text.replace('Authors:', '').strip()
        authors = [author.strip() for author in authors_text.split(',')]
        abstract = article.find('span', class_='abstract-full').text.strip()
        submitted = article.find('p', class_='is-size-7').text.strip()
        submission_date = submitted.split(
            ';')[0].replace('Submitted', '').strip()
        pdf_link_element = article.find('a', text='pdf')
        if pdf_link_element:
            pdf_link = pdf_link_element['href']
        else:
            pdf_link = 'No PDF link found'

        papers.append({'title': title, 'authors': authors, 'abstract': abstract.split(
            '\n')[0], 'submission_date': submission_date, 'pdf_link': pdf_link})

    return papers

def download_file(url, filename):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as file:
            file.write(response.content)
        # add_log(f"文件已下载：{filename}")
    else:
        add_log("下载失败，状态码：", response.status_code)

def get_html_content(url, method_key_words, arixv_base_html_url='https://arxiv.org/html/'):
    url_id = f'{url.split("/")[-1]}'
    arxiv_html_url = arixv_base_html_url + url_id
    response = requests.get(arxiv_html_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    sections = soup.find_all('h2',attrs={'class': 'ltx_title ltx_title_section'})
    conclusion = ''
    all_text = ''
    for section in sections:
        if any(method_key_word in section.text.lower() for method_key_word in method_key_words):
            all_text = section.parent
            conclusion = section.parent.findAll(attrs={'class': re.compile(r"^ltx_para"),'id':re.compile(r"^S\d.p\d") }) # 拿总结
            # content = section.parent.findAll(attrs={'class': re.compile(r"^ltx_subsection"),'id':re.compile(r"^S\d.SS\d") }) # 拿内容
    
    sections = soup.find_all('div',attrs={'class': 'ltx_abstract',})
    title = soup.find_all('h1',attrs={'class': 'ltx_title ltx_title_document',})
    try:
        title = title[0].text.strip().replace('\n', '')
    except:
        title = "未获取到题目"
    try:
        abstract = sections[0].text.strip().replace('\n', '')
    except:
        abstract = None

    conclusion_text = ''
    if conclusion:
        for paragraph in conclusion:
            conclusion_text += paragraph.text.strip().replace('\n','') + '\n'
    if all_text:
        return conclusion_text,all_text,abstract,title
    else:
        return None,None,abstract,title

def get_html_abstract_title(url, arixv_base_html_url='https://arxiv.org/html/'):
    # headers = {"User-Agent": "Mozilla/5.0"}
    url_id = f'{url.split("/")[-1]}'
    arxiv_html_url = arixv_base_html_url + url_id
    response = requests.get(arxiv_html_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    sections = soup.find_all('div',attrs={'class': 'ltx_abstract',})
    title = soup.find_all('h1',attrs={'class': 'ltx_title ltx_title_document',})
    try:
        title = title[0].text.strip().replace('\n', '')
    except:
        title = None
    try:
        abstract = sections[0].text.strip().replace('\n', '')
    except:
        abstract = None
    return abstract, title