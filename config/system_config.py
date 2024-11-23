# 结构图相关关键词
STRUCTURE_KEYWORDS = ["structure", "construction",
                      "pipeline", "method", "architecture"]
for structure_key_word in STRUCTURE_KEYWORDS:
    STRUCTURE_KEYWORDS[0] = structure_key_word.lower()

# 图表相关关键词
FIGURE_KEYWORDS = ["figure", "picture", "fig", "image", "chart"]
for figure_key_word in FIGURE_KEYWORDS:
    FIGURE_KEYWORDS[0] = figure_key_word.lower()

# 方法相关关键词
METHOD_KEYWORDS = ['Approach',
                   'Framework',
                   'Technique',
                   'Strategy',
                   'Algorithm',
                   'System',
                   'Procedure',
                   'Design',
                   'Scheme',
                   'Solution',
                   'Mechanism',
                   'Workflow',
                   'Implementation',
                   'Module',
                   'Protocol',
                   'Configuration',
                   'Setup',
                   'Methodology',
                   "method", "pipeline", "proposed", "architecture", "model"
                   ]
for method_key_word in METHOD_KEYWORDS:
    METHOD_KEYWORDS[0] = method_key_word.lower()

# 不安全符号
UNSAFE_SIGN = [':', '?', '/', '<', '>', '*', '|', '"']

MAX_IMG_NUM = 5 # TODO 最大图片数量 尚未添加gradio
DELAY = 0.5 # 连接延时
RETRIES = 3 # 重试次数
START_PAGE = 0 # 起始页码



