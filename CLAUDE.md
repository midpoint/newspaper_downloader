# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python 3.12 project using uv for package management. It includes a newspaper/magazine PDF downloader for https://reader.jojokanbao.cn/

## Common Commands

```bash
# Run the main script
python main.py

# Install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate
```

## Environment Setup

The `m25.sh` script configures MiniMax API access for Claude Code. Source it before running Claude if you need API access:

```bash
source m25.sh
```

This sets:
- `ANTHROPIC_BASE_URL` - MiniMax API endpoint
- `ANTHROPIC_AUTH_TOKEN` - API authentication token
- `ANTHROPIC_MODEL` - Default model (MiniMax-M2.5)
- `API_TIMEOUT_MS` - 3 second timeout

## Project Structure

- `main.py` - Entry point
- `downloader.py` - Newspaper/magazine PDF downloader
- `pyproject.toml` - Project configuration
- `downloads/` - Downloaded PDF files
- `.venv/` - Virtual environment (created by uv)

## Newspaper Downloader

Download newspapers/magazines from https://reader.jojokanbao.cn/ as PDF files:

```bash
# Download single issue
python downloader.py https://reader.jojokanbao.cn/rmhb/197201

# Download with custom filename
python downloader.py https://reader.jojokanbao.cn/rmhb/197201 my_file

# Batch download (multiple issues)
python downloader.py --batch "https://reader.jojokanbao.cn/rmhb/1972{issue:02d}" 1 12
```

Supported newspaper types:
- `rmhb` - 人民画报 (People's Pictorial)
- `rmrb` - 人民日报 (People's Daily)
- `ckxx` - 参考消息 (Reference News)
- `hq` - 红旗 (Red Flag)
- `sjzs` - 世界知识 (World Knowledge)
