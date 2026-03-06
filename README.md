# 电子报纸下载器

从 [JOJO看报](https://reader.jojokanbao.cn/) 下载报纸、杂志内容并打包为PDF文件。

## 功能特点

- 支持多种报纸杂志：人民日报、参考消息、人民画报、红旗、世界知识等
- 自动滚动页面加载所有图片（支持懒加载）
- 支持图片(img)和画布(canvas)两种渲染方式
- 将网页中的图片内容提取并合并为单个PDF文件
- 支持单期下载和批量下载

## 环境要求

- Python 3.12+
- uv 包管理器

## 安装

### 方式1：使用 uv（推荐）

```bash
# 创建虚拟环境
uv venv

# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
uv sync

# 安装Playwright浏览器
playwright install chromium
```

### 方式2：使用 pip

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装Playwright浏览器
playwright install chromium
```

## 使用方法

### 下载单期报纸

```bash
python downloader.py <URL> [输出文件名]
```

示例：

```bash
# 下载人民画报1972年1月
python downloader.py https://reader.jojokanbao.cn/rmhb/197201

# 指定输出文件名
python downloader.py https://reader.jojokanbao.cn/rmhb/197201 rmb_197201

# 下载人民日报
python downloader.py https://reader.jojokanbao.cn/rmrb/19761009
```

### 批量下载

```bash
python downloader.py --batch "<URL模板>" <起始期号> <结束期号>
```

示例：

```bash
# 下载1972年全年（共12期）
python downloader.py --batch "https://reader.jojokanbao.cn/rmhb/1972{issue:02d}" 1 12

# 下载1971年1-6月
python downloader.py --batch "https://reader.jojokanbao.cn/rmhb/1971{issue:02d}" 1 6

# 下载多日人民日报
python downloader.py --batch "https://reader.jojokanbao.cn/rmrb/1976{issue:04d}" 1009 1015
```

## 支持的报纸类型

| 代码 | 名称 | 示例URL |
|------|------|---------|
| rmhb | 人民画报 | https://reader.jojokanbao.cn/rmhb/197201 |
| rmrb | 人民日报 | https://reader.jojokanbao.cn/rmrb/19761009 |
| ckxx | 参考消息 | https://reader.jojokanbao.cn/ckxx/19760910 |
| hq | 红旗 | https://reader.jojokanbao.cn/hq/196419 |
| sjzs | 世界知识 | https://reader.jojokanbao.cn/sjzs/196513 |

## 输出

下载的PDF文件保存在 `downloads/` 目录下，临时图片文件会在转换完成后自动删除。

## 注意事项

- 下载过程会自动滚动页面加载所有图片，需要等待一段时间
- 部分历史报刊可能无法访问
- 请遵守网站的使用条款，仅供个人学习研究使用
