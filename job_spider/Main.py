from spider.ReSpider import JobRe
# from analysis.cloud import get_cloud

class Main:
    @staticmethod
    def run(key):

        print(f"开始爬取关键词：{key}")
        JobRe().crawl(key)
        print("爬取关键词：{key}数据完毕")

        # print("开始抽取关键词：{key}, 生成抽取结果, 并生成词云")
        # get_cloud(key)


if __name__ == "__main__":
    keys = ["大模型", "RAG", "Agent", "多模态", "LLM", 
            "AIGC", "NLP"]
    for key in keys:
        Main.run(key)
    # Main.run("RAG")

