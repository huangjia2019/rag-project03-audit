#!/usr/bin/env python3
"""
Milvus 性能测试示例
测试不同配置下的 Milvus 性能表现
"""

import os
import sys
import time
from pathlib import Path
import numpy as np

# 添加项目根目录到 Python 路径
sys.path.append(str(Path(__file__).parent.parent.parent / "backend"))

from utils.config import get_milvus_config
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility

def performance_test():
    """性能测试主函数"""
    print("=" * 60)
    print("Milvus 性能测试")
    print("=" * 60)
    
    # 连接到 Milvus
    config = get_milvus_config()
    connections.connect(
        alias="default",
        uri=config["uri"],
        user=config.get("user", ""),
        password=config.get("password", ""),
        token=config.get("token", "")
    )
    
    # 测试参数
    test_configs = [
        {"dim": 128, "count": 1000, "index_type": "FLAT"},
        {"dim": 128, "count": 1000, "index_type": "IVF_FLAT"},
        {"dim": 256, "count": 1000, "index_type": "IVF_FLAT"},
        {"dim": 384, "count": 1000, "index_type": "IVF_FLAT"},
    ]
    
    results = []
    
    for i, test_config in enumerate(test_configs, 1):
        print(f"\n测试 {i}/{len(test_configs)}: {test_config}")
        result = run_single_test(**test_config)
        results.append((test_config, result))
    
    # 输出测试结果摘要
    print_test_summary(results)
    
    connections.disconnect("default")

def run_single_test(dim, count, index_type):
    """运行单个测试"""
    collection_name = f"perf_test_{dim}d_{count}_{index_type.lower()}"
    
    try:
        # 1. 创建集合
        start_time = time.time()
        collection = create_test_collection(collection_name, dim)
        create_time = time.time() - start_time
        
        # 2. 插入数据
        start_time = time.time()
        vectors = np.random.random((count, dim)).tolist()
        texts = [f"文档_{i}" for i in range(count)]
        entities = [texts, vectors]
        
        insert_result = collection.insert(entities)
        collection.flush()
        insert_time = time.time() - start_time
        
        # 3. 创建索引
        start_time = time.time()
        create_test_index(collection, index_type)
        index_time = time.time() - start_time
        
        # 4. 加载集合
        start_time = time.time()
        collection.load()
        load_time = time.time() - start_time
        
        # 5. 搜索测试
        search_times = []
        query_vectors = np.random.random((10, dim)).tolist()
        
        for query_vector in query_vectors:
            start_time = time.time()
            results = collection.search(
                data=[query_vector],
                anns_field="vector",
                param={"metric_type": "COSINE", "params": {"nprobe": 10}},
                limit=10
            )
            search_time = time.time() - start_time
            search_times.append(search_time)
        
        avg_search_time = np.mean(search_times)
        
        # 清理
        utility.drop_collection(collection_name)
        
        return {
            "create_time": create_time,
            "insert_time": insert_time,
            "index_time": index_time,
            "load_time": load_time,
            "avg_search_time": avg_search_time,
            "total_time": create_time + insert_time + index_time + load_time,
            "success": True
        }
        
    except Exception as e:
        print(f"测试失败: {e}")
        # 清理失败的集合
        try:
            if utility.has_collection(collection_name):
                utility.drop_collection(collection_name)
        except:
            pass
        
        return {
            "error": str(e),
            "success": False
        }

def create_test_collection(collection_name, dim):
    """创建测试集合"""
    # 删除已存在的集合
    if utility.has_collection(collection_name):
        utility.drop_collection(collection_name)
    
    # 定义字段
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=512),
        FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=dim)
    ]
    
    schema = CollectionSchema(fields, description=f"性能测试集合 - {dim}维")
    collection = Collection(collection_name, schema)
    
    return collection

def create_test_index(collection, index_type):
    """创建测试索引"""
    if index_type == "FLAT":
        index_params = {
            "metric_type": "COSINE",
            "index_type": "FLAT"
        }
    elif index_type == "IVF_FLAT":
        index_params = {
            "metric_type": "COSINE",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 128}
        }
    else:
        raise ValueError(f"不支持的索引类型: {index_type}")
    
    collection.create_index("vector", index_params)

def print_test_summary(results):
    """输出测试结果摘要"""
    print("\n" + "=" * 60)
    print("测试结果摘要")
    print("=" * 60)
    
    print(f"{'配置':<30} {'状态':<8} {'总时间':<10} {'搜索时间':<12}")
    print("-" * 60)
    
    for test_config, result in results:
        config_str = f"{test_config['dim']}维, {test_config['count']}条, {test_config['index_type']}"
        
        if result["success"]:
            status = "成功"
            total_time = f"{result['total_time']:.3f}s"
            search_time = f"{result['avg_search_time']*1000:.2f}ms"
        else:
            status = "失败"
            total_time = "N/A"
            search_time = "N/A"
        
        print(f"{config_str:<30} {status:<8} {total_time:<10} {search_time:<12}")
    
    # 详细结果
    print(f"\n详细性能数据:")
    for test_config, result in results:
        if result["success"]:
            config_str = f"{test_config['dim']}维, {test_config['count']}条, {test_config['index_type']}"
            print(f"\n{config_str}:")
            print(f"  - 创建集合: {result['create_time']:.3f}s")
            print(f"  - 插入数据: {result['insert_time']:.3f}s")
            print(f"  - 创建索引: {result['index_time']:.3f}s") 
            print(f"  - 加载集合: {result['load_time']:.3f}s")
            print(f"  - 平均搜索: {result['avg_search_time']*1000:.2f}ms")

def system_info():
    """显示系统信息"""
    config = get_milvus_config()
    mode = os.getenv("MILVUS_MODE", "local")
    
    print("系统信息:")
    print(f"  - 模式: {mode}")
    print(f"  - URI: {config['uri']}")
    print(f"  - Python: {sys.version}")

if __name__ == "__main__":
    try:
        system_info()
        performance_test()
    except Exception as e:
        print(f"性能测试失败: {e}")
        print("\n请确保:")
        print("1. Milvus 服务器正在运行")
        print("2. 环境变量配置正确")
        print("3. 有足够的内存和存储空间") 