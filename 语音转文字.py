# audio_monitor_simple.py
import whisper
import os
import time

# ===== 配置 =====
WATCH_FOLDER = r"C:\Users\43162\Desktop\video"  # 监控的文件夹
MODEL_SIZE = "medium"  # 模型大小
CHECK_INTERVAL = 1  # 检查间隔(秒)

#设置ffmpeg路径
os.environ["PATH"] += os.pathsep + r"C:\Users\43162\Desktop\ffmpeg-8.0.1-essentials_build\bin"


# ===== 简体转换函数=====
def to_simple(text):
    """繁体转简体"""
    try:
        from zhconv import convert
        return convert(text, 'zh-cn')
    except ImportError:
        try:
            import opencc
            converter = opencc.OpenCC('t2s.json')
            return converter.convert(text)
        except ImportError:
            return text


# ===== 处理单个文件 =====
def process_file(audio_file, model):
    """处理音频文件：完全复制原来成功的逻辑"""
    try:
        # 1. 检查文件
        if not os.path.exists(audio_file):
            print(f"文件不存在: {audio_file}")
            return False

        # 2. 转文字
        print("开始转文字...")
        result = model.transcribe(audio_file, language="zh", fp16=True)
        text = result["text"].strip()

        # 3. 转简体
        simple_text = to_simple(text)

        # 4. 输出
        print("\n" + "=" * 40)
        print("结果:")
        print("=" * 40)
        print(simple_text)
        print("=" * 40)

        # 5. 保存为同名的txt文件
        txt_file = audio_file.rsplit('.', 1)[0] + ".txt"
        with open(txt_file, "w", encoding="utf-8") as f:
            f.write(simple_text)
        print(f"已保存: {txt_file}")

        # 6. 删除原音频文件
        os.remove(audio_file)
        print(f"已删除原文件: {os.path.basename(audio_file)}")

        return True

    except Exception as e:
        print(f"处理出错: {e}")
        return False


# ===== 主监控循环 =====
def main():
    print(f"监控文件夹: {WATCH_FOLDER}")

    # 确保文件夹存在
    if not os.path.exists(WATCH_FOLDER):
        os.makedirs(WATCH_FOLDER, exist_ok=True)
        print(f"创建文件夹: {WATCH_FOLDER}")

    # 加载模型 (一次性)
    print(f"加载模型: {MODEL_SIZE}")
    model = whisper.load_model(MODEL_SIZE)
    print("模型加载完成，开始监控...\n")

    processed_files = set()  # 记录已处理的文件

    try:
        while True:
            # 扫描文件夹
            for filename in os.listdir(WATCH_FOLDER):
                filepath = os.path.join(WATCH_FOLDER, filename)

                # 只处理音频文件且未处理过
                if (os.path.isfile(filepath) and
                        filepath.lower().endswith(('.mp3', '.wav', '.m4a', '.m4b', '.flac', '.aac', '.ogg')) and
                        filepath not in processed_files):
                    print(f"\n发现新文件: {filename}")
                    success = process_file(filepath, model)
                    processed_files.add(filepath)

            # 等待
            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("\n监控已停止")


# ===== 运行 =====
if __name__ == "__main__":
    main()