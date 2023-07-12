from PIL import Image

image = Image.open(r"C:\Users\Administrator\Desktop\chat\t.jpg")  # 打开jpg文件
width=image.size[0]
height=image.size[1]
for x in range(width):
    for y in range(height):
        r, g, b = image.getpixel((x, y))
        if r > 220 and g > 220 and b > 220:  # 判断是否为白色背景
            image.putpixel((x, y), (224, 227, 236))  # 将白色背景改为绿色
        else:
            break  # 非白色背景则退出循环

for y in range(height):  # 从左边开始，遍历每一行
    for x in range(width):
        r, g, b = image.getpixel((x, y))
        if r > 220 and g > 220 and b > 220:  # 判断是否为白色背景
            image.putpixel((x, y), (224, 227, 236))  # 将白色背景改为绿色
        else:
            break  # 非白色背景则退出循环

for y in range(height-1, 0, -1):  # 从右边开始，遍历每一行
    for x in range(width-1, 0, -1):
        r, g, b = image.getpixel((x, y))
        if r > 220 and g > 220 and b > 220:  # 判断是否为白色背景
            image.putpixel((x, y), (224, 227, 236))  # 将白色背景改为绿色
        else:
            break  # 非白色背景则退出循环
image=image.resize((60,70))
image.save(r"C:\Users\Administrator\Desktop\chat\t2.jpg")  # 保存修改后的图片