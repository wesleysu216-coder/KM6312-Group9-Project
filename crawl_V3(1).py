import random
import re
import time

import requests
import csv
from lxml import etree
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class JinJiangSpider():
    
    def __init__(self):
        self.cookies = {
            "Hm_lpvt_bc3b748c21fe5cf393d26c12b2c38d99":"1762953741",
            "Hm_lvt_bc3b748c21fe5cf393d26c12b2c38d99":"1760617963,1762918072",
            "JJEVER":"%7B%22isKindle%22%3A%22%22%2C%22shumeideviceId%22%3A%22WHJMrwNw1k/F4H3qBqOJpZajh1iQHdKIPe/hPUb3ovGkpEJ8tEpSs6F2qbnxEO6aGrvgxz9payhkWWHGUY4345TuRI1LWNB1MdCW1tldyDzmQI99+chXEiuJKYMhkKHDEYp5HxsF710xcYulduuw4jgCHPPxycwCneu8bpbMPuOQ/I2Qhiy6FgQIQ+DgAADG7/mcSd2NoEqnNtAKvckCXn9GTjt1evOwGT2YBWXqMYCmUH34bx8YNDA%3D%3D1487582755342%22%2C%22background%22%3A%22%22%2C%22font_size%22%3A%22%22%2C%22fenzhan%22%3A%22bq%22%2C%22lastCheckLoginTimePc%22%3A1762951601%2C%22sms_total%22%3A4%7D",
            "smidV2":"2025101620301910492cfc7438901112236b1d5dde0f8a00736f5bdf11316f0",
            "testcookie":"yes",
            "JJSESS":"%7B%22referer%22%3A%22%5C%2Fbook2%5C%2F6725433%22%2C%22clicktype%22%3A%22%22%2C%22register_info%22%3A%22288d2948016bd6e7de9145a646078132%22%2C%22userinfoprocesstoken%22%3A%22%22%2C%22sidkey%22%3A%22kyIAJd7oGsa82PZvcpmMYqE4DSCx6VUhe%22%7D",
            "bbsnicknameAndsign":"1%257E%2529%2524",
            "bbstoken":"ODA4Mjc1ODhfMF9iODY1NjRiNTRiYmNhNDcxZThiMmQ3NTU5NTg1ZTgxM18xX19fMQ%3D%3D",
            "token":"ODA4Mjc1ODh8NmRkNTQ4ODllOTdhZTI0Nzk4YjAwY2FlZDUwMmEzM2J8fHx8MjU5MjAwMHwxfHx85pmL5rGf55So5oi3fDB8bW9iaWxlfDF8MHx8",
            "timeOffset_o":"-804.39990234375",
            "HMACCOUNT":"EB120C3B13662327",
        }
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.jjwxc.net/bookbase.php',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3.1 Safari/605.1.15',
            'Connection': 'keep-alive',
            'Priority': 'u=0, i'
        }
        # self.base_url = 'https://www.jjwxc.net/bookbase.php'
        self.f = open('novel-1.csv', 'w', encoding='utf-8-sig', newline='')
        self.writer = csv.DictWriter(self.f, fieldnames=['作者', '名称', '类型', '进度', '字数', '发表时间', '作品视角',
                                                         '所属系列', '版权转化','签约状态','非v章节章均点击数','总书评数',
                                                         '当前被收藏数','文章积分','内容标签','评分','评价人数',
                                                         '五星比例','四星比例','三星比例','二星比例','一星比例'])
        self.writer.writeheader()
        self.count = 0

        # 初始化 Selenium WebDriver
        self.driver = None
        self.init_driver()
    
    def init_driver(self):
        """初始化 Chrome 驱动"""
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')  # 无头模式
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            # 防止检测
            options.add_experimental_option('excludeSwitches', ['enable-automation'])
            options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.set_page_load_timeout(30)  # 设置页面加载超时
            print("✅ Chrome 驱动初始化成功")
        except Exception as e:
            print(f"❌ Chrome 驱动初始化失败: {e}")
            raise
    
    def check_driver_alive(self):
        """检查 driver 是否还活着"""
        try:
            _ = self.driver.current_url
            return True
        except:
            return False
    
    def send_requests(self, page):
        params = {
            'fw0': '0',
            'fbsj2024': '2024',
            'fbsj2023': '2023',
            'fbsj2022': '2022',
            'novelbefavoritedcount0': '0',
            'yc0': '0',
            'xx0': '0',
            'mainview0': '0',
            'sd0': '0',
            'lx0': '0',
            'bq': '-1',
            'removebq': '',
            'sortType': '5',
            'page': f'{page}',
            'isfinish': '2',
            'collectiontypes': 'ors',
            'searchkeywords': '',
        }
        try:
            response = requests.get('https://www.jjwxc.net/bookbase.php', params=params, cookies=self.cookies,
                                    headers=self.headers, timeout=10)
            response.encoding = 'gb18030'
            response.raise_for_status()  # 检查HTTP错误
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            return None

    def parse_html(self, response, page):
        if not response:
            print("响应为空，跳过解析")
            return
            
        pbtime_list = re.findall("<td align='center'>(.*?)</td>", response)
        # idx = 0
        tree = etree.HTML(response)
        tr_list = tree.xpath('/html/body/table[1]/tbody/tr')
        for tr in tr_list[1:]:
            try:
                author = tr.xpath('./td[1]/a/text()')[0].strip()  # 作者
                title = tr.xpath('./td[2]/a/text()')[0].strip()  # 小说名称
                novel_type = tr.xpath('./td[3]/text()')[0].strip()  # 小说类型
                speed = tr.xpath('./td[4]/font/text()')[0].strip()  # 进度
                wordcount = tr.xpath('./td[5]/text()')[0].strip()  # 字数
                publish_time = str(tr.xpath('./td[7]/text()'))  # 发表时间
                novel_url = 'https://www.jjwxc.net/' + tr.xpath('./td[2]/a/@href')[0].strip()
                novel_id = novel_url.split('=')[1]
                # 解析详情页并得到扩展字段（包含 版权转化 字段）
                zuopinshijiao, suoshuxilie, banquanzhuanhua, qianyuezhuangtai, totalclick, reviewCount, collectedCount, scoreCount, neirongbiaoqian, pingfen, yipingfenrenshu, wuxing_baifenbi, sixing_baifenbi, sanxing_baifenbi, erxing_baifenbi, yixing_baifenbi = self.send_detail_request2(
                    novel_id, page)
                dic = {
                    '作者': author,
                    '名称': title,
                    '类型': novel_type,
                    '进度': speed,
                    '字数': wordcount,
                    '发表时间': publish_time,
                    '作品视角': zuopinshijiao,
                    '所属系列': suoshuxilie,
                    '版权转化': banquanzhuanhua,
                    '签约状态': qianyuezhuangtai,
                    '非v章节章均点击数': totalclick,
                    '总书评数': reviewCount,
                    '当前被收藏数': collectedCount,
                    # '营养液数': nutritionCount,
                    '文章积分': scoreCount,
                    '内容标签': neirongbiaoqian,
                    '评分': pingfen,
                    '评价人数': yipingfenrenshu,
                    '五星比例': wuxing_baifenbi,
                    '四星比例': sixing_baifenbi,
                    '三星比例': sanxing_baifenbi,
                    '二星比例': erxing_baifenbi,
                    '一星比例': yixing_baifenbi,
                }
                print(author, title)
                self.writer.writerow(dic)
                self.f.flush() 
            except Exception as e:
                print(e)

    def _init_driver(self):
        """初始化 Chrome WebDriver（无头模式）"""
        opts = Options()
        opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument(f"user-agent={self.headers['User-Agent']}")
        
        # 添加 cookies（可选，如果需要登录状态）
        driver = webdriver.Chrome(options=opts)
        driver.get('https://www.jjwxc.net/onebook.php?novelid=1')  # 先访问任何页面以设置 cookies
        for key, val in self.cookies.items():
            try:
                driver.add_cookie({'name': key, 'value': val})
            except Exception as e:
                print(f"添加 cookie {key} 失败: {e}")
        
        return driver

    def send_detail_request2(self, novel_id, page):
        """通过 Selenium 获取渲染后的 HTML"""
        url = f'https://www.jjwxc.net/onebook.php?novelid={novel_id}'
        
        print(f'正在通过 Selenium 爬取第{page}页第{self.count+1}条数据... (novelid={novel_id})')
        self.count += 1
        max_retries = 1
        for attempt in range(max_retries):
            try:
                # 检查 driver 是否还活着，如果不活着就重新初始化
                if not self.check_driver_alive():
                    print("⚠️  检测到 driver 会话失效，正在重新初始化...")
                    if self.driver:
                        try:
                            self.driver.quit()
                        except:
                            pass
                    self.init_driver()
                
                self.driver.get(url)
                
                # # 等待关键元素加载
                # WebDriverWait(self.driver, 10).until(
                #     EC.presence_of_element_located((By.ID, "novelreview_div"))
                # )
                
                time.sleep(1)
                
                html = self.driver.page_source
                tree_detail = etree.HTML(html)
                
                
                # 作品视角
                try:
                    zuopinshijiao = tree_detail.xpath('//ul[@name="printright"]/li[2]/text()')[1].strip() if tree_detail.xpath('//ul[@name="printright"]/li[2]/text()') else "未知"
                except:
                    zuopinshijiao = "未知"
                # 所属系列  
                try:
                    suoshuxilie = tree_detail.xpath('//ul[@name="printright"]/li[3]/span[2]/text()')[0].strip() if tree_detail.xpath('//ul[@name="printright"]/li[3]/span[2]/text()') else "无"
                except:
                    suoshuxilie = "无"

                # 版权转化
                # 提取"版权转化"一项中所有 img 的 title 属性，拼接为逗号分隔字符串
                try:
                    # 优先按包含"版权转化"文字的 li 节点查找
                    titles = tree_detail.xpath('//ul[@name="printright"]/li[contains(normalize-space(.),"版权转化")]//img/@title')
                    # 若没有找到，则退而求其次，查找该 ul 下所有带 title 的 img
                    if not titles:
                        titles = tree_detail.xpath('//ul[@name="printright"]//img[@title]/@title')
                    # 过滤空值并去重（保持出现顺序）
                    seen = set()
                    cleaned = []
                    for t in titles:
                        if not t:
                            continue
                        s = t.strip()
                        if s and s not in seen:
                            seen.add(s)
                            cleaned.append(s)
                    banquanzhuanhua = ",".join(cleaned) if cleaned else "未签约"
                except Exception:
                    banquanzhuanhua = "无匹配结果"
                    
                # 签约状态
                try:
                    # 找到“签约状态”所在的 li
                    li_node = tree_detail.xpath('//ul[@name="printright"]/li[contains(string(),"签约状态")]')

                    if li_node:
                        text = "".join(li_node[0].xpath('.//text()')).strip()

                        if "未签约" in text:
                            qianyuezhuangtai = "未签约"
                        else:
                            # 只要不是“未签约”，就是已签约（排除影视签约等属于版权转化）
                            qianyuezhuangtai = "已签约"
                    else:
                        qianyuezhuangtai = "未签约"

                except:
                    qianyuezhuangtai = "未签约"

                # 新增：提取"内容标签"
                try:
                    tag_nodes = tree_detail.xpath('//div[@class="smallreadbody"][contains(., "内容标签")]//span/a/text()')
                    cleaned_tags = []
                    seen = set()
                    for tag in tag_nodes:
                        if tag and tag.strip():
                            t = tag.strip()
                            if t not in seen:
                                seen.add(t)
                                cleaned_tags.append(t)
                    neirongbiaoqian = ",".join(cleaned_tags) if cleaned_tags else "无"
                except Exception as e:
                    print(f"内容标签提取失败: {e}")
                    neirongbiaoqian = "无"
                
                # 新增：提取"完结评分"相关数据
                try:
                    # 评分
                    pingfen_nodes = tree_detail.xpath('//div[@id="novelreview_div"]//div[contains(text(),"评分：")]/span[@class="coltext"]/text()')
                    pingfen = pingfen_nodes[0].strip() if pingfen_nodes else "0"
                    
                    # 已评分人数
                    yipingfenrenshu_nodes = tree_detail.xpath('//div[@id="novelreview_div"]//div[contains(text(),"已评分人数：")]/span[@class="coltext"]/text()')
                    yipingfenrenshu = yipingfenrenshu_nodes[0].strip() if yipingfenrenshu_nodes else "0"
                    
                    # 5星百分比
                    wuxing_nodes = tree_detail.xpath('//div[@class="novelreview_chart_col"][@data-score="5"]//div[@class="col_item"]/following-sibling::div/text()')
                    wuxing_baifenbi = wuxing_nodes[0].strip() if wuxing_nodes else "0%"
                    
                    # 4星百分比
                    sixing_nodes = tree_detail.xpath('//div[@class="novelreview_chart_col"][@data-score="4"]//div[@class="col_item"]/following-sibling::div/text()')
                    sixing_baifenbi = sixing_nodes[0].strip() if sixing_nodes else "0%"
                    
                    # 3星百分比
                    sanxing_nodes = tree_detail.xpath('//div[@class="novelreview_chart_col"][@data-score="3"]//div[@class="col_item"]/following-sibling::div/text()')
                    sanxing_baifenbi = sanxing_nodes[0].strip() if sanxing_nodes else "0%"
                    
                    # 2星百分比
                    erxing_nodes = tree_detail.xpath('//div[@class="novelreview_chart_col"][@data-score="2"]//div[@class="col_item"]/following-sibling::div/text()')
                    erxing_baifenbi = erxing_nodes[0].strip() if erxing_nodes else "0%"
                    
                    # 1星百分比
                    yixing_nodes = tree_detail.xpath('//div[@class="novelreview_chart_col"][@data-score="1"]//div[@class="col_item"]/following-sibling::div/text()')
                    yixing_baifenbi = yixing_nodes[0].strip() if yixing_nodes else "0%"
                    
                except Exception as e:
                    print(f"完结评分提取失败: {e}")
                    pingfen = "0"
                    yipingfenrenshu = "0"
                    wuxing_baifenbi = "0%"
                    sixing_baifenbi = "0%"
                    sanxing_baifenbi = "0%"
                    erxing_baifenbi = "0%"
                    yixing_baifenbi = "0%"
                
                # 从第二个 table 最后一行的 sptd 中提取五个数据：总书评数、被收藏数、营养液数、文章积分、非v章节章均点击数
                try:
                    # 非v章节章均点击数
                    totalclick = tree_detail.xpath('//table[2]/tbody/tr[last()]/td[@class="sptd"]/div/span[1]/text()')[0] if tree_detail.xpath('//table[2]/tbody/tr[last()]/td[@class="sptd"]/div/span[1]/text()') else "0"
                except:
                    totalclick = "0"
                    
                try:
                    # 总书评数
                    reviewCount = tree_detail.xpath('//span[@itemprop="reviewCount"]/text()')[0].strip() if tree_detail.xpath('//span[@itemprop="reviewCount"]/text()') else "0"
                except:
                    reviewCount = "0"
                    
                try:
                    # 当前被收藏数
                    collectedCount = tree_detail.xpath('//span[@itemprop="collectedCount"]/text()')[0].strip() if tree_detail.xpath('//span[@itemprop="collectedCount"]/text()') else "0"
                except:
                    collectedCount = "0"
                    
                # try:
                #     # 营养液数
                #     nutritionCount = tree_detail.xpath('//span[@itemprop="nutritionCount"]/text()')[0].strip() if tree_detail.xpath('//span[@itemprop="nutritionCount"]/text()') else "0"
                # except:
                #     nutritionCount = "0"
                
                try:
                    # 文章积分
                    scoreCount = tree_detail.xpath('//span[@itemprop="scoreCount"]/text()')[0].strip() if tree_detail.xpath('//span[@itemprop="scoreCount"]/text()') else "0"
                except:
                    scoreCount = "0"

                # 返回值中新增字段
                return zuopinshijiao, suoshuxilie, banquanzhuanhua, qianyuezhuangtai, totalclick, reviewCount, collectedCount, scoreCount, neirongbiaoqian, pingfen, yipingfenrenshu, wuxing_baifenbi, sixing_baifenbi, sanxing_baifenbi, erxing_baifenbi, yixing_baifenbi
            
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"⚠️  第 {attempt+1} 次尝试失败，正在重试... 错误: {e}")
                    time.sleep(2)
                else:
                    print(f"❌ 详情页请求失败 (novelid={novel_id}): {e}")
                    return "未知", "无", "未签约", "未知", "0", "0", "0", "0", "0", "无", "0", "0", "0%", "0%", "0%", "0%", "0%"

    def save_data(self):
        pass

    def close(self):
        """关闭 WebDriver"""
        if self.driver:
            self.driver.quit()

    def run(self):
        try:
            for i in range(1, 173):  # 爬取前172页数据
                print(f'正在爬取第{i}页数据...')
                response = self.send_requests(i)
                self.parse_html(response, i)
        finally:
            # 确保文件被正确关闭
            if hasattr(self, 'f')and self.f:
                self.f.flush()  # 最后再 flush 一次
                self.f.close()
                print("文件已关闭")


if __name__ == '__main__':
    JJ = JinJiangSpider()
    JJ.run()