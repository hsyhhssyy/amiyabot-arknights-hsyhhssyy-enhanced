import asyncio
import os

from amiyabot import PluginInstance
from core import log, Message, Chain

from .stageModelEnhancement import download_penguin_stats_matrix,stage_model_enhancement_action
from .recruitModuleEnhancement import Recruit,auto_discern,recruit_module_enhancement_action1,recruit_module_enhancement_action2

curr_dir = os.path.dirname(__file__)

class EnhancedOperatorPluginInstance(PluginInstance):
    def install(self):
        asyncio.create_task(download_penguin_stats_matrix())
        asyncio.create_task(Recruit.init_tags_list())

bot = EnhancedOperatorPluginInstance(
    name='明日方舟增强查询',
    version='1.0',
    plugin_id='amiyabot-arknights-hsyhhssyy-enhanced',
    plugin_type='',
    description='增强兔兔的查询功能，让他可以执行更多操作',
    document=f'{curr_dir}/README.md'
)


#拦截关卡查询功能，提供更高的level来短路到这里，然后递交回
@bot.on_message(keywords=['地图', '关卡'], allow_direct=True, level=10)
async def _(data: Message):
    return await stage_model_enhancement_action(data)
 

@bot.on_message(keywords=['公招', '公开招募'], allow_direct=True, level=20)
async def _(data: Message):
    return await recruit_module_enhancement_action1(data)

@bot.on_message(verify=auto_discern, check_prefix=False, allow_direct=True)
async def _(data: Message):
    return await recruit_module_enhancement_action2(data)