import abc
import requests
from os import sep
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import requests
from bs4 import BeautifulSoup
import os
import pandas as pd


# 获取代理 IP 的函数
def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").json()

# 删除无效代理 IP 的函数
def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))

class Spider():
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.row_title = ['title', 'salary', 'region', 'degree', 'exper', 'company', 'stage', 'scale', 'industry', 'detail']
        self.jobs_data = []
        self.count = 0

    """
        爬虫入口
    """
    def crawl(self, key):
        print("crawl: ", key)
        # 查北京和杭州2个城市
        url1 = "https://www.zhipin.com/web/geek/job?query="+key+"&city=101010100&jobType=1901" # 北京
        # url2 = "https://www.zhipin.com/web/geek/job?query="+key+"&city=101210100&jobType=1901" # 杭州
        
        self.key = key
        date = datetime.now().strftime('%Y%m%d')
        file_path0 = "data" + sep + self.key + date + "_res0.csv"
        file_path = "data" + sep + self.key + date + "_res.csv"
        # Check if the file exists
        if not os.path.exists(file_path0):
            self.request_job_list(url1)
            self.save()
        if not self.jobs_data:
            df = pd.read_csv(file_path0, encoding='utf_8_sig')
            self.jobs_data = df.to_dict('records')
        if not os.path.exists(file_path):
            self.request_job_details()
            self.save1()

    
    """
        获取并解析职位信息
    """
    def request_job_list(self, url):
        try:
            # headers = get_headers()
            # reponse = requests.get(url, headers=headers)
            # if reponse.status_code != 200: return
            # self.parse_job_list(reponse.text)
            # 配置 Chrome 无头模式（可选）
            chrome_options = Options()
            # chrome_options.add_argument("--headless")  # 无头模式
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            # 获取代理 IP
            proxy = get_proxy().get("proxy")
            print("使用的代理 IP:", proxy)

            # 指定chromedriver路径（确保已经下载并配置好chromedriver）
            driver = webdriver.Chrome(options=chrome_options)

            # 设置代理,这个必须在driver定义之后
            chrome_options.add_argument(f'--proxy-server=http://{proxy}')

            driver.get(url)

            # 设置最大等待时间和间隔时间
            max_wait_time = 60  # 最大等待时间为60秒
            interval = 5  # 每5秒检查一次

            # 初始化等待时间
            elapsed_time = 0

            # 循环检查元素是否存在
            while elapsed_time < max_wait_time:
                try:
                    # 使用 CSS 选择器查找 JD 内容
                    jd_element = driver.find_element(By.CSS_SELECTOR, ".job-list-box")
                    break  # 找到元素，跳出循环
                except:
                    time.sleep(interval)  # 等待一段时间
                    elapsed_time += interval  # 增加已等待时间

            if elapsed_time >= max_wait_time:
                print("超时未找到，跳过此次循环")
                return  # 超时未找到元素，结束此次循环

            # 使用 CSS 选择器查找 JD 内容
            # jd_element = driver.find_element(By.CSS_SELECTOR, ".job-list-box")

            # Get the HTML content from the element
            html_content = jd_element.get_attribute('innerHTML')

            # Parse the HTML content with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')

            # Find all job listings
            job_listings = soup.find_all('li', class_='job-card-wrapper')
  
            # Iterate over each job listing
            for job in job_listings:
                try:
                    # Extract the required information
                    title = job.find('span', class_='job-name').text.strip()
                    salary = job.find('span', class_='salary').text.strip()
                    region = job.find('span', class_='job-area').text.strip()
                    degree = job.find('ul', class_='tag-list').find_all('li')[1].text.strip()
                    exper = job.find('ul', class_='tag-list').find_all('li')[0].text.strip()
                    company = job.find('h3', class_='company-name').text.strip()
                    stage = job.find('ul', class_='company-tag-list').find_all('li')[1].text.strip()
                    scale = job.find('ul', class_='company-tag-list').find_all('li')[2].text.strip()
                    industry = job.find('ul', class_='company-tag-list').find_all('li')[0].text.strip()
                    detail_url = job.find('a', class_='job-card-left')['href']

                    # Append the job data to the list
                    self.jobs_data.append({
                        'title': title,
                        'salary': salary,
                        'region': region,
                        'degree': degree,
                        'exper': exper,
                        'company': company,
                        'stage': stage,
                        'scale': scale,
                        'industry': industry,
                        'detail': detail_url
                    })
                except Exception as e:
                    print(f'循环中错误：{e}')
                    continue
            # 关闭浏览器
            driver.quit()
        except Exception as e:
            print('request_job_list error : {}'.format(e))

    """
        解析职位URL
    """
    @abc.abstractmethod
    def parse_job_list(self, text):
        pass

    """
        请求职位详细页面
    """
    def request_job_details(self):
        try:
            # print("解析到的子url: ", url)
            # headers = get_headers()
            # response = requests.get(url, headers=headers)
            # if response.status_code != 200: return
            # return self.parse_job_details(response.text)
            # 配置 Chrome 无头模式（可选）
            chrome_options = Options()
            # chrome_options.add_argument("--headless")  # 无头模式
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")

            # 指定chromedriver路径（确保已经下载并配置好chromedriver）
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(50)  # 设置页面加载超时时间为30秒
            
            for job in self.jobs_data:
                try:
                    # 获取代理 IP
                    proxy = get_proxy().get("proxy")

                    # 设置代理,这个必须在driver定义之后
                    chrome_options.add_argument(f'--proxy-server=http://{proxy}')

                    url = "https://www.zhipin.com" + job["detail"]

                    print(f"使用的代理 IP:{proxy}, 请求的URL:{url}")
                    driver.get(url)

                    # 设置最大等待时间和间隔时间
                    max_wait_time = 60  # 最大等待时间为60秒
                    interval = 5  # 每5秒检查一次

                    # 初始化等待时间
                    elapsed_time = 0

                    # 循环检查元素是否存在
                    while elapsed_time < max_wait_time:
                        try:
                            # 使用 CSS 选择器查找 JD 内容
                            jd_element = driver.find_element(By.CSS_SELECTOR, ".job-sec-text")
                            break  # 找到元素，跳出循环
                        except:
                            time.sleep(interval)  # 等待一段时间
                            elapsed_time += interval  # 增加已等待时间

                    if elapsed_time >= max_wait_time:
                        print("超时未找到，跳过此次循环")
                        continue  # 超时未找到元素，结束此次循环

                    # 使用 CSS 选择器查找 JD 内容
                    # jd_element = driver.find_element(By.CSS_SELECTOR, ".job-sec-text")
                    jd_text = jd_element.text.strip()
                    job["detail"] = jd_text
                except Exception as e:
                    print('详情循环内异常 : {}'.format(e))
            # 关闭浏览器
            driver.quit()
        except Exception as e:
            # raise e
            print('向职位详细界面发起请求错误 : {}'.format(e))
    

    """
        解析职位详细页面
    """
    @abc.abstractmethod
    def parse_job_details(self, text):
        pass

    def append(self, title, salary, region, degree, exper, company, stage, scale, industry, detail):
        self.job_data.append([title, salary, region, degree, exper, company, stage, scale, industry, detail])


    def data_clear(self):
        self.job_data = []

    def extract(self, data):
        return data[0] if len(data) > 0 else ""


    def get_data(self):
        return self.job_data


    def save(self):
        titles = []
        salarys = []
        regions = []
        degrees = []
        expers = []
        companys = []
        stages = []
        scales = []
        industrys = []
        details = []
        for line in self.jobs_data:
            titles.append(line['title'])
            salarys.append(line['salary'])
            regions.append(line['region'])
            degrees.append(line['degree'])
            expers.append(line['exper'])
            companys.append(line['company'])
            stages.append(line['stage'])
            scales.append(line['scale'])
            industrys.append(line['industry'])
            details.append(line['detail'])

        df = pd.DataFrame()
        df["title"] = titles
        df['salary'] = salarys
        df["region"] = regions
        df["degree"] = degrees
        df["exper"] = expers
        df["company"] = companys
        df["stage"] = stages
        df["scale"] = scales
        df["industry"] = industrys
        df["detail"] = details

        date = datetime.now().strftime('%Y%m%d')
        ensure_directory(date)
        df.to_csv(date+sep+self.key+date+"_res0.csv", encoding='utf_8_sig', index=False)


    def save1(self):
        titles = []
        salarys = []
        regions = []
        degrees = []
        expers = []
        companys = []
        stages = []
        scales = []
        industrys = []
        details = []
        for line in self.jobs_data:
            titles.append(line['title'])
            salarys.append(line['salary'])
            regions.append(line['region'])
            degrees.append(line['degree'])
            expers.append(line['exper'])
            companys.append(line['company'])
            stages.append(line['stage'])
            scales.append(line['scale'])
            industrys.append(line['industry'])
            details.append(line['detail'].replace('\n', ' '))

        df = pd.DataFrame()
        df["title"] = titles
        df['salary'] = salarys
        df["region"] = regions
        df["degree"] = degrees
        df["exper"] = expers
        df["company"] = companys
        df["stage"] = stages
        df["scale"] = scales
        df["industry"] = industrys
        df["detail"] = details

        date = datetime.now().strftime('%Y%m%d')
        ensure_directory(date)
        df.to_csv(date+sep+self.key+date+"_res.csv", encoding='utf_8_sig', index=False)




def ensure_directory(path):
    """检查路径是否存在，不存在则创建"""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"目录 {path} 已创建。")
    else:
        print(f"目录 {path} 已存在。")
