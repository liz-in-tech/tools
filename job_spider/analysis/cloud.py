import pandas as pd
import wordcloud
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

from .key_word import get_skills
from .key_word import filt
from .key_word import get_filted_cnts
from os import sep
from datetime import datetime
from .llm_api import chat
from .split_jd import split_job_description

def get_cloud(job):
    date = "20250212"
    data_dir = date+sep
    print("get_cloud: ", job)
    # date = datetime.now().strftime('%Y%m%d')
    
    df = pd.read_csv(data_dir + job + date + "_res.csv", engine="python", encoding="utf_8_sig") # engine默认为c engine, 不支持文件名含有中文
    # words, cnts = get_skills(df)
    # filted_words = filt(words, ["n", "eng", "nz"])
    # filt_cnt = get_filted_cnts(filted_words, cnts)

    details = []
    for line in df["detail"]:
        details.append(split_job_description(line))

    prompt = """
你是一个招聘数据分析助手，任务是分析给定的Job Description（JD）列表，提取出与技能相关的关键词，并统计它们的出现频次。这些关键词应该是可以提升的技能点，且需要考虑不同JD中可能用不同词汇表达相同技能的情况（例如，“SFT”和“微调”应归为同一类，“llama”和“LLaMA”为同一类）。最终输出一个关键词及其频次的词典，其中key是关键词，value是频次，用于指导面试准备和学习方向。
注意，请给出最后分析的结果，不用告诉用户怎么做到的或者要怎么做到。

输入：
- JD列表：["JD1", "JD2", ..., "JDn"]，其中每个元素是一个字符串，表示一个Job Description。

输出：
- 一个频次递减的词典，格式如下：
  {
    "关键词1": 频次1,
    "关键词2": 频次2,
    ...
  }

补充要求：
1. 同义词处理：对于不同JD中表达相同技能的不同词汇，应归为同一类。
2. 技能分类：关键词应尽量聚焦于可提升的技能点，避免过于宽泛或不相关的词汇，例如“人工智能”，“自然语言处理”这就太宽泛了。
3. 频次统计：统计每个可提升关键词在所有JD中出现的总次数，只出现1次的就不用统计了。
4. 输出格式：关键词按频次从高到低排序，频次相同的按字母顺序排序，词典形式，且只输出这个词典，不要输出其他内容

示例输入：
["JD1: 需要熟悉LangChain,llamaindex和向量数据库。", "JD2: 要求掌握SFT和RAG。", "JD3: langchain和llamaindex。"]

示例输出：
{
  "langchain": 2,
  "llamaindex": 2,
  "向量数据库": 1,
  "SFT": 1,
  "RAG": 1
}

待处理的JD列表：
"""
    prompt = prompt + str(details)
    print(f'Prompt:{prompt}')
    res = chat("qwen/qwen-2-7b-instruct:free", prompt, "")
    print(res)

    with open(data_dir + job + date + "_key_skills.txt", "w", encoding="utf-8") as f:
        for k, v in filt_cnt.items():
            f.write(k+"="+str(v)+"\n")

    apple_mask = np.array(Image.open(data_dir+"apple2.jpg"))

    wc = wordcloud.WordCloud(font_path=data_dir+"NotoSansCJKsc-DemiLight.otf",
                             background_color="white",  # 背景颜色
                             max_words=400,  # 词云显示的最大词数
                             mask=apple_mask,  # 设置背景图片
                             max_font_size=200,  # 字体最大值
                             min_font_size=40,
                             random_state=42,
                             margin=1
                             )
    image_colors = wordcloud.ImageColorGenerator(apple_mask)
    if len(filt_cnt):
        wc.generate_from_frequencies(filt_cnt)
        # show
        plt.figure(figsize=[20, 20])
        plt.tight_layout(pad=0)
        plt.imshow(wc.recolor(color_func=image_colors), interpolation="bilinear")
        plt.axis("off")

        plt.savefig(data_dir+job+ date +"_cloud.png")
        print("生成词云完毕")