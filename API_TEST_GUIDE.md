# TCP/HTTP 博客系统 API 测试指南

## 启动服务器
```bash
conda activate net
python main.py
```
服务器默认运行在 http://127.0.0.1:8080

## API 接口测试

### 1. 用户注册
```bash
curl -X POST http://127.0.0.1:8080/api/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"123456","nickname":"测试用户","email":"test@example.com"}'
```

### 2. 用户登录
```bash
curl -X POST http://127.0.0.1:8080/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"123456"}' \
  -c cookies.txt
```

### 3. 查看当前用户信息
```bash
curl -X GET http://127.0.0.1:8080/api/session \
  -b cookies.txt
```

### 4. 发布文章
```bash
curl -X POST http://127.0.0.1:8080/api/posts \
  -H "Content-Type: application/json" \
  -d '{"title":"我的第一篇文章","body":"这是文章内容","tags":"测试,博客"}' \
  -b cookies.txt
```

### 5. 查看文章列表
```bash
curl -X GET http://127.0.0.1:8080/api/posts
```

### 6. 查看特定文章
```bash
curl -X GET http://127.0.0.1:8080/api/posts/1
```

### 7. 添加评论
```bash
curl -X POST http://127.0.0.1:8080/api/posts/1/comments \
  -H "Content-Type: application/json" \
  -d '{"body":"这是一条评论"}' \
  -b cookies.txt
```

### 8. 点赞文章
```bash
curl -X POST http://127.0.0.1:8080/api/posts/1/reaction \
  -H "Content-Type: application/json" \
  -d '{"reaction":"like"}' \
  -b cookies.txt
```

### 9. 关注作者
```bash
curl -X POST http://127.0.0.1:8080/api/authors/1/follow \
  -b cookies.txt
```

### 10. 发送私信
```bash
curl -X POST http://127.0.0.1:8080/api/messages \
  -H "Content-Type: application/json" \
  -d '{"receiver_id":2,"subject":"问候","body":"你好！"}' \
  -b cookies.txt
```

## 数据库设置

1. 启动 MySQL 服务
2. 执行以下命令创建数据库：
```sql
mysql -u root -p < db/schema.sql
```

或者在 MySQL 命令行中：
```sql
source /path/to/your/project/db/schema.sql;
```

## 配置文件

可以创建 `.env` 文件来覆盖默认配置：
```
BLOG_HOST=127.0.0.1
BLOG_PORT=8080
BLOG_DB_HOST=127.0.0.1
BLOG_DB_PORT=3306
BLOG_DB_USER=root
BLOG_DB_PASSWORD=your_password
BLOG_DB_NAME=tcp_blog
```