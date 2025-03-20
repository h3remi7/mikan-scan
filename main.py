import re
import os
import json
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import requests
from bs4 import XMLParsedAsHTMLWarning
import warnings

# 忽略XML解析警告
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

def extract_anime_info(html_content, rss_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    rss_soup = BeautifulSoup(rss_content, 'html.parser')  # 使用html.parser替代xml
    
    anime_info = {}
    
    # Extract anime name from RSS page
    rss_title = rss_soup.find('title')
    if rss_title:
        # 标题格式为 "Mikan Project - 番剧名"，我们需要提取番剧名部分
        title_text = rss_title.text.strip()
        anime_name = title_text.split(' - ')[-1] if ' - ' in title_text else title_text
        anime_info["name"] = anime_name
    
    # Extract anime ID from subscribe button
    subscribe_button = soup.find('button', class_='btn logmod-submit js-subscribe_bangumi_page')
    if subscribe_button and subscribe_button.get('data-bangumiid'):
        anime_info["id"] = int(subscribe_button['data-bangumiid'])
    else:
        # Fallback: try to extract from the current page URL
        anime_id_match = re.search(r'/Bangumi/(\d+)', str(soup))
        if anime_id_match:
            anime_info["id"] = int(anime_id_match.group(1))
    
    # Extract subtitle groups
    sub_groups = []
    # 尝试多种可能的选择器
    group_links = soup.find_all('a', class_=lambda x: x and ('subgroup-name' in x or 'subgroup-' in x))
    
    for group_link in group_links:
        # 尝试从class属性中提取group_id
        group_id_match = re.search(r'subgroup-(\d+)', ','.join(group_link.get('class', [''])))
        if not group_id_match:
            # 尝试从href属性中提取
            group_id_match = re.search(r'/PublishGroup/(\d+)', group_link.get('href', ''))
        
        if group_id_match:
            group_id = int(group_id_match.group(1))
            group_name = group_link.text.strip()
            if group_name and {"group_name": group_name, "group_id": group_id} not in sub_groups:
                sub_groups.append({"group_name": group_name, "group_id": group_id})
    
    anime_info["sub_groups"] = sub_groups
    
    return anime_info

def main():
    # 设置目标URL
    base_url = "https://mikanani.me/Home/Bangumi/3463"  # 这里使用示例URL，实际使用时可以根据需要修改
    
    try:
        # 发送HTTP请求获取页面内容
        response = requests.get(base_url)
        response.raise_for_status()  # 检查请求是否成功
        
        # 获取HTML内容
        html_content = response.text
        
        # 从页面中提取番剧ID
        soup = BeautifulSoup(html_content, 'html.parser')
        subscribe_button = soup.find('button', class_='btn logmod-submit js-subscribe_bangumi_page')
        if not subscribe_button or not subscribe_button.get('data-bangumiid'):
            raise Exception("无法获取番剧ID")
        
        bangumi_id = subscribe_button['data-bangumiid']
        
        # 获取RSS页面内容
        rss_url = f"https://mikanani.me/RSS/Bangumi?bangumiId={bangumi_id}"
        rss_response = requests.get(rss_url)
        rss_response.raise_for_status()
        rss_content = rss_response.text
        
        anime_info = extract_anime_info(html_content, rss_content)
        # 获取每个字幕组的剧集列表
        sub_groups = anime_info["sub_groups"]
        # 获取每个字幕组的剧集列表
        for idx, group in enumerate(sub_groups):
            print(group)
            all_episodes = []
            episode_table_url = f"https://mikanani.me/Home/ExpandEpisodeTable?bangumiId={bangumi_id}&subtitleGroupId={group['group_id']}&take=100"
            episode_response = requests.get(episode_table_url)
            episode_response.raise_for_status()
            episode_content = episode_response.text
            
            # 解析剧集列表
            episode_soup = BeautifulSoup(episode_content, 'html.parser')
            episode_rows = episode_soup.find_all('tr')[1:]  # Skip header row
            
            for row in episode_rows:
                cols = row.find_all('td')
                if len(cols) >= 4:
                    episode_link = cols[0].find('a')
                    if episode_link:
                        episode_info = {
                            "title": episode_link.text.strip(),
                            "size": cols[1].text.strip(),
                            "update_time": cols[2].text.strip(),
                            "magnet_link": cols[0].find_all('a')[1]['data-clipboard-text'] if len(cols[0].find_all('a')) > 1 else None,
                            "subtitle_group": group['group_name']
                        }
                        all_episodes.append(episode_info)
        
            # add magnet link to anime_info subtitle_group
            anime_info["sub_groups"][idx]["episodes"] = all_episodes
        # Create the final JSON structure
        # Create output directory if it doesn't exist
        output_dir = os.path.join(os.getcwd(), "Generated", "Products")
        os.makedirs(output_dir, exist_ok=True)
        
        # Write to JSON file
        output_file = os.path.join(output_dir, "anime_info.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(anime_info, f, ensure_ascii=False, indent=2)
        
        print(f"JSON file saved to: {os.path.abspath(output_file)}")
        
        # Also print the JSON to console
        print("\nJSON Output:")
        print(json.dumps(anime_info, ensure_ascii=False, indent=2))
        
    except requests.RequestException as e:
        print(f"获取页面内容时发生错误: {e}")
    except Exception as e:
        print(f"处理过程中发生错误: {e}")

if __name__ == "__main__":
    main()
