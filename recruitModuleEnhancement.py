import os
import dhash
import jieba
import asyncio

from io import BytesIO
from PIL import Image
from jieba import posseg
from typing import List
from itertools import combinations
from amiyabot import PluginInstance
from amiyabot.network.download import download_async

from core import log, Message, Chain
from core.util import all_match, read_yaml
from core.resource.arknightsGameData import ArknightsGameData

try:
    from paddleocr import paddleocr
    from paddleocr import PaddleOCR

    # paddleocr.logging.disable()
    ocr = PaddleOCR(lang='ch')
    enabled = True
    log.info('PaddleOCR初始化完成')
except ModuleNotFoundError:
    log.info('未安装PaddleOCR')
    enabled = False

curr_dir = os.path.dirname(__file__)

recruit_config = read_yaml(f'{curr_dir}/recruit.yaml')
discern = recruit_config.autoDiscern

class Recruit:
    tags_list: List[str] = []

    @staticmethod
    async def init_tags_list():
        log.info('building operator tags keywords dict...')

        tags = ['资深', '高资', '高级资深']
        for name, item in ArknightsGameData.operators.items():
            for tag in item.tags:
                if tag not in tags:
                    tags.append(tag)

        with open(f'{curr_dir}/tags.txt', mode='w+', encoding='utf-8') as file:
            file.write('\n'.join([item + ' 500 n' for item in tags]))

        jieba.load_userdict(f'{curr_dir}/tags.txt')

        Recruit.tags_list = tags

    @classmethod
    async def action(cls, data: Message, text: str, ocr: bool = False):
        reply = Chain(data)

        if not text:
            if ocr:
                return reply.text('图片识别失败')
            return None

        words = posseg.lcut(text.replace('公招', ''))

        tags = []
        max_rarity = 5
        for item in words:
            if item.word in cls.tags_list:
                if item.word in ['资深', '资深干员'] and '资深干员' not in tags:
                    tags.append('资深干员')
                    continue
                if item.word in ['高资', '高级资深', '高级资深干员'] and '高级资深干员' not in tags:
                    tags.append('高级资深干员')
                    max_rarity = 6
                    continue
                if item.word not in tags:
                    tags.append(item.word)

        if tags:
            result = find_operator_tags_by_tags(tags, max_rarity=max_rarity)
            if result:
                operators = {}
                for item in result:
                    name = item['operator_name']
                    if name not in operators:
                        operators[name] = item
                    else:
                        operators[name]['operator_tags'] += item['operator_tags']

                groups = []

                for comb in [tags] if len(tags) == 1 else find_combinations(tags):
                    lst = []
                    max_r = 0
                    for name, item in operators.items():
                        rarity = item['operator_rarity']
                        if all_match(item['operator_tags'], comb):
                            if rarity == 6 and '高级资深干员' not in comb:
                                continue
                            if rarity >= 4 or rarity == 1:
                                if rarity > max_r:
                                    max_r = rarity
                                lst.append(item)
                            else:
                                break
                    else:
                        if lst:
                            groups.append({
                                'tags': comb,
                                'max_rarity': max_r,
                                'operators': lst
                            })

                if groups:
                    groups = sorted(groups, key=lambda n: (-len(n['tags']), -n['max_rarity']))
                    return reply.html(f'{curr_dir}/template/operatorRecruit.html', {'groups': groups, 'tags': tags})
                else:
                    return reply.text('博士，没有找到可以锁定稀有干员的组合')
            else:
                return reply.text('博士，无法查询到标签所拥有的稀有干员')

        if ocr:
            return reply.text('博士，没有在图内找到标签信息')

def find_operator_tags_by_tags(tags, max_rarity):
    res = []
    for name, item in ArknightsGameData.operators.items():
        if not item.is_recruit or item.rarity > max_rarity:
            continue
        for tag in item.tags:
            if tag in tags:
                res.append(
                    {
                        'operator_id': item.id,
                        'operator_name': name,
                        'operator_rarity': item.rarity,
                        'operator_tags': tag
                    }
                )

    return sorted(res, key=lambda n: -n['operator_rarity'])


def find_combinations(_list):
    result = []
    for i in range(3):
        for n in combinations(_list, i + 1):
            n = list(n)
            if n and not ('高级资深干员' in n and '资深干员' in n):
                result.append(n)
    result.reverse()
    return result

async def auto_discern(data: Message):
    if not enabled:
        return False
    for item in data.image:
        img = await download_async(item)
        if img:
            try:
                hash_value = dhash.dhash_int(Image.open(BytesIO(img)))
                diff = dhash.get_num_bits_different(hash_value, discern.templateHash)
            except OSError:
                return False

            if diff <= discern.maxDifferent:
                data.image = [img]
                return True,20
    return False


async def get_ocr_result(image):
    if enabled:
        result = ocr.ocr(image)
        log.info(f'{result}')
        str_ret = [text[1][0] for text in result[0]]
        log.info(f'{str_ret}')
        return ''.join(str_ret)
    return ''

async def recruit_module_enhancement_action1(data: Message):

    log.info('短路后的公招查询1')

    if data.image:
        # 直接 OCR 识别图片
        return await Recruit.action(data, await get_ocr_result(data.image[0]), ocr=True)
    else:
        # 先验证文本内容
        recruit = await Recruit.action(data, data.text_origin)
        if recruit:
            return recruit
        else:
            # 文本内容验证不出则询问截图

            wait = await data.wait(Chain(data, at=True).text('博士，请发送您的公招界面截图~'), force=True)

            if wait and wait.image:
                return await Recruit.action(wait, await get_ocr_result(wait.image[0]), ocr=True)
            else:
                return Chain(data, at=True).text('博士，您没有发送图片哦~')

async def recruit_module_enhancement_action2(data: Message):

    log.info('短路后的公招查询2')

    return await Recruit.action(data, await get_ocr_result(data.image[0]), ocr=True)
