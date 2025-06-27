#!/usr/bin/env python3
"""
Milvus 基础使用示例
演示如何使用 Milvus 进行基本的向量操作
"""

import os
import sys
from pathlib import Path
import numpy as np

# 添加项目根目录到 Python 路径
sys.path.append(str(Path(__file__).parent.parent.parent / "backend"))

from utils.config import get_milvus_config
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility

def create_sample_collection():
    """创建示例集合"""
    # 获取配置并连接
    config = get_milvus_config()
    connections.connect(
        alias="default",
        uri=config["uri"],
        user=config.get("user", ""),
        password=config.get("password", ""),
        token=config.get("token", "")
    )
    
    # 定义集合 schema
    collection_name = "example_collection"
    
    # 删除已存在的集合
    if utility.has_collection(collection_name):
        utility.drop_collection(collection_name)
    
    # 定义字段
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=512),
        FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=128)
    ]
    
    schema = CollectionSchema(fields, description="示例集合")
    collection = Collection(collection_name, schema)
    
    return collection

def insert_sample_data(collection):
    """插入示例数据"""
    # 生成示例数据
    texts = [
        "人工智能是计算机科学的一个分支",
        "机器学习是人工智能的子领域",
        "深度学习使用神经网络",
        "向量数据库用于存储和检索向量",
        "Milvus 是一个开源向量数据库"
    ]
    
    vectors = np.random.random((len(texts), 128)).tolist()
    
    entities = [
        texts,
        vectors
    ]
    
    # 插入数据
    insert_result = collection.insert(entities)
    print(f"插入了 {len(insert_result.primary_keys)} 条数据")
    
    # 刷新数据
    collection.flush()
    
    return insert_result

def create_index_and_load(collection):
    """创建索引并加载集合"""
    # 创建索引
    index_params = {
        "metric_type": "COSINE",
        "index_type": "IVF_FLAT",
        "params": {"nlist": 128}
    }
    
    collection.create_index("vector", index_params)
    print("索引创建完成")
    
    # 加载集合
    collection.load()
    print("集合加载完成")

def search_vectors(collection):
    """搜索向量"""
    # 生成查询向量
    query_vector = np.random.random((1, 128)).tolist()
    
    # 执行搜索
    search_params = {
        "metric_type": "COSINE",
        "params": {"nprobe": 10}
    }
    
    results = collection.search(
        data=query_vector,
        anns_field="vector",
        param=search_params,
        limit=3,
        output_fields=["text"]
    )
    
    print("搜索结果:")
    for hits in results:
        for hit in hits:
            print(f"- ID: {hit.id}, 距离: {hit.distance:.4f}, 文本: {hit.entity.get('text')}")

def main():
    """主函数"""
    try:
        print("=" * 50)
        print("Milvus 基础使用示例")
        print("=" * 50)
        
        # 1. 创建集合
        print("1. 创建示例集合...")
        collection = create_sample_collection()
        
        # 2. 插入数据
        print("\n2. 插入示例数据...")
        insert_sample_data(collection)
        
        # 3. 创建索引并加载
        print("\n3. 创建索引并加载集合...")
        create_index_and_load(collection)
        
        # 4. 搜索向量
        print("\n4. 执行向量搜索...")
        search_vectors(collection)
        
        print("\n示例完成！")
        
    except Exception as e:
        print(f"错误: {e}")
        print("\n请确保:")
        print("1. Milvus 服务器正在运行")
        print("2. 环境变量配置正确")
        print("3. 网络连接正常")
        
    finally:
        connections.disconnect("default")

if __name__ == "__main__":
    main() 