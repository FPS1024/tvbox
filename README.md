# TVBox 接口解析工具

这是一个简单的 TVBox 接口解析工具，用于从接口地址获取配置并保存为 JSON 文件。

## 功能

- ✅ 从 `api-key.txt` 读取接口地址
- ✅ 使用 TVBox 专用请求头（避免被标记为爬虫）
- ✅ 解析接口返回的 JSON 配置
- ✅ 保存为 `tvbox_config.json` 文件

## 安装依赖

```bash
pip3 install -r requirements.txt
```

## 使用方法

### 1. 配置接口地址

在 `api-key.txt` 文件中写入接口地址（每行一个）：

```
http://v.esirtv.top/api/index.php?sign=xxxxxxxxxxxxxxxx
```

### 2. 解析主接口配置

```bash
python3 parse_api.py
```

解析成功后，会生成 `tvbox_config.json` 文件，包含完整的 TVBox 配置（站点列表和直播源）。

### 3. 解析所有站点配置（可选）

如果需要获取每个站点的详细配置：

```bash
python3 parse_sites.py
```

脚本会：
- 读取 `tvbox_config.json` 中的站点列表
- 使用相同的请求头访问每个站点的 API
- 将每个站点的配置保存到 `sites/` 文件夹
- 按照站点名称命名文件（如 `11.json`、`12.json`）

**注意**: 脚本会在每个请求之间延迟 0.5 秒，避免请求过快。

### 4. 获取视频播放链接（可选）

如果需要为每个视频获取播放链接：

```bash
python3 fetch_play_urls.py
```

脚本会：
- 读取 `sites/` 文件夹中的所有站点 JSON 文件
- 对每个视频，通过 API 获取详情（使用 `ac=detail&ids=vod_id`）
- 提取播放链接（`vod_play_url` 和 `vod_play_from`）
- 更新到对应的 JSON 文件中

**注意**: 
- 脚本会在每个请求之间延迟 0.3 秒，避免请求过快
- 如果视频已有播放链接，会自动跳过
- 处理所有站点可能需要较长时间

## 反爬虫策略

工具使用 TVBox Android 客户端专用的请求头：

- **User-Agent**: `okhttp/3.12.0` (TVBox 客户端使用的 HTTP 库)
- **Accept**: `application/json, text/plain, */*`
- **Accept-Encoding**: `gzip, deflate`
- **Connection**: `keep-alive`

这些请求头可以确保请求被识别为 TVBox 客户端，而不是爬虫。

## 输出示例

```
从 api-key.txt 读取接口地址: http://v.esirtv.top/api/index.php?sign=xxxxxxxxxxxxxxxx

正在解析接口: http://v.esirtv.top/api/index.php?sign=xxxxxxxxxxxxxxxx
--------------------------------------------------------------------------------
响应状态码: 200
Content-Type: application/json
响应长度: 3303 字节
✅ JSON 解析成功!
✅ 配置验证通过:
   - 站点数量: 20
   - 直播源组数: 1

✅ 配置已保存到: tvbox_config.json

================================================================================
✅ 接口解析完成！
================================================================================
```

## 文件说明

- `api-key.txt` - 接口地址配置文件
- `parse_api.py` - 主接口解析脚本（生成 tvbox_config.json）
- `parse_sites.py` - 站点配置解析脚本（生成 sites/*.json）
- `fetch_play_urls.py` - 播放链接获取脚本（更新 sites/*.json，添加播放链接）
- `tvbox_config.json` - 主配置文件（自动生成）
- `sites/` - 站点配置文件夹（自动生成）
  - `ئەسىر.json`、`ئەسىر19.json` 等 - 各站点的配置文件
- `requirements.txt` - Python 依赖

## 注意事项

- 请确保接口地址有效
- 工具会自动验证配置格式
- 如果接口返回的不是 JSON 格式，会显示警告信息
