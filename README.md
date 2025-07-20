# 朋友动态后端 API

本项目是一个基于 Flask 的后端服务，用于聚合和展示朋友站点的最新文章动态。  
通过读取 MySQL 数据库中的友链和文章数据，提供统一的 API 接口，便于前端展示。

# 相关项目
- [Friends 前端展示](https://github.com/lusyoe/friends-frontend)
- [Friends 定时任务](https://github.com/lusyoe/friends-rss-fetch)

[博客地址-青萍叙事](https://blog.lusyoe.com)

## 功能特性

- 查询所有激活的友链站点（is_active=1）。
- 每个站点返回最近半年内的最多 3 篇文章（如不足 3 篇，则补足更早的文章）。
- 仅展示最近半年内有更新的站点。
- 文章时间自动格式化为 `YYYY-MM-DD`。
- 支持跨域请求（CORS）。

## 安装依赖

```bash
pip install -r requirements.txt
```

## 环境变量配置

在项目根目录下新建 `.env` 文件，内容如下：

```
DB_HOST=<你的数据库IP地址>
DB_USER=<数据库用户名>
DB_PASSWORD=<数据库密码>
DB_NAME=blog
```

## 启动服务

```bash
python app.py
```

默认监听在 `0.0.0.0:5001`，可通过 `http://<服务器IP>:5001/api/sites` 访问接口。

## API 说明

### 获取所有活跃站点及其最新文章

- **接口地址**：`GET /api/sites`
- **返回示例**：

```json
[
  {
    "id": 1,
    "name": "示例站点",
    "logo": "https://example.com/logo.png",
    "description": "这是一个示例友链站点",
    "url": "https://example.com",
    "last_fetched_at": "2024-06-01 12:00:00",
    "articles": [
      {
        "title": "最新文章标题",
        "link": "https://example.com/article1",
        "created_at": "2024-05-30"
      }
      // ... 最多3篇
    ]
  }
  // ... 更多站点
]
```

- **说明**：
  - 仅返回最近半年内有新文章的站点。
  - 每个站点最多返回 3 篇文章，优先展示最近半年的文章，不足则补足更早的。

## 依赖环境

- Python 3.7+
- Flask
- flask-cors
- mysql-connector-python
- python-dotenv

## Docker 镜像构建与启动

### 构建镜像

在项目根目录下执行：

```bash
docker build -t friends-api:latest .
```

### 运行容器

假设你已经准备好 `.env` 文件，可以通过挂载方式传递环境变量：

```bash
docker run -d \
  --name friends-api \
  -p 5001:5001 \
  --env-file .env \
  friends-api:latest
```

- `-p 5001:5001`：将容器的 5001 端口映射到主机。
- `--env-file .env`：加载本地的环境变量配置。

如需挂载代码目录以便开发调试，可加上：

```bash
docker run -d \
  --name friends-api \
  -p 5001:5001 \
  --env-file .env \
  -v $(pwd):/app \
  friends-api:latest
```

## 数据库表结构
可参看项目 `scripts/friends.sql` 文件，需要提前导入到数据库中，字段详细说明如下：
### friend_links 表（友链站点信息）
存储友链站点的基本信息，包含以下字段：
- `id` (int, 主键, 自增)：站点唯一标识
- `name` (varchar(255))：站点名称
- `url` (varchar(512))：站点URL地址
- `logo` (varchar(512), 可选)：站点logo图片URL
- `rss_url` (varchar(512), 可选)：RSS订阅地址
- `description` (text, 可选)：站点描述
- `is_active` (tinyint(1), 默认1)：是否激活状态
- `fetch_failed_count` (int, 默认0)：RSS抓取失败次数
- `last_fetch_status` (varchar(50), 可选)：最后一次抓取状态
- `last_fetched_at` (datetime, 可选)：最后一次抓取时间
- `created_at` (datetime, 可选)：创建时间
- `updated_at` (datetime, 可选)：更新时间

### friend_rss_articles 表（文章信息）
存储从友链站点抓取的文章信息，包含以下字段：
- `id` (int, 主键, 自增)：文章唯一标识
- `friend_id` (bigint)：关联的友链站点ID
- `title` (varchar(512))：文章标题
- `link` (varchar(1024))：文章链接
- `created_at` (datetime, 可选)：文章发布时间

### friend_rss_fetch_logs 表（抓取日志）
记录RSS抓取的历史日志，包含以下字段：
- `id` (int, 主键, 自增)：日志唯一标识
- `friend_id` (bigint)：关联的友链站点ID
- `rss_url` (varchar(512))：抓取的RSS地址
- `status` (varchar(50))：抓取状态
- `http_status` (int, 可选)：HTTP响应状态码
- `message` (text, 可选)：抓取结果消息
- `fetched_at` (datetime, 可选)：抓取时间

---

如需进一步定制或有疑问，欢迎提 issue 或联系作者。