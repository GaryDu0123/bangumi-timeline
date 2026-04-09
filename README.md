# bangumi

HoshinoBot 的 Bangumi 时间线订阅插件。

插件支持按群订阅 Bangumi 用户，定时抓取这些用户最近的时间线动态，并将合并后的动态渲染为图片推送到群内。

## 功能特性

- 按群订阅一个或多个 Bangumi 用户
- 定时轮询用户时间线
- 将多个订阅用户的动态合并后统一推送
- 自动记录用户昵称，展示时优先使用昵称

## 当前实现说明

- 当前主要使用 Bangumi 用户时间线页面抓取数据
- 每轮轮询会抓取配置时间窗口内的最新动态
- 每个群会收到一张合并后的时间线图片
- 渲染依赖 Playwright 截图

## 目录结构

```text
bangumi-timeline/
├─ bgm.py            # 插件入口、命令注册、定时任务
├─ config.py         # 配置项
├─ http_client.py    # HTTP 请求封装
├─ models.py         # 数据模型
├─ poller.py         # 轮询与群消息推送逻辑
├─ render.py         # 时间线图片渲染
├─ storage.py        # 本地 JSON 存储
├─ timeline.py       # Bangumi 时间线抓取与解析
└─ data/             # 启动后自动创建
   ├─ subs.json      # 群订阅关系
   └─ nickname.json  # 用户昵称缓存
```

## 安装方式

将本目录放到 HoshinoBot 的模块目录下：

```text
hoshino/modules/bangumi-timeline
```

## 依赖

除了 HoshinoBot 本体外，还需要以下 Python 依赖：

```bash
pip install playwright
```

安装 Playwright 浏览器：

```bash
playwright install chromium
```

如果你的运行环境缺少系统字体，渲染出来的中文样式可能不理想，需要自行补充字体环境。


## 配置说明

配置文件为 config.py。

可调整的主要配置项如下：

- `POLL_MINUTES`：轮询间隔，当前为 `60`，即 1 小时
- `USER_AGENT`：请求 Bangumi 时使用的 UA
- `TIMEOUT_SEC`：HTTP 请求超时时间
- `CONCURRENCY`：并发抓取用户时间线的上限
- `BANGUMI_URL`：Bangumi 主站地址
- `BGM_API_URL`：Bangumi API 地址
- `TIMELINE_MAX_PAGES_PER_USER`：每轮每个用户最多抓取的时间线页数
- `DATA_DIRNAME`：数据目录名
- `SUBS_FILENAME`：订阅存储文件名
- `NICKNAME_FILENAME`：昵称缓存文件名

## 使用命令

### 订阅用户

```text
bgm订阅用户 <用户名>
bangumi订阅用户 <用户名>
```

效果：

- 校验用户是否存在
- 写入当前群的订阅列表
- 缓存该用户昵称
- 返回用户名、昵称和用户主页链接

### 取消订阅用户

```text
bgm取消订阅用户 <用户名>
bangumi取消订阅用户 <用户名>
```

### 查看当前群订阅列表

```text
bgm订阅列表
bangumi订阅列表
```

### 更新昵称缓存

```text
bgm更新昵称 <用户名>
bangumi更新昵称 <用户名>
bgm update nickname <用户名>
```

### 手动测试轮询

```text
bgmtest
```

该命令会直接执行一次轮询任务，便于调试是否能够正常抓取和推送。

## 数据存储

插件会在 [data](/E:/ProjectD/server/hoshino/modules/bangumi/data) 目录下自动创建以下文件：

- `subs.json`：保存各个群订阅了哪些 Bangumi 用户
- `nickname.json`：保存订阅用户对应的昵称缓存

`subs.json` 大致结构如下：

```json
{
  "groups": {
    "123456": {
      "users": {
        "some_user": true
      }
    }
  }
}
```

## 工作流程

1. 定时任务按 `POLL_MINUTES` 周期运行
2. 聚合所有群订阅过的 Bangumi 用户
3. 并发抓取这些用户最近的时间线页面
4. 根据群订阅关系组合出每个群自己的动态流
5. 使用 Playwright 将动态流渲染成图片
6. 发送到对应群聊

## 注意事项

- 请尽量在群聊中使用订阅相关命令
- 用户名应填写 Bangumi 用户唯一标识，而不是单纯昵称
- 如果 Playwright 或 Chromium 未正确安装，图片渲染会失败
- 如果 Bangumi 页面结构发生变化，时间线解析逻辑可能需要同步调整
- 当前版本没有“已推送事件去重记录”，如果轮询窗口覆盖了同一批动态，理论上可能重复推送

## 适用场景

- 追踪群友最近看了什么番、动画、书、游戏
- 在群内汇总多个 Bangumi 用户的动态
- 作为 Bangumi 时间线订阅和图片推送的基础实现继续扩展

