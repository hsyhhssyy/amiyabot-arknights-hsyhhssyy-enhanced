import re
import time
import datetime
import json
import copy
import random
import os
import importlib
import inspect
import pathlib
import jieba
import aiohttp
import requests
import asyncio

from io import BytesIO
from amiyabot import PluginInstance
from amiyabot.util import temp_sys_path, extract_zip, argv
from amiyabot.network.download import download_async
from core.util import read_yaml, any_match, remove_punctuation
from core import log, Message, Chain, tasks_control
from core.database.user import User, UserInfo
from core.database.bot import OperatorConfig
from core.resource.arknightsGameData import ArknightsGameData, ArknightsGameDataResource, Operator

curr_dir = os.path.dirname(__file__)

stage_drop = {}

def download_sync(url: str):
    try:
        default_headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) '
            'AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1'
            }
        stream = requests.get(url, headers=default_headers, stream=True)
        
        file_size = 0
        if 'content-length' in stream.headers:
            file_size = int(stream.headers['content-length'])

        container = BytesIO()

        if stream.status_code == 200:
            iter_content = stream.iter_content(chunk_size=1024)
            for chunk in iter_content:
                if chunk:
                    container.write(chunk)

            content = container.getvalue()

            return content

    except requests.exceptions.ConnectionError:
        pass
    except Exception as e:
        log.error(e, desc='download error:')

def init_stage_drop(json_data):
    stage_drop_list = {}
    for item in json_data['matrix']:
        stage_id = item['stageId']
        if not stage_drop_list.__contains__(stage_id):
            stage_drop_list[stage_id] = { }
        
        stage_drop = stage_drop_list[stage_id]
        
        item_id = item['itemId']
        
        if not stage_drop.__contains__(item_id):
            stage_drop[item_id] = {
                'quantity':0,
                'times':0
            }
        
        stage_drop[item_id]['quantity']+= item['quantity']
        stage_drop[item_id]['times']+= item['times']

    return stage_drop_list

async def download_penguin_stats_matrix():  
    
    global stage_drop

    front_page_address = 'https://penguin-stats.io/PenguinStats/api/v2/result/matrix'
    # front_page_address = 'https://www.google.com'
    resource_file = f'{curr_dir}/../../resource/penguin-stats-CN-all.json'

    res = await download_async(front_page_address) 
    if res:
        with open(resource_file, mode='wb+') as src:
            src.write(res)
        log.info('成功从企鹅物流获取了数据...')
    else:
        log.info('无法从企鹅物流获取数据，使用备份数据中，稍后自动重试。')

    with open(resource_file,
                mode='r',
                encoding='utf-8') as src:
        json_data = json.load(src)

    log.info('initialize init_penguin_stats_drop_rate...')
    stage_drop = init_stage_drop(json_data)

@tasks_control.timed_task(each=12000)
async def _():
    await download_penguin_stats_matrix()

async def stage_model_enhancement_action(data: Message):

    log.info('短路后的关卡查询')

    words = jieba.lcut(
        remove_punctuation(data.text_initial, ['-']).upper().replace(' ', '')
    )

    level = ''
    level_str = ''
    if any_match(data.text, ['突袭']):
        level = '_hard'
        level_str = '（突袭）'
    if any_match(data.text, ['简单', '剧情']):
        level = '_easy'
        level_str = '（剧情）'
    if any_match(data.text, ['困难', '磨难']):
        level = '_tough'
        level_str = '（磨难）'

    stage_id = None
    stages_map = ArknightsGameData.stages_map

    for item in words:
        stage_key = item + level
        if stage_key in stages_map:
            stage_id = stages_map[stage_key]

    if stage_id:
        stage_data = ArknightsGameData.stages[stage_id]

        if stage_id in stage_drop.keys():
            penguin_data = stage_drop[stage_id]
        else:
            penguin_data = {}

        res = {
            **stage_data,
            'name': stage_data['name'] + level_str
        }


        for material in res["stageDropInfo"]["displayDetailRewards"]:
            if material['id'] in penguin_data:
                item_drop_data = penguin_data[material['id']]
                drop_rate = round( 100 * item_drop_data['quantity'] / item_drop_data['times'] , 2)
                material['rate'] = f'{drop_rate}%'

        # log.info(f'{res}')

        return Chain(data).html(f'{curr_dir}/template/stage.html', res)
    else:
        return Chain(data).text('抱歉博士，没有查询到相关地图信息')