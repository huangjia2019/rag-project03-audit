# Windows CPU版本安装说明

## 概述
由于您的电脑没有GPU，我们创建了专门的CPU版本依赖文件 `requirements_win_cpu.txt`，它移除了所有NVIDIA CUDA相关的包。

**重要提示：** Milvus Lite 目前不支持 Windows 系统。在 Windows 上只能使用内存模式或远程 Milvus 服务器。

## 已移除的GPU相关包
以下包已从CPU版本中移除：
- `milvus-lite==2.4.9` (在Windows上不支持)
- `nvidia-cublas-cu12==12.1.3.1`
- `nvidia-cuda-cupti-cu12==12.1.105`
- `nvidia-cuda-nvrtc-cu12==12.1.105`
- `nvidia-cuda-runtime-cu12==12.1.105`
- `nvidia-cudnn-cu12==9.1.0.70`
- `nvidia-cufft-cu12==11.0.2.54`
- `nvidia-curand-cu12==10.3.2.106`
- `nvidia-cusolver-cu12==11.4.5.107`
- `nvidia-cusparse-cu12==12.1.0.106`
- `nvidia-nccl-cu12==2.20.5`
- `nvidia-nvjitlink-cu12==12.6.20`
- `nvidia-nvtx-cu12==12.1.105`
- `torch==2.4.0` (需要CPU版本)
- `torchaudio==2.4.0` (需要CPU版本)
- `torchvision==0.19.0` (需要CPU版本)
- `triton==3.0.0` (GPU专用)

## 安装方法

### 方法1：使用CPU专用PyTorch索引（推荐）
```bash
# 步骤1：安装CPU版本的PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# 步骤2：安装其他依赖
pip install -r requirements_win_cpu.txt
```

### 方法2：如果遇到冲突
```bash
# 清理可能的冲突
pip uninstall torch torchvision torchaudio -y

# 重新安装
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements_win_cpu.txt
```

### 方法3：一次性安装所有依赖
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu && pip install -r requirements_win_cpu.txt
```

## 验证安装
安装完成后，可以运行以下命令验证：

```python
import torch
print(f"PyTorch版本: {torch.__version__}")
print(f"CUDA可用: {torch.cuda.is_available()}")  # 应该显示False

import pymilvus
print(f"Milvus版本: {pymilvus.__version__}")

# 测试Milvus（内存模式，无需milvus-lite）
from pymilvus import MilvusClient
client = MilvusClient(":memory:")  # 使用内存模式
print("Milvus内存模式连接成功！")
```

## Windows 上的 Milvus 解决方案

**重要提示：** 详细的 Milvus 配置和部署说明已移至专门的文件夹中：

📁 **[milvus/ 文件夹](milvus/)** - 包含完整的 Milvus 部署方案

主要解决方案：
- **本地模式**：仅支持 Ubuntu/MacOS（使用文件数据库）
- **远程模式**：支持 Windows（使用 Docker 部署）

快速开始（Windows 用户）：
```bash
# 1. 进入 milvus 目录
cd milvus

# 2. 启动 Docker 服务
docker-compose up -d

# 3. 切换到远程模式
./switch_to_remote.bat

# 4. 测试连接
python test_connection.py
```

## 文件对比
- `requirements_win.txt`: 原始文件（包含GPU依赖和milvus-lite）
- `requirements_win_cpu.txt`: CPU专用文件（移除了GPU依赖和milvus-lite）

## 注意事项
1. 由于使用CPU版本，模型训练和推理速度会比GPU版本慢
2. 某些深度学习操作可能需要更多内存
3. **Windows 系统不支持 milvus-lite，只能使用内存模式或远程服务器**
4. 使用内存模式时，数据不会持久化保存
5. 所有RAG功能在CPU上都能正常工作 