import os
import zipfile
from xmindparser import xmind_to_dict

def extract_images_from_xmind(xmind_file, output_folder):
    """
    从 .xmind 文件中提取图片并保存到指定文件夹
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    xmind_base_name = os.path.splitext(os.path.basename(xmind_file))[0]
    name_map = {}
    counter = 1

    with zipfile.ZipFile(xmind_file, 'r') as z:
        for file in z.namelist():
            if file.startswith('resources/') and file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                
                # 生成新文件名
                ext = os.path.splitext(file)[1]
                new_name = f"{xmind_base_name}_{counter:03d}{ext}"
                counter += 1
                
                # 保存图片并记录映射
                image_path = os.path.join(output_folder, new_name)
                with open(image_path, 'wb') as img_file:
                    img_file.write(z.read(file))
                name_map[os.path.basename(file)] = new_name
    return name_map

def xmind_to_md(xmind_file, md_file, image_folder):
    """
    将 .xmind 文件转换为 .md 文件，并处理图片
    """
    # 提取图片
    name_map = extract_images_from_xmind(xmind_file, image_folder)

    # 读取 xmind 文件并转换为字典
    xmind_dict = xmind_to_dict(xmind_file)

    # 打开 md 文件准备写入
    with open(md_file, 'w', encoding='utf-8') as f:
        # 递归遍历 xmind 字典并生成 markdown 内容
        def parse_topic(topic, level, is_last_level):
            if 'title' in topic:
                if is_last_level or level > 6:
                    f.write(topic['title'] + '\n\n')  # 作为普通文本
                else:
                    f.write('#' * level + ' ' + topic['title'] + '\n')  # 其他级别作为标题
            if 'image' in topic:  # 如果有图片
                origin_image_name = os.path.basename(topic['image']['src'])
                new_image_name = name_map.get(origin_image_name)
                image_path = os.path.join('images', new_image_name)
                f.write(f'![]({image_path})\n\n')  # 插入图片
            if 'topics' in topic:
                is_last = False
                for subtopic in topic['topics']:
                    # 判断是否是最后一级
                    if not is_last:
                        is_last = not subtopic.get('topics')
                    else:
                        break
                for subtopic in topic['topics']:
                    parse_topic(subtopic, level + 1, is_last)

        # 开始解析 xmind 内容
        for sheet in xmind_dict:
            parse_topic(sheet['topic'], 1, False)  # 从第一级开始，初始不是最后一级

def convert_folder_xmind_to_md(folder_path):
    """
    将文件夹中的所有 .xmind 文件转换为 .md 文件
    """
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.xmind'):
                xmind_file_path = os.path.join(root, file)
                md_file_path = os.path.splitext(xmind_file_path)[0] + '.md'
                image_folder = os.path.join(root, 'images')  # 图片保存文件夹
                print(f'Converting {xmind_file_path} to {md_file_path}...')
                xmind_to_md(xmind_file_path, md_file_path, image_folder)

# 使用示例
folder_path = './' # 将当前文件夹下的所有xmind转为md
convert_folder_xmind_to_md(folder_path)