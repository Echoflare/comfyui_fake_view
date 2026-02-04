import os
import random
import io
from PIL import Image, ImageDraw
from aiohttp import web
from server import PromptServer

def generate_fake_image(width=512, height=512):
    bg_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img, 'RGBA')
    
    for _ in range(random.randint(20, 50)):
        shape_type = random.choice(['rect', 'ellipse', 'polygon'])
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), random.randint(100, 255))
        
        if shape_type == 'rect':
            x1, y1 = random.randint(0, width), random.randint(0, height)
            x2, y2 = random.randint(0, width), random.randint(0, height)
            draw.rectangle([min(x1,x2), min(y1,y2), max(x1,x2), max(y1,y2)], fill=color)
        elif shape_type == 'ellipse':
            x1, y1 = random.randint(0, width), random.randint(0, height)
            x2, y2 = random.randint(0, width), random.randint(0, height)
            draw.ellipse([min(x1,x2), min(y1,y2), max(x1,x2), max(y1,y2)], fill=color)
        elif shape_type == 'polygon':
            points = [(random.randint(0, width), random.randint(0, height)) for _ in range(random.randint(3, 6))]
            draw.polygon(points, fill=color)
    print(f"[调试] 已生成假图片对象: {img}")
    return img

@web.middleware
async def fake_view_middleware(request, handler):
    if request.path == "/view":
        print(f"[调试] 已触发劫持中间件: {request.path}")
        if "filename" in request.rel_url.query:
            filename = request.rel_url.query["filename"]
            img = generate_fake_image(512, 512)
            image_format = 'png'
            if 'preview' in request.rel_url.query:
                preview_info = request.rel_url.query['preview'].split(';')
                if preview_info[0] in ['webp', 'jpeg']:
                    image_format = preview_info[0]

            buffer = io.BytesIO()
            img.save(buffer, format=image_format.upper())
            buffer.seek(0)

            return web.Response(
                body=buffer.read(),
                content_type=f'image/{image_format}',
                headers={
                    "Content-Disposition": f"filename=\"fake_{filename}\"",
                    "Cache-Control": "no-store, no-cache, must-revalidate"
                }
            )
    return await handler(request)

server = PromptServer.instance
app = server.app
app.middlewares.append(fake_view_middleware)

print("[调试] 假图片拓展路由劫持成功")

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}