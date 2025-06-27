from enum import Enum
from typing import Dict, Any
import os

class VectorDBProvider(str, Enum):
    MILVUS = "milvus"
    # More providers can be added later

# 默认的本地文件数据库配置（保持原有配置）
MILVUS_CONFIG = {
    "uri": "03-vector-store/langchain_milvus.db",
    "index_types": {
        "flat": "FLAT",
        "ivf_flat": "IVF_FLAT",
        "ivf_sq8": "IVF_SQ8",
        "hnsw": "HNSW"
    },
    "index_params": {
        "flat": {},
        "ivf_flat": {"nlist": 1024},
        "ivf_sq8": {"nlist": 1024},
        "hnsw": {
            "M": 16,
            "efConstruction": 500
        }
    }
}

# 新增：远程Milvus服务器配置
MILVUS_REMOTE_CONFIG = {
    "uri": "http://localhost:19530",  # 远程Milvus服务器地址
    "user": "",  # 用户名（如果需要认证）
    "password": "",  # 密码（如果需要认证）
    "token": "",  # Token认证（可选）
    "index_types": {
        "flat": "FLAT",
        "ivf_flat": "IVF_FLAT",
        "ivf_sq8": "IVF_SQ8",
        "hnsw": "HNSW"
    },
    "index_params": {
        "flat": {},
        "ivf_flat": {"nlist": 1024},
        "ivf_sq8": {"nlist": 1024},
        "hnsw": {
            "M": 16,
            "efConstruction": 500
        }
    }
}

def get_milvus_config():
    """
    根据环境变量选择Milvus配置
    
    环境变量 MILVUS_MODE:
    - "local" 或 未设置: 使用本地文件数据库（默认）
    - "remote": 使用远程Milvus服务器
    
    Returns:
        Dict: Milvus配置字典
    """
    mode = os.getenv("MILVUS_MODE", "local").lower()
    
    if mode == "remote":
        # 可以通过环境变量覆盖远程配置
        config = MILVUS_REMOTE_CONFIG.copy()
        if os.getenv("MILVUS_URI"):
            config["uri"] = os.getenv("MILVUS_URI")
        if os.getenv("MILVUS_USER"):
            config["user"] = os.getenv("MILVUS_USER")
        if os.getenv("MILVUS_PASSWORD"):
            config["password"] = os.getenv("MILVUS_PASSWORD")
        if os.getenv("MILVUS_TOKEN"):
            config["token"] = os.getenv("MILVUS_TOKEN")
        return config
    else:
        # 默认使用本地配置
        return MILVUS_CONFIG 