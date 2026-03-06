#!/usr/bin/env python3
"""
人民日报图片版下载器
用于下载 https://reader.jojokanbao.cn/ 上的报纸内容并打包为PDF
支持单期下载和批量下载
"""

import asyncio
import base64
import os
import re
import sys
from pathlib import Path

import img2pdf
import playwright.async_api


class NewspaperDownloader:
    def __init__(self, output_dir: str = "downloads"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    async def _scroll_to_load_all(self, page):
        """滚动页面以触发懒加载，获取所有图片"""
        print("  向下滚动加载更多图片...")

        max_scrolls = 60  # 最多滚动60次
        scroll_pause = 2  # 每次滚动后等待2秒
        last_count = 0
        no_change_count = 0

        for i in range(max_scrolls):
            # 滚动内部容器到底部
            await page.evaluate("""() => {
                const wrap = document.querySelector('.el-scrollbar__wrap');
                if (wrap) {
                    wrap.scrollTop = wrap.scrollHeight;
                }
            }""")

            await asyncio.sleep(scroll_pause)

            # 计算当前图片数量
            img_count = await page.evaluate("""() => {
                let count = 0;
                document.querySelectorAll('img').forEach(img => {
                    if (img.naturalWidth > 200 && img.naturalHeight > 200 && img.src.startsWith('blob:')) {
                        count++;
                    }
                });
                document.querySelectorAll('canvas').forEach(c => {
                    if (c.width > 100 && c.height > 100) {
                        count++;
                    }
                });
                return count;
            }""")

            print(f"    第{i+1}次: {img_count} 张")

            # 如果图片数量没有变化，增加计数器
            if img_count == last_count:
                no_change_count += 1
                if no_change_count >= 6:  # 连续6次（12秒）没有新图片
                    print(f"    图片加载稳定，停止滚动 (共 {img_count} 张)")
                    break
            else:
                no_change_count = 0

            last_count = img_count

        # 滚动回顶部
        await page.evaluate("""() => {
            const wrap = document.querySelector('.el-scrollbar__wrap');
            if (wrap) wrap.scrollTop = 0;
        }""")
        await asyncio.sleep(0.5)

    async def download_issue(self, url: str, filename: str = None) -> str:
        """下载单期报纸并转换为PDF"""
        print(f"正在访问: {url}")

        async with playwright.async_api.async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.set_viewport_size({"width": 1920, "height": 1080})

            try:
                await page.goto(url)
                await page.wait_for_load_state("networkidle")

                print("等待页面渲染...")
                await asyncio.sleep(5)  # 增加初始等待时间

                print("加载所有页面...")
                await self._scroll_to_load_all(page)

                print("正在提取图片...")

                image_data_list = await page.evaluate("""() => {
                    const result = [];
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');

                    // 处理img标签
                    document.querySelectorAll('img').forEach(img => {
                        const rect = img.getBoundingClientRect();
                        if (rect.width > 200 && rect.height > 200 && img.src.startsWith('blob:')) {
                            try {
                                canvas.width = img.naturalWidth || img.width;
                                canvas.height = img.naturalHeight || img.height;
                                ctx.drawImage(img, 0, 0);
                                const dataUrl = canvas.toDataURL('image/jpeg', 0.95);
                                result.push(dataUrl);
                            } catch(e) {}
                        }
                    });

                    // 处理canvas元素
                    document.querySelectorAll('canvas').forEach(c => {
                        if (c.width > 100 && c.height > 100) {
                            try {
                                const dataUrl = c.toDataURL('image/jpeg', 0.95);
                                result.push(dataUrl);
                            } catch(e) {}
                        }
                    });

                    return result;
                }""")

                print(f"提取到 {len(image_data_list)} 张图片")

                image_files = []

                for i, data_url in enumerate(image_data_list):
                    try:
                        img_data = base64.b64decode(data_url.split(',')[1])
                        img_path = self.output_dir / f"page_{i:03d}.jpg"

                        with open(img_path, 'wb') as f:
                            f.write(img_data)

                        image_files.append(str(img_path))
                        print(f"  保存: {img_path.name} ({len(img_data) / 1024:.1f} KB)")

                    except Exception as e:
                        print(f"  保存失败: {e}")

            finally:
                await browser.close()

        if not image_files:
            print("未能找到任何图片!")
            return None

        if not filename:
            match = re.search(r'/(\w+)/(\d+)', url)
            if match:
                filename = f"{match.group(1)}_{match.group(2)}"
            else:
                filename = "newspaper"

        image_files.sort()

        print("正在生成PDF...")
        pdf_path = self.output_dir / f"{filename}.pdf"

        try:
            with open(pdf_path, "wb") as f:
                f.write(img2pdf.convert(image_files))
            print(f"PDF已保存: {pdf_path}")

            for img_file in image_files:
                try:
                    os.remove(img_file)
                except:
                    pass

            return str(pdf_path)

        except Exception as e:
            print(f"PDF生成失败: {e}")
            return None

    async def batch_download(self, base_url: str, start_issue: int, end_issue: int) -> list:
        """批量下载多期报纸"""
        results = []

        for issue_num in range(start_issue, end_issue + 1):
            url = base_url.format(issue=issue_num)
            print(f"\n{'='*50}")
            print(f"下载第 {issue_num} 期...")
            print(f"{'='*50}")

            try:
                result = await self.download_issue(url)
                if result:
                    results.append(result)
                else:
                    print(f"第 {issue_num} 期下载失败")
            except Exception as e:
                print(f"第 {issue_num} 期出错: {e}")

            await asyncio.sleep(1)

        return results


def print_usage():
    print("""
人民日报图片版下载器
==================

用法:
    python downloader.py <URL> [输出文件名]
    python downloader.py --batch <URL模板> <起始期号> <结束期号>

示例:
    python downloader.py https://reader.jojokanbao.cn/rmhb/197201
    python downloader.py https://reader.jojokanbao.cn/rmrb/19761009
    python downloader.py --batch "https://reader.jojokanbao.cn/rmhb/1972{issue:02d}" 1 12

支持的报纸类型:
    rmhb - 人民画报
    rmrb - 人民日报
    ckxx - 参考消息
    hq   - 红旗
    sjzs - 世界知识
""")


async def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    if sys.argv[1] == "--batch":
        if len(sys.argv) < 5:
            print("用法: python downloader.py --batch <URL模板> <起始期号> <结束期号>")
            sys.exit(1)

        url_template = sys.argv[2]
        start = int(sys.argv[3])
        end = int(sys.argv[4])

        downloader = NewspaperDownloader()
        results = await downloader.batch_download(url_template, start, end)

        print(f"\n批量下载完成! 成功 {len(results)} 期")
        for r in results:
            print(f"  {r}")
        sys.exit(0)

    url = sys.argv[1]
    filename = sys.argv[2] if len(sys.argv) > 2 else None

    downloader = NewspaperDownloader()
    result = await downloader.download_issue(url, filename)

    if result:
        print(f"\n完成! 文件保存在: {result}")
    else:
        print("下载失败")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
