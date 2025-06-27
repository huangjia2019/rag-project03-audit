from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
from pymilvus import connections, Collection, utility
from services.embedding_service import EmbeddingService
from utils.config import VectorDBProvider, get_milvus_config
import os
import json

logger = logging.getLogger(__name__)

class SearchService:
    """
    搜索服务类，负责向量数据库的连接和向量搜索功能
    提供集合列表查询、向量相似度搜索和搜索结果保存等功能
    """
    def __init__(self):
        """
        初始化搜索服务
        创建嵌入服务实例，设置Milvus连接配置，初始化搜索结果保存目录
        """
        self.embedding_service = EmbeddingService()
        self.milvus_config = get_milvus_config()
        self.milvus_uri = self.milvus_config["uri"]
        self.search_results_dir = "04-search-results"
        os.makedirs(self.search_results_dir, exist_ok=True)

    def _connect_to_milvus(self):
        """
        连接到Milvus数据库，支持本地和远程连接
        """
        connection_params = {
            "alias": "default",
            "uri": self.milvus_uri
        }
        
        # 如果是远程连接，添加认证参数
        if self.milvus_config.get("user"):
            connection_params["user"] = self.milvus_config["user"]
        if self.milvus_config.get("password"):
            connection_params["password"] = self.milvus_config["password"]
        if self.milvus_config.get("token"):
            connection_params["token"] = self.milvus_config["token"]
        
        connections.connect(**connection_params)

    def get_providers(self) -> List[Dict[str, str]]:
        """
        获取支持的向量数据库列表
        
        Returns:
            List[Dict[str, str]]: 支持的向量数据库提供商列表
        """
        return [
            {"id": VectorDBProvider.MILVUS.value, "name": "Milvus"}
        ]

    def list_collections(self, provider: str = VectorDBProvider.MILVUS.value) -> List[Dict[str, Any]]:
        """
        获取指定向量数据库中的所有集合
        
        Args:
            provider (str): 向量数据库提供商，默认为Milvus
            
        Returns:
            List[Dict[str, Any]]: 集合信息列表，包含id、名称和实体数量
            
        Raises:
            Exception: 连接或查询集合时发生错误
        """
        try:
            self._connect_to_milvus()
            
            collections = []
            collection_names = utility.list_collections()
            
            for name in collection_names:
                try:
                    collection = Collection(name)
                    collections.append({
                        "id": name,
                        "name": name,
                        "count": collection.num_entities
                    })
                except Exception as e:
                    logger.error(f"Error getting info for collection {name}: {str(e)}")
            
            return collections
            
        except Exception as e:
            logger.error(f"Error listing collections: {str(e)}")
            raise
        finally:
            connections.disconnect("default")

    def save_search_results(self, query: str, collection_id: str, results: List[Dict[str, Any]]) -> str:
        """
        保存搜索结果到JSON文件
        
        Args:
            query (str): 搜索查询文本
            collection_id (str): 集合ID
            results (List[Dict[str, Any]]): 搜索结果列表
            
        Returns:
            str: 保存文件的路径
            
        Raises:
            Exception: 保存文件时发生错误
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            # 使用集合ID的基础名称（去掉路径相关字符）
            collection_base = os.path.basename(collection_id)
            filename = f"search_{collection_base}_{timestamp}.json"
            filepath = os.path.join(self.search_results_dir, filename)
            
            search_data = {
                "query": query,
                "collection_id": collection_id,
                "timestamp": datetime.now().isoformat(),
                "results": results
            }
            
            logger.info(f"Saving search results to: {filepath}")
            
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(search_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Successfully saved search results to: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving search results: {str(e)}")
            raise

    async def search(self, 
                    query: str, 
                    collection_id: str, 
                    top_k: int = 3, 
                    threshold: float = 0.7,
                    word_count_threshold: int = 20,
                    save_results: bool = False) -> Dict[str, Any]:
        """
        执行向量搜索
        
        Args:
            query (str): 搜索查询文本
            collection_id (str): 要搜索的集合ID
            top_k (int): 返回的最大结果数量，默认为3
            threshold (float): 相似度阈值，低于此值的结果将被过滤，默认为0.7
            word_count_threshold (int): 文本字数阈值，低于此值的结果将被过滤，默认为20
            save_results (bool): 是否保存搜索结果，默认为False
            
        Returns:
            Dict[str, Any]: 包含搜索结果的字典，如果保存结果则包含保存路径
            
        Raises:
            Exception: 搜索过程中发生错误
        """
        try:
            # 添加参数日志
            logger.info(f"Search parameters:")
            logger.info(f"- Query: {query}")
            logger.info(f"- Collection ID: {collection_id}")
            logger.info(f"- Top K: {top_k}")
            logger.info(f"- Threshold: {threshold}")
            logger.info(f"- Word Count Threshold: {word_count_threshold}")
            logger.info(f"- Save Results: {save_results} (type: {type(save_results)})")

            logger.info(f"Starting search with parameters - Collection: {collection_id}, Query: {query}, Top K: {top_k}")
            
            # 连接到 Milvus
            logger.info(f"Connecting to Milvus at {self.milvus_uri}")
            self._connect_to_milvus()
            
            # 获取collection
            logger.info(f"Loading collection: {collection_id}")
            collection = Collection(collection_id)
            collection.load()
            
            # 记录collection的基本信息
            logger.info(f"Collection info - Entities: {collection.num_entities}")
            
            # 从collection中读取embedding配置
            logger.info("Querying sample entity for embedding configuration")
            sample_entity = collection.query(
                expr="id >= 0", 
                output_fields=["embedding_provider", "embedding_model"],
                limit=1
            )
            if not sample_entity:
                logger.error(f"Collection {collection_id} is empty")
                raise ValueError(f"Collection {collection_id} is empty")
            
            logger.info(f"Sample entity configuration: {sample_entity[0]}")
            
            # 使用collection中存储的配置创建查询向量
            logger.info("Creating query embedding")
            query_embedding = self.embedding_service.create_single_embedding(
                query,
                provider=sample_entity[0]["embedding_provider"],
                model=sample_entity[0]["embedding_model"]
            )
            logger.info(f"Query embedding created with dimension: {len(query_embedding)}")
            
            # 执行搜索
            search_params = {
                "metric_type": "COSINE",
                "params": {"nprobe": 10}
            }
            logger.info(f"Executing search with params: {search_params}")
            logger.info(f"Word count threshold filter: word_count >= {word_count_threshold}")
            
            results = collection.search(
                data=[query_embedding],
                anns_field="vector",
                param=search_params,
                limit=top_k,
                expr=f"word_count >= {word_count_threshold}",
                output_fields=[
                    "content",
                    "document_name",
                    "chunk_id",
                    "total_chunks",
                    "word_count",
                    "page_number",
                    "page_range",
                    "embedding_provider",
                    "embedding_model",
                    "embedding_timestamp"
                ]
            )
            
            # 处理结果
            processed_results = []
            logger.info(f"Raw search results count: {len(results[0])}")
            
            for hits in results:
                for hit in hits:
                    logger.info(f"Processing hit - Score: {hit.score}, Word Count: {hit.entity.get('word_count')}")
                    if hit.score >= threshold:
                        processed_results.append({
                            "text": hit.entity.content,
                            "score": float(hit.score),
                            "metadata": {
                                "source": hit.entity.document_name,
                                "page": hit.entity.page_number,
                                "chunk": hit.entity.chunk_id,
                                "total_chunks": hit.entity.total_chunks,
                                "page_range": hit.entity.page_range,
                                "embedding_provider": hit.entity.embedding_provider,
                                "embedding_model": hit.entity.embedding_model,
                                "embedding_timestamp": hit.entity.embedding_timestamp
                            }
                        })

            response_data = {"results": processed_results}
            
            # 添加详细的保存逻辑日志
            logger.info(f"Preparing to handle save_results (flag: {save_results})")
            if save_results:
                logger.info("Save results is True, attempting to save...")
                if processed_results:
                    try:
                        filepath = self.save_search_results(query, collection_id, processed_results)
                        logger.info(f"Successfully saved results to: {filepath}")
                        response_data["saved_filepath"] = filepath
                    except Exception as e:
                        logger.error(f"Error saving results: {str(e)}")
                        response_data["save_error"] = str(e)
                        raise  # 添加这行来查看完整的错误堆栈
                else:
                    logger.info("No results to save")
            else:
                logger.info("Save results is False, skipping save")
            
            return response_data
            
        except Exception as e:
            logger.error(f"Error performing search: {str(e)}")
            raise
        finally:
            connections.disconnect("default") 