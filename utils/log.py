# 日志记录列表，用于存储日志
log_records = []

# 增加日志记录
def add_log(message):
    log_entry = f"[INFO] {message}"
    log_records.append(log_entry)

# 获取最新的日志内容
def get_logs():
    return "\n".join(log_records)