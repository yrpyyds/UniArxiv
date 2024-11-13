def save_text(text, save_path):
    """
    将文本内容保存到指定文件中。

    参数:
    - text (str): 要保存的文本内容。
    - save_path (str): 保存文件的路径，包括文件名。
    """
    try:
        with open(save_path, 'w', encoding='utf-8') as file:
            file.write(text)
        return None
    except Exception as e:
        return e