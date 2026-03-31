import pygame
import os
from langchain.tools import tool

# 初始化pygame的音频模块（必须执行）
pygame.mixer.init()
@tool
def play_music():
    """
    播放音乐
    """
    file_path ="D:\\m.mp3"
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    # 保持程序运行，直到音乐播放完毕
    while pygame.mixer.music.get_busy():
        continue
    pygame.mixer.music.unload()
    return "播放成功"

@tool
def stop_music():
    """
    停止播放音乐
    """
    pygame.mixer.music.stop()
    return "停止成功"