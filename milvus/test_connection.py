#!/usr/bin/env python3
"""
Milvus 连接测试脚本
用于验证不同模式下的 Milvus 连接是否正常
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from utils.config import get_milvus_config
from pymilvus import connections, utility

def test_milvus_connection():
    """测试 Milvus 连接"""
    print("=" * 50)
    print("Milvus 连接测试")
    print("=" * 50)
    
    # 获取当前配置
    config = get_milvus_config()
    mode = os.getenv("MILVUS_MODE", "local")
    
    print(f"当前模式: {mode}")
    print(f"连接 URI: {config['uri']}")
    
    if config.get("user"):
        print(f"用户名: {config['user']}")
    if config.get("token"):
        print(f"Token: {config['token'][:10]}...")
    
    print("-" * 50)
    
    try:
        # 准备连接参数
        connection_params = {
            "alias": "test_connection",
            "uri": config["uri"]
        }
        
        # 添加认证参数（如果有）
        if config.get("user"):
            connection_params["user"] = config["user"]
        if config.get("password"):
            connection_params["password"] = config["password"]
        if config.get("token"):
            connection_params["token"] = config["token"]
        
        print("正在连接到 Milvus...")
        connections.connect(**connection_params)
        
        # 测试基本操作
        print("连接成功！")
        
        # 检查服务器版本
        try:
            version = utility.get_server_version()
            print(f"Milvus 版本: {version}")
        except Exception as e:
            print(f"获取版本信息失败: {e}")
        
        # 列出现有集合
        try:
            collections = utility.list_collections()
            print(f"现有集合数量: {len(collections)}")
            if collections:
                print("集合列表:")
                for collection in collections:
                    print(f"  - {collection}")
        except Exception as e:
            print(f"列出集合失败: {e}")
        
        # 断开连接
        connections.disconnect("test_connection")
        print("连接测试完成！")
        return True
        
    except Exception as e:
        print(f"连接失败: {e}")
        print("\n故障排除建议:")
        
        if mode == "local":
            if "milvus_lite" in str(e):
                print("1. milvus-lite 在 Windows 上不受支持")
                print("2. 请使用远程模式：set MILVUS_MODE=remote")
                print("3. 或者运行：milvus/switch_to_remote.bat")
            else:
                print("1. 检查文件路径是否正确")
                print("2. 检查文件权限")
        else:
            print("1. 确保 Milvus 服务器正在运行")
            print("2. 检查网络连接")
            print("3. 验证 URI 是否正确")
            print("4. 如果使用 Docker：cd milvus && docker-compose up -d")
        
        return False

def print_usage():
    """打印使用说明"""
    print("\n" + "=" * 50)
    print("使用说明")
    print("=" * 50)
    print("1. 本地模式（Ubuntu/MacOS）:")
    print("   set MILVUS_MODE=local")
    print("   python milvus/test_connection.py")
    print()
    print("2. 远程模式（推荐用于 Windows）:")
    print("   set MILVUS_MODE=remote")
    print("   set MILVUS_URI=http://localhost:19530")
    print("   python milvus/test_connection.py")
    print()
    print("3. 使用 Docker 部署 Milvus:")
    print("   cd milvus")
    print("   docker-compose up -d")
    print("   cd ..")
    print("   milvus/switch_to_remote.bat")
    print("   python milvus/test_connection.py")

if __name__ == "__main__":
    success = test_milvus_connection()
    print_usage()
    
    if not success:
        sys.exit(1) 