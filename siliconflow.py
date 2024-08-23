from io import BytesIO
import requests
import plugins
import httpx
from plugins import *
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger

BASE_URL = "https://api.siliconflow.cn/v1/black-forest-labs/FLUX.1-schnell/text-to-image" 

@plugins.register(name="siliconflow",
                  desc="siliconflow插件",
                  version="1.0",
                  author="Ray",
                  desire_priority=100)
class siliconflow_pic(Plugin):
    content = None
    config_data = None

    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        logger.info(f"[{__class__.__name__}] inited")

    def get_help_text(self, **kwargs):
        help_text = f"输入“画”或“Draw”开头、获取相关图片(建议使用英文描述，中文生图不太行)"
        return help_text

    def on_handle_context(self, e_context: EventContext):
        # 只处理文本消息
        if e_context['context'].type != ContextType.TEXT:
            return
        self.content = e_context["context"].content.strip()

        isExist = self.content.startswith("画") or self.content.startswith("Draw")

        if isExist:
            logger.info(f"[{__class__.__name__}] 收到消息: {self.content}")
            # 读取配置文件
            config_path = os.path.join(os.path.dirname(__file__), "config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r') as file:
                    self.config_data = json.load(file)
            else:
                logger.error(f"请先配置{config_path}文件")
                return

            reply = Reply()
            result = self.siliconflow_pic()
            if result != None:
                reply.type = ReplyType.IMAGE_URL
                reply.content = result
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS
            else:
                reply.type = ReplyType.ERROR
                reply.content = "获取失败,等待修复⌛️"
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS

    def siliconflow_pic(self):
        logger.info(self.config_data)

        key = self.config_data.get('siliconflow_api_key', '')

        logger.info("Bearer " + key)

        try:
            payload = {
                "prompt": self.content,
                "image_size": "800x800",
                "num_inference_steps": 20
            }
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "authorization": "Bearer " + key
            }

            response = requests.post(BASE_URL, json=payload, headers=headers).json()

            logger.info(response)

            img = response['images'][0]['url']
            logger.info(img)
            return img
        except Exception as e:
                logger.error(f"接口抛出异常:{e}")
        return None
    
    def is_startswith(string, prefix):
        return 