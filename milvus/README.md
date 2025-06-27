# Milvus 部署和配置指南

本文件夹包含所有与 Milvus 向量数据库相关的配置、部署和管理文件。

## 📁 文件结构

```
milvus/
├── README.md                   # 本文件 - 总体说明
├── SETUP.md                   # 详细部署说明
├── docker-compose.yml         # Docker 部署配置
├── switch_to_remote.bat      # Windows 快速切换脚本  
├── test_connection.py        # 连接测试脚本
└── examples/                 # 使用示例
    ├── basic_usage.py        # 基础使用示例
    └── performance_test.py   # 性能测试示例
```

## 🚀 快速开始

### Windows 用户（推荐）

1. **安装 Docker Desktop**
2. **启动 Milvus 服务**：
   ```bash
   cd milvus
   docker-compose up -d
   ```
3. **切换到远程模式**：
   ```bash
   ./switch_to_remote.bat
   ```
4. **测试连接**：
   ```bash
   python test_connection.py
   ```

### Ubuntu/MacOS 用户

可以选择本地模式或远程模式：

#### 本地模式（使用 milvus-lite）
```bash
set MILVUS_MODE=local
python test_connection.py
```

#### 远程模式（使用 Docker）
```bash
cd milvus
docker-compose up -d
set MILVUS_MODE=remote
python test_connection.py
```

## 🛠️ 配置选项

### 环境变量

| 变量名 | 说明 | 默认值 | 示例 |
|--------|------|---------|------|
| `MILVUS_MODE` | 连接模式 | `local` | `remote` |
| `MILVUS_URI` | 服务器地址 | `http://localhost:19530` | `https://your-endpoint.com` |
| `MILVUS_USER` | 用户名 | 空 | `username` |
| `MILVUS_PASSWORD` | 密码 | 空 | `password` |
| `MILVUS_TOKEN` | 访问令牌 | 空 | `your-token` |

### 模式说明

- **本地模式（local）**：使用文件数据库，仅支持 Ubuntu/MacOS
- **远程模式（remote）**：连接到远程 Milvus 服务器，支持所有平台

## 🌐 访问地址

启动 Docker 服务后，可以访问：

- **Milvus API**: http://localhost:19530
- **Attu 管理界面**: http://localhost:3000
- **MinIO 对象存储**: http://localhost:9001

## 📋 管理命令

```bash
# 启动服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs milvus

# 停止服务
docker-compose down

# 清理数据（谨慎使用）
docker-compose down -v
```

## 🔧 故障排除

### 常见问题

1. **Windows 上 "No module named 'milvus_lite'" 错误**
   - 原因：milvus-lite 不支持 Windows
   - 解决：使用远程模式

2. **Docker 启动失败**
   - 检查 Docker Desktop 是否运行
   - 确保端口未被占用
   - 检查系统内存（至少 4GB）

3. **连接超时**
   - 等待服务完全启动（1-2分钟）
   - 检查防火墙设置
   - 验证网络连接

### 诊断工具

```bash
# 测试连接
python test_connection.py

# 检查服务状态
docker-compose ps

# 查看详细日志
docker-compose logs --tail 50 milvus
```

## 📚 更多资源

- [Milvus 官方文档](https://milvus.io/docs)
- [Attu 管理工具](https://github.com/zilliztech/attu)
- [Zilliz Cloud](https://cloud.zilliz.com/)

## 🤝 支持

如果遇到问题，请查看：
1. `SETUP.md` - 详细配置说明  
2. `test_connection.py` - 连接诊断
3. 项目根目录的 `install_cpu_instructions.md` 