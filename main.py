# script/ImageGenerate/main.py

import logging
import os
import sys
import re
from PIL import Image, ImageDraw, ImageFont


# 添加项目根目录到sys.path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from app.config import owner_id
from app.api import *
from app.switch import load_switch, save_switch

# 输入图片路径
INPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "scripts",
    "ImageGenerate",
    "input",
)


# 输出图片路径
OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "scripts",
    "ImageGenerate",
    "output",
)


# 查看功能开关状态
def load_function_status(group_id):
    return load_switch(group_id, "function_status")


# 保存功能开关状态
def save_function_status(group_id, status):
    save_switch(group_id, "function_status", status)


# 通用的添加文字到图片的函数
async def add_text_to_image(input_image, box, text, angle=0):
    font_path = "/usr/share/fonts/truetype/win/SIMHEI.TTF"  # 使用中文字体
    initial_font_size = 10
    img = Image.open(input_image)
    draw = ImageDraw.Draw(img)

    # 矩形范围的宽度和高度
    box_width, box_height = box[2] - box[0], box[3] - box[1]
    box_x, box_y = box[0], box[1]

    font_size = initial_font_size
    text_width, text_height = 0, 0
    font = ImageFont.truetype(font_path, font_size)

    # 增加字体大小，直到文字宽度或高度超出矩形范围
    while True:
        font = ImageFont.truetype(font_path, font_size)
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width, text_height = (
            text_bbox[2] - text_bbox[0],
            text_bbox[3] - text_bbox[1],
        )
        if text_width > box_width or text_height > box_height:
            font_size -= 1
            break
        font_size += 1

    # 计算文字的起始位置以居中文字
    x = box_x + (box_width - text_width) / 2
    y = box_y + (box_height - text_height) / 2

    # 创建一个新的透明图层来绘制旋转的文本
    text_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
    text_draw = ImageDraw.Draw(text_layer)
    font = ImageFont.truetype(font_path, font_size)
    text_draw.text((x, y), text, font=font, fill=(0, 0, 0, 255))

    # 旋转文本图层
    rotated_text_layer = text_layer.rotate(
        angle,
        resample=Image.Resampling.BICUBIC,
        center=(x + text_width / 2, y + text_height / 2),
    )

    # 将旋转后的文本图层粘贴到原图像上
    img = Image.alpha_composite(img.convert("RGBA"), rotated_text_layer)

    # 转换为RGB模式以保存为PNG
    img = img.convert("RGB")
    output_path = os.path.join(OUTPUT_DIR, os.path.basename(input_image))
    img.save(output_path, "PNG")

    return output_path


# 狂粉
async def add_text_kf(text="W1ndys"):
    img_path = os.path.join(INPUT_DIR, "love.png")
    box = (257, 21, 724, 252)
    return await add_text_to_image(img_path, box, text, angle=-5)


# 向上竖起大拇指
async def add_text_up_hand(text="W1ndys"):
    img_path = os.path.join(INPUT_DIR, "up_hand.png")
    box = (30, 690, 931, 907)
    return await add_text_to_image(img_path, box, text, angle=0)


# 源鲁杯邀请函
async def add_text_invitation(text="Yuanloo"):
    img_path = os.path.join(INPUT_DIR, "yuanloo.png")
    box = (92, 655, 663, 810)
    return await add_text_to_image(img_path, box, text, angle=0)


# 群消息处理函数
async def handle_ImageGenerate_group_message(websocket, msg):
    # 确保数据目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    try:
        user_id = str(msg.get("user_id"))
        group_id = str(msg.get("group_id"))
        raw_message = str(msg.get("raw_message"))
        role = str(msg.get("sender", {}).get("role"))
        message_id = str(msg.get("message_id"))

        if raw_message.startswith("狂粉"):
            match = re.search(r"狂粉(.*)", raw_message)
            if match:
                if len(match.group(1)) <= 10 and len(match.group(1)) > 0:
                    del_message_id = await send_group_msg_with_reply(
                        websocket, group_id, "图片生成中..."
                    )
                    prompt = match.group(1)
                    img_path = await add_text_kf(prompt)

                    # 文件
                    if img_path:
                        await delete_msg(websocket, del_message_id)
                        await send_group_msg(
                            websocket, group_id, f"[CQ:image,file=file://{img_path}]"
                        )
                else:
                    await send_group_msg(
                        websocket,
                        group_id,
                        f"[CQ:reply,id={message_id}]输入内容不合法，请重新输入",
                    )
        elif raw_message.startswith("hand"):
            match = re.search(r"hand(.*)", raw_message)
            if match:
                if len(match.group(1)) <= 10 and len(match.group(1)) > 0:
                    del_message_id = await send_group_msg_with_reply(
                        websocket, group_id, "图片生成中..."
                    )
                    prompt = match.group(1)
                    img_path = await add_text_up_hand(prompt)

                    # 文件
                    if img_path:
                        await delete_msg(websocket, del_message_id)
                        await send_group_msg(
                            websocket, group_id, f"[CQ:image,file=file://{img_path}]"
                        )
                else:
                    await send_group_msg(
                        websocket,
                        group_id,
                        f"[CQ:reply,id={message_id}]输入内容不合法，请重新输入",
                    )

        elif raw_message.startswith("YL邀请函"):
            match = re.search(r"YL邀请函(.*)", raw_message)
            if match:
                if len(match.group(1)) <= 15 and len(match.group(1)) > 0:
                    del_message_id = await send_group_msg_with_reply(
                        websocket, group_id, "图片生成中..."
                    )
                    prompt = match.group(1)
                    img_path = await add_text_invitation(prompt)

                    # 文件
                    if img_path:
                        await delete_msg(websocket, del_message_id)
                        await send_group_msg(
                            websocket, group_id, f"[CQ:image,file=file://{img_path}]"
                        )
                else:
                    await send_group_msg(
                        websocket,
                        group_id,
                        f"[CQ:reply,id={message_id}]输入内容不合法，请重新输入",
                    )
    except Exception as e:
        logging.error(f"处理ImageGenerate群消息失败: {e}")
        return
