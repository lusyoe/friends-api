#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
友链页面抓取器
用于获取友链页面中的友链信息，包括标题、图标和描述
通过HTML解析方式获取内容
"""

import requests
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

class LinksScraper:
    def __init__(self, url: str):
        """
        初始化友链抓取器
        
        Args:
            url: 友链页面URL
        """
        self.url = url
        self.session = requests.Session()
        # 设置请求头，模拟浏览器访问
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def check_rss_url(self, base_url: str) -> Optional[str]:
        """检查RSS URL是否可用"""
        if not base_url:
            return None
        
        # 常见的RSS路径
        rss_paths = [
            '/rss',
            '/rss.xml',
            '/rss2.xml',
            '/rss/feed.xml',
            '/feed',
            '/atom.xml',
            '/feed.xml',
            '/rss/atom.xml'
        ]
        
        for path in rss_paths:
            try:
                rss_url = urljoin(base_url, path)
                response = self.session.head(rss_url, timeout=10, allow_redirects=True)
                
                # 检查状态码是否为200
                if response.status_code == 200:
                    print(f"  ✓ 找到RSS: {rss_url}")
                    return rss_url
                    
            except Exception as e:
                # 静默处理错误，继续尝试下一个路径
                continue
        
        print(f"  ✗ 未找到RSS: {base_url}")
        return None
    
    def get_page_content(self) -> Dict:
        """获取页面内容"""
        if not self.url:
            raise ValueError("未提供页面URL")
        
        # 获取页面HTML
        response = self.session.get(self.url)
        if response.status_code != 200:
            raise Exception(f"无法访问页面: {response.status_code}")
        
        # 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 尝试提取页面信息
        page_info = {
            "title": soup.title.string if soup.title else "Unknown",
            "url": self.url
        }
        
        return page_info
    
    def extract_links_info(self) -> List[Dict]:
        """提取友链信息"""
        # 获取页面HTML
        response = self.session.get(self.url)
        if response.status_code != 200:
            raise Exception(f"无法访问页面: {response.status_code}")
        
        # 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = []
        
        # 查找所有notion-collection-card元素
        cards = soup.find_all('a', class_='notion-collection-card')
        
        for card in cards:
            link_info = self.parse_link_card(card)
            if link_info:
                links.append(link_info)
        
        return links
    
    def parse_link_card(self, card) -> Optional[Dict]:
        """解析友链卡片"""
        try:
            # 提取标题文本 (notion-page-title-text)
            title_element = card.find('span', class_='notion-page-title-text')
            title = title_element.get_text(strip=True) if title_element else ""
            
            # 提取图标URL (notion-page-title-icon)
            icon_element = card.find('img', class_='notion-page-title-icon')
            icon_url = icon_element.get('src', '') if icon_element else ""
            
            # 提取描述文本 (notion-property-text)
            description = ""
            text_properties = card.find_all('span', class_='notion-property notion-property-text')
            
            for prop in text_properties:
                # 跳过包含form的property（通常是URL）
                if prop.find('form'):
                    continue
                text = prop.get_text(strip=True)
                if text and not text.startswith('http'):
                    description = text
                    break
            
            # 提取URL（如果有的话）
            url = ""
            form_element = card.find('form')
            if form_element:
                input_element = form_element.find('input', class_='nested-form-link')
                if input_element:
                    url = input_element.get('value', '')
            
            # 提取创建时间
            created_time = self.extract_created_time(card)
            
            # 检查RSS URL
            rss_url = None
            if url:
                print(f"检查 {title} 的RSS...")
                rss_url = self.check_rss_url(url)
            
            if title:  # 只要有标题就认为是有效的友链
                return {
                    "name": title,
                    "logo": icon_url,
                    "description": description,
                    "url": url,
                    "rss_url": rss_url,
                    "created_time": created_time
                }
        
        except Exception as e:
            print(f"解析卡片时出错: {str(e)}")
        
        return None
    
    def extract_created_time(self, card) -> str:
        """从卡片中提取创建时间"""
        try:
            # 尝试从卡片的data属性中提取时间
            # Notion卡片通常会有时间相关的属性
            time_attributes = [
                'data-created-time',
                'data-last-edited-time',
                'data-block-id'
            ]
            
            for attr in time_attributes:
                time_value = card.get(attr)
                if time_value:
                    # 如果是时间戳格式，尝试转换
                    try:
                        # 假设是ISO格式的时间戳
                        if 'T' in time_value and 'Z' in time_value:
                            return time_value
                        # 如果是数字时间戳
                        elif time_value.isdigit():
                            timestamp = int(time_value) / 1000  # 转换为秒
                            return datetime.fromtimestamp(timestamp).isoformat()
                    except:
                        pass
            
            # 尝试从页面内容中查找时间信息
            time_selectors = [
                '.notion-property[data-property-type="date"]',
                '.notion-property[data-property-type="created_time"]',
                '.notion-property[data-property-type="last_edited_time"]'
            ]
            
            for selector in time_selectors:
                time_element = card.select_one(selector)
                if time_element:
                    time_text = time_element.get_text(strip=True)
                    if time_text:
                        return time_text
            
            # 如果都找不到，返回当前时间
            return datetime.now().isoformat()
            
        except Exception as e:
            print(f"提取创建时间时出错: {str(e)}")
            return datetime.now().isoformat()
    
    def scrape_links(self) -> List[Dict]:
        """抓取友链信息"""
        print("开始抓取友链页面...")
        
        try:
            print(f"正在抓取页面: {self.url}")
            page_content = self.get_page_content()
            print(f"页面标题: {page_content.get('title', 'Unknown')}")
            
            # 提取友链信息
            links = self.extract_links_info()
            print(f"找到 {len(links)} 个友链")
            
            return links
            
        except Exception as e:
            print(f"抓取失败: {str(e)}")
            return []

def save_to_json(links: List[Dict], filename: str = "links.json"):
    """保存友链信息到JSON文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(links, f, ensure_ascii=False, indent=2)
    print(f"友链信息已保存到 {filename}")

def save_to_csv(links: List[Dict], filename: str = "links.csv"):
    """保存友链信息到CSV文件"""
    import csv
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'Logo', 'Description', 'URL', 'RSS URL', 'Created Time'])
        
        for link in links:
            writer.writerow([
                link.get('name', ''),
                link.get('logo', ''),
                link.get('description', ''),
                link.get('url', ''),
                link.get('rss_url', ''),
                link.get('created_time', '')
            ])
    print(f"友链信息已保存到 {filename}")

def main():
    """主函数"""
    # 从环境变量获取配置
    url = os.getenv("LINKS_URL")
    
    if not url:
        print("请设置环境变量:")
        print("export LINKS_URL='https://blog.lusyoe.com/links'")
        print("\n或者直接在代码中设置:")
        print("url = 'https://blog.lusyoe.com/links'")
        return
    
    # 创建抓取器
    scraper = LinksScraper(url)
    
    # 抓取友链信息
    links = scraper.scrape_links()
    
    if links:
        print("\n找到的友链信息:")
        for i, link in enumerate(links, 1):
            print(f"\n{i}. {link.get('name', 'Unknown')}")
            print(f"   图标: {link.get('logo', 'N/A')}")
            print(f"   描述: {link.get('description', 'N/A')}")
            print(f"   URL: {link.get('url', 'N/A')}")
            print(f"   RSS: {link.get('rss_url', 'N/A')}")
        
        # 保存到文件
        save_to_json(links)
        save_to_csv(links)
    else:
        print("未找到友链信息")

if __name__ == "__main__":
    main() 