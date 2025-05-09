# CATIA MCP服务

这是一个基于`pycatia`的CATIA自动化服务，提供了完整的REST API接口，用于远程控制和操作CATIA。

## 功能特点

- 完整的CATIA操作API支持
- RESTful API设计
- JWT认证保护
- 跨域支持
- 完整的日志记录
- 类型提示支持
- 异常处理机制

## 支持的功能

### 1. 文档操作
- 创建新文档（Part/Product/Drawing）
- 打开文档
- 保存文档
- 关闭文档

### 2. 参数操作
- 获取参数列表
- 设置参数值

### 3. 几何操作
- 创建点
- 创建线
- 创建平面

### 4. 草图操作
- 创建草图
- 添加线条
- 添加圆形

### 5. 特征操作
- 创建凸台
- 创建凹槽
- 创建旋转体

### 6. 装配操作
- 添加组件
- 创建约束

### 7. 测量操作
- 测量距离
- 测量角度
- 测量面积
- 测量体积

### 8. 分析操作
- 质量分析
- 干涉检查

### 9. 工程图操作
- 创建视图
- 添加尺寸

### 10. 系统操作
- 获取系统信息

## 安装要求

- Python 3.8+
- CATIA V5/V6
- pycatia 0.8.2+
- 其他依赖见requirements.txt

## 安装步骤

1. 克隆仓库：
```bash
git clone [repository_url]
cd catia-mcp-service
```

2. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 配置环境变量：
- 复制`.env.example`为`.env`
- 修改配置参数

## 运行服务

```bash
python catia_mcp_service.py
```

服务将在 http://localhost:5000 启动

## API使用示例

### 1. 连接CATIA
```python
import requests

# 获取JWT令牌
response = requests.post('http://localhost:5000/api/catia/connect', 
                        headers={'Authorization': f'Bearer {token}'})
```

### 2. 创建新文档
```python
response = requests.post('http://localhost:5000/api/catia/document',
                        json={
                            'operation': 'create',
                            'doc_type': 'Part'
                        },
                        headers={'Authorization': f'Bearer {token}'})
```

### 3. 创建几何体
```python
# 创建点
response = requests.post('http://localhost:5000/api/catia/geometry',
                        json={
                            'operation': 'point',
                            'x': 0,
                            'y': 0,
                            'z': 0
                        },
                        headers={'Authorization': f'Bearer {token}'})
```

## API文档

### 认证
所有API请求都需要在header中包含JWT令牌：
```
Authorization: Bearer <token>
```

### 主要端点

1. 连接CATIA
- POST `/api/catia/connect`

2. 文档操作
- POST `/api/catia/document`
  - operation: open/save/create/close

3. 参数操作
- GET `/api/catia/parameters`
- POST `/api/catia/parameters`

4. 几何操作
- POST `/api/catia/geometry`
  - operation: point/line/plane

5. 草图操作
- POST `/api/catia/sketch`
  - operation: create/add_line/add_circle

6. 特征操作
- POST `/api/catia/feature`
  - operation: pad/pocket/revolution

7. 装配操作
- POST `/api/catia/assembly`
  - operation: add_component/create_constraint

8. 测量操作
- POST `/api/catia/measure`
  - operation: distance/angle/area/volume

9. 分析操作
- POST `/api/catia/analysis`
  - operation: mass/interference

10. 工程图操作
- POST `/api/catia/drawing`
  - operation: create_view/add_dimension

11. 系统操作
- GET `/api/catia/system`

## 错误处理

所有API响应都遵循以下格式：
```json
{
    "status": "success/error",
    "message": "操作结果描述",
    "data": {} // 可选，成功时返回的数据
}
```

## 日志

服务运行日志保存在`catia_mcp.log`文件中，包含以下信息：
- 时间戳
- 日志级别
- 模块名
- 消息内容

## 注意事项

1. 确保CATIA已正确安装并可以正常运行
2. 使用前请先获取JWT令牌
3. 所有API调用都需要包含认证信息
4. 注意处理API返回的错误信息

## 贡献指南

1. Fork项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

MIT License

## 联系方式

如有问题，请提交Issue或联系维护者。 