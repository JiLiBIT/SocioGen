import re
def read_interview_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        # 读取整个文件内容
        text = file.read()

        # 根据空行分割段落
        paragraphs = text.split('\n\n')  # 假设段落之间是由空行分隔的

        # 删除前三段
        remaining_paragraphs = paragraphs[2:]

        # 将剩余的段落重新合并为一个字符串
        new_text = "\n\n".join(remaining_paragraphs)

    # 返回处理后的内容，不保存到文件
    return new_text

def read_video_caption_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        # 读取整个文件内容
        text = file.read()

    return text

def remove_think_part(text):
    parts = text.split("think>\n")
    if len(parts) > 2:
        return parts[2].strip()

def get_theme(number_str):
    theme_mapping = {
        range(1, 6): "个人与社会",
        range(6, 11): "积极与消极",
        range(11, 16): "理性与感性",
    }
    
    for num_range, theme in theme_mapping.items():
        if int(number_str) in num_range:
            return theme
    return "未知主题"  # 处理超出范围的情况

def get_theme_description(number_str):
    theme_mapping = {
        range(1, 6): "个人与社会：喜欢与个人、微观个体的生活、感悟、经历、得失、福祉有关的内容，还是与宏观社会发展、法律、经济、和广泛的大众的公共利益和发展有关的内容。",
        # range(6, 11): "积极与消极：倾向乐观积极还是悲观消极",
        # range(11, 16): "感性与理性：喜欢丰富的情感还是严谨的分析", 
        range(6, 11): "积极与消极：在描述某一事件时，倾向使用乐观、积极、正面的内容，还是较为悲观、消极的内容。",
        range(11, 16): "理性与感性：在描述一件事时，倾向偏向理性、严肃、严谨的解释、播报、分析，还是倾向情感丰富、叙事性与故事性强、感动人心的内容。但是，过于感性的人在看到有强烈情感唤醒的事件或内容时，也可能因为其可能会造成强烈情感共鸣或波动而产生对这类内容的回避。反之，理性的人也可能会因为个人经历中的独特部分而对某些话题和事件产生情感和共鸣。", 
    }
    
    for num_range, theme in theme_mapping.items():
        if int(number_str) in num_range:
            return theme
    return "未知主题"  # 处理超出范围的情况



def simplify_classification_task(classification_number, answer):
    if classification_number == 2:
        # 替换类似 "非常不同意"、"不太不同意"、"有点不同意" 为 "不同意"
        answer = re.sub(r"(总是|非常|比较|有点|大多数情况下是|)不", "不", answer)
        # 替换类似 "非常同意"、"有点同意" 为 "同意"
        answer = re.sub(r"(总是|非常|比较|不太|有点|稍有|大多数情况下是)", "", answer)
        return answer
    else:
        raise NotImplementedError("Only classification_number == 2 is implemented")