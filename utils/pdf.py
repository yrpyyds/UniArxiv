import fitz
import os
from PIL import Image

def find_pages_with_structure_diagrams(pdf_path, structure_keywords, figure_keywords):
    # 打开PDF文件
    doc = fitz.open(pdf_path)
    page_numbers = []

    # 遍历每一页
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        paragraphs = text.split("\n")

        # 检查每个段落是否同时包含结构图和图表关键词
        for paragraph in paragraphs:
            lower_paragraph = paragraph.lower()
            if any(structure_keyword in lower_paragraph for structure_keyword in structure_keywords) and \
               any(figure_keyword in lower_paragraph for figure_keyword in figure_keywords):
                page_numbers.append(page_num + 1)  # +1是因为页面编号从1开始
                break  # 一旦找到，就不需要检查同一页面的其他段落

    doc.close()
    return page_numbers

def extract_images_from_pdf(pdf_path, may_pages, output_folder, filename):
    # 创建输出文件夹
    os.makedirs(output_folder, exist_ok=True)

    # 打开PDF文件
    pdf_file = fitz.open(pdf_path)
    img_pages = []
    for page_num in may_pages:
        # 获取页面
        page = pdf_file[page_num - 1]
        # 获取页面中的图片列表
        image_list = page.get_images()

        if image_list:
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img_pages.append((img, page_num))

    if len(img_pages) > 0:
        for img, page_num in img_pages:
            img.save(f"{output_folder}/{filename}_page_{page_num}.png")
        return (f"Extracted Successfully!{len(img_pages)} page images had saved in {output_folder}")
    else:
        return (f"No images found")