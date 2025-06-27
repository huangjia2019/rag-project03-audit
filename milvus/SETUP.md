# Milvus 配置和部署说明

## 概述

本项目支持两种 Milvus 配置模式：
1. **本地模式（local）**: 使用文件数据库（需要 milvus-lite，仅支持 Ubuntu/MacOS）
2. **远程模式（remote）**: 连接到远程 Milvus 服务器（支持 Windows）

## 配置模式选择

通过环境变量 `MILVUS_MODE` 来控制使用哪种模式：

```bash
# 使用本地文件数据库（默认）
set MILVUS_MODE=local

# 使用远程 Milvus 服务器
set MILVUS_MODE=remote
```

## 方案1：本地模式（Ubuntu/MacOS）

**注意：** 此模式仅在 Ubuntu 和 MacOS 上受支持，Windows 不支持。

### 特点
- 使用文件数据库存储
- 数据持久化
- 无需额外服务器

### 配置
```bash
set MILVUS_MODE=local
```

使用默认的本地文件数据库配置：`../backend/03-vector-store/langchain_milvus.db`

## 方案2：远程模式

### 方案2.1：使用 Docker 部署 Milvus（推荐）

#### Windows 安装前提条件
- 安装 Docker Desktop for Windows
- 至少 4GB 可用内存

#### 部署步骤

1. 启动 Milvus 服务器：
```bash
cd milvus
docker-compose up -d
```

2. 等待服务启动（约1-2分钟），检查服务状态：
```bash
docker-compose ps
```

3. 设置环境变量使用远程模式：
```bash
set MILVUS_MODE=remote
set MILVUS_URI=http://localhost:19530
```

4. 启动应用程序：
```bash
cd ..
python backend/main.py
```

#### 服务端口
- Milvus: `http://localhost:19530`
- Attu（管理界面）: `http://localhost:3000`
- MinIO（对象存储）: `http://localhost:9001`

#### 停止服务
```bash
cd milvus
docker-compose down
```

#### 清理数据
```bash
cd milvus
docker-compose down -v
```

### 方案2.2：使用云端 Milvus 服务

#### Zilliz Cloud
1. 注册 [Zilliz Cloud](https://cloud.zilliz.com/) 账号
2. 创建集群并获取连接信息
3. 设置环境变量：
```bash
set MILVUS_MODE=remote
set MILVUS_URI=https://your-endpoint.serverless.gcp-us-west1.cloud.zilliz.com
set MILVUS_TOKEN=your-token
```

## 环境变量配置

### 基本配置
```bash
# 配置模式
set MILVUS_MODE=remote

# 远程 Milvus 服务器地址
set MILVUS_URI=http://localhost:19530
```

### 认证配置（可选）
```bash
# 用户名密码认证
set MILVUS_USER=username
set MILVUS_PASSWORD=password

# 或者 Token 认证
set MILVUS_TOKEN=your-token
```

## 测试连接

运行以下命令测试 Milvus 连接：

```python
# 从项目根目录运行
cd ..
python milvus/test_connection.py

# 或者使用 Python 代码测试
import sys
sys.path.append('backend')
from utils.config import get_milvus_config
from pymilvus import connections

config = get_milvus_config()
print(f"当前配置: {config}")

try:
    connections.connect(
        alias="test",
        uri=config["uri"],
        user=config.get("user", ""),
        password=config.get("password", ""),
        token=config.get("token", "")
    )
    print("Milvus 连接成功！")
    connections.disconnect("test")
except Exception as e:
    print(f"连接失败: {e}")
```

## 故障排除

### 1. Windows 上的 "No module named 'milvus_lite'" 错误
- **原因**: milvus-lite 不支持 Windows
- **解决**: 使用远程模式（`MILVUS_MODE=remote`）

### 2. Docker 启动失败
- 检查 Docker Desktop 是否正在运行
- 确保端口 19530, 9091, 3000, 9001, 9000 未被占用
- 检查系统内存是否足够（至少4GB）

### 3. 连接超时
- 确保 Milvus 服务器已完全启动
- 检查防火墙设置
- 验证网络连接

### 4. 权限错误
- 确保环境变量设置正确
- 检查用户名、密码或 Token 是否有效

## 性能建议

### 本地模式
- 适合开发和小规模测试
- 单机性能限制

### 远程模式
- 适合生产环境
- 可扩展性更好
- 支持集群部署

## 数据迁移

从本地模式迁移到远程模式时，需要重新创建索引和导入数据，因为两种模式使用不同的存储后端。 