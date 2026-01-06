"""
系统配置文件
"""
import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent

# 数据库配置
DATABASE_URL = "sqlite:///./teacher_data.db"

# 文件上传配置
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATE_DIR = UPLOAD_DIR / "templates"
TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
EXPORT_DIR = UPLOAD_DIR / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

# 允许的文件类型（现在只支持PDF）
ALLOWED_EXTENSIONS = {'.pdf'}

# 最大文件大小（MB）
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# 管理员密码（可以通过环境变量 ADMIN_PASSWORD 设置，默认密码为 admin123）
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "linmy")

# 大模型配置（如果需要使用）
# LLM_API_KEY = os.getenv("LLM_API_KEY", "")
# LLM_API_URL = os.getenv("LLM_API_URL", "")
# USE_LLM = os.getenv("USE_LLM", "false").lower() == "true"

