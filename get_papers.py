from config import *
from utils import *

from llm_model import BAILIAN

def get_papers(domain, sub_domain, size, start_page, keyword, save_path, save_flag, proxy_url, api_key, system_role, system_role_english, notion_flag, notion_token, notion_database_id, image_bed, client_id, retries=5, delay=0.5):
    llm = BAILIAN(api_key = api_key,system_role = system_role, system_role_english = system_role_english)
    # AI回复长度
    answer_length = 100
    each_method_length = 50
    arixv_base_html_url = 'https://arxiv.org/html/'

    base_url = 'https://arxiv.org/search/advanced?advanced='

    if notion_flag:
        if notion_token is None or notion_database_id is None:
            add_log("notion_token and notion_database_id must be provided if notion_flag is True")
            raise ValueError("notion_token and notion_database_id must be provided if notion_flag is True")
        notion_arxiv_ids = get_notion_arxiv_ids(notion_token, notion_database_id)
        
    if save_flag:
        if save_path is None:
            add_log("save_path must be provided if save_flag is True")
            raise ValueError("save_path must be provided if save_flag is True")
        if not os.path.exists(save_path):
            os.makedirs(save_path)

    use_proxy(True, proxy_url)
    add_log("已开启代理访问arxiv")

    size = int(size)
    start_page = start_page * size
    sleep_time = float(delay)
    retries = int(retries)
    args = keyword.split(';')

    find_params = '&'
    for i in range(len(args)):
        find_params += f"terms-{i}-operator=AND&terms-{i}-term={args[i]}&terms-{i}-field=all&"

    classification_include_cross_list = 'include'
    date_filter_by = 'all_dates'
    abstracts = 'show'
    order = '-announced_date_first'

    other_params = f'{domain}=y&classification-include_cross_list={classification_include_cross_list}&date-filter_by={date_filter_by}&abstracts={abstracts}&size={size}&order={order}'
    api_url = f'{base_url}{find_params}{other_params}'
    for retry in range(retries):
        try:
            arxiv_papers = get_paper_info(api_url + f"&start={int(start_page)}")
            break
        except Exception as e:
            add_log(f"第{retry+1}次访问失败，错误信息为{e}")
            time.sleep(delay)
            if retry == retries - 1:
                add_log(f"访问失败，请检查网络连接")
                raise e

    for i in range(len(arxiv_papers)):
        if notion_flag:
            if arxiv_papers[i]['pdf_link'].split('/')[-1] in notion_arxiv_ids:
                add_log('-' * 100)
                add_log(f"第{i+1}篇文章{arxiv_papers[i]['title']}已存在，跳过")
                continue
        # time.sleep(0.5) # 百炼延时防频繁
        use_proxy(False, proxy_url)
        add_log(f"为访问百炼,代理已关闭")

        title = arxiv_papers[i]['title']
        for sign in UNSAFE_SIGN:
            title = title.replace(sign, '')
        add_log('-' * 100)
        add_log(f"正在使用百炼判断第{i+1}篇文章{title}是否属于{sub_domain}类别")
        flag = llm.detect_classification(arxiv_papers[i]['abstract'], sub_domain)
        if not flag:
            add_log(f"不是")
            continue

        else:
            add_log(f"是")
            use_proxy(True, proxy_url)
            add_log(f"为访问arxiv,代理已开启")
            add_log(f"延时{sleep_time}秒，防止访问频繁")
            time.sleep(sleep_time)

            if save_flag and os.path.exists(save_path):
                add_log(f"开始下载PDF")
                
                save_path_folder = os.path.join(save_path, f"{arxiv_papers[i]['pdf_link'].split('/')[-1]}")
                if not os.path.exists(save_path_folder):
                    os.mkdir(save_path_folder)
                save_path_pdf = os.path.join(
                    save_path_folder, f"{arxiv_papers[i]['pdf_link'].split('/')[-1]}.pdf")
                for retry in range(retries):
                    try:
                        download_file(arxiv_papers[i]['pdf_link'], save_path_pdf)
                        add_log(f"pdf已下载至{save_path_pdf}")
                        has_pdf = True
                        break
                    except Exception as e:
                        add_log(f"下载失败{e},正在进行第{retry+1}次重试")
                        has_pdf = False
                        time.sleep(delay)
                        if retry == retries - 1:
                            add_log(f"下载失败{e},不再重试")
                            break

            
            add_log(f"开始获取方法总结及内容")
            for retry in range(retries):
                try:
                    conclusion,all_text,_,_ = get_html_content(arxiv_papers[i]['pdf_link'],METHOD_KEYWORDS)
                    break
                except Exception as e:
                    add_log(f"获取失败{e},正在进行第{retry+1}次重试")
                    time.sleep(delay)
                    if retry == retries - 1:
                        add_log(f"获取失败{e},不再重试")

                        break

            
            add_log(f"开始发送摘要到百炼API")
            use_proxy(False, proxy_url)
            add_log(f"为访问百炼,代理已关闭")
            ai_abstract = llm.AI_chat(arxiv_papers[i]['abstract'],answer_length=answer_length,is_conclusion=True)

            if save_flag and os.path.exists(save_path):
                save_text_state = save_text(ai_abstract, os.path.join(save_path_folder, 'ai_abstract.txt'))
                if save_text_state is None:
                    add_log(f"摘要总结已保存至{os.path.join(save_path_folder, 'ai_abstract.txt')}")
                else:
                    add_log(f"摘要总结保存失败:{save_text_state}")

            ai_conclusion = "无"
            if conclusion:
                add_log(f"开始发送方法总结到百炼API")
                ai_conclusion = llm.AI_chat(conclusion,answer_length=answer_length,is_conclusion=True)

                if save_flag and os.path.exists(save_path):
                    save_text_state = save_text(ai_conclusion, os.path.join(save_path_folder, 'ai_conclusion.txt'))
                    if save_text_state is None:
                        add_log(f"方法总结已保存至{os.path.join(save_path_folder, 'ai_conclusion.txt')}")
                    else:
                        add_log(f"方法总结保存失败:{save_text_state}")
            
            ai_all_text = "无"
            img_list = []
            if all_text:
                add_log(f"开始发送全部method到百炼API")
                ai_all_text = llm.AI_chat(all_text.text.strip().replace('\n',''),answer_length=each_method_length,is_conclusion=False)

                if save_flag and os.path.exists(save_path):
                    save_text_state = save_text(ai_all_text, os.path.join(save_path_folder, 'ai_all_text.txt'))
                    if save_text_state is None:
                        add_log(f"AI全部method已保存至{os.path.join(save_path_folder, 'ai_all_text.txt')}\n")
                    else:
                        add_log(f"AI全部method保存失败:{save_text_state}\n")
            
                add_log(f"开始获取方法图")
                use_proxy(True, proxy_url)
                add_log(f"为访问方法图,代理已开启")
                img_content = all_text.findAll('img')
                add_log(f"共找到{len(img_content)}张方法图")
                img_num = len(img_content) if len(img_content) < MAX_IMG_NUM else MAX_IMG_NUM #TODO 最大获取图像数量
                add_log(f"将获取{img_num}张方法图")
                for j, img in enumerate(img_content[:img_num]):
                    url_id = arxiv_papers[i]['pdf_link'].split("/")[-1]
                    arxiv_html_url = arixv_base_html_url + url_id
                    img_url = arxiv_html_url + '/' + img_content[j]['src']
                    for retry in range(retries):
                        try:
                            img = requests.get(img_url)
                            img.raise_for_status()
                            add_log(f"方法图{j}获取成功")
                            img_list.append(img.content)
                            break
                        except Exception as e:
                            add_log(f"方法图{j}获取失败,{e},正在第{retry+1}次重试")
                            time.sleep(delay)
                            if retry == retries - 1:
                                add_log(f"方法图{j}获取失败,不再重试")
                                break

            if img_list:
                add_log(f"{len(img_list)}张方法图已获取")
                if save_flag and os.path.exists(save_path):
                    img_folder = os.path.join(save_path_folder, 'method_images')
                    if not os.path.exists(img_folder):
                            os.mkdir(img_folder)
                    for j, img in enumerate(img_list):
                        with open(os.path.join(img_folder, f'method_{j}.png'), 'wb') as f:
                            f.write(img)
                    add_log(f"{len(img_list)}张方法图已保存至{img_folder}")
            else:
                add_log(f"未获取到方法图")

            if notion_flag:
                add_log(f"开始发送Notion")
                use_proxy(True, proxy_url)
                time.sleep(1)
                post_notion(notion_token,notion_database_id,title,arxiv_papers[i]['pdf_link'].split('/')[-1],ai_conclusion,ai_all_text,ai_abstract,img_list,image_bed,client_id)

            if save_flag and os.path.exists(save_path) and has_pdf:
                add_log(f"开始提取可能存在结构图的页码")
                found_img_page = find_pages_with_structure_diagrams(save_path_pdf, STRUCTURE_KEYWORDS, FIGURE_KEYWORDS)
                add_log(f"可能存在结构图的页码为{' '.join(map(str,found_img_page))}")
                add_log(f"开始保存缩略图")
                img_folder = os.path.join(save_path_folder, 'pdf_images')
                if not os.path.exists(img_folder):
                    os.mkdir(img_folder)
                extract_images_from_pdf(save_path_pdf, found_img_page, img_folder, title)
                add_log(f"缩略图{len(found_img_page)}张已保存至{img_folder}")

if __name__ == '__main__':
    pass

