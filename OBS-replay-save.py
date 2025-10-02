import time
import json
import os
import sys
from obsws_python import ReqClient

def get_base_path():
    # 如果是 exe（PyInstaller/auto-py-to-exe 打包後）
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    # 開發環境（.py）
    return os.path.dirname(os.path.abspath(__file__))

# 讀取 config.json
base_path = get_base_path()
config_path = os.path.join(base_path, "config.json")

if not os.path.exists(config_path):
    print("❌ 錯誤：找不到 config.json，請確認檔案是否存在於程式所在資料夾。")
    input("請按任意鍵結束程式...")
    sys.exit(1)

try:
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
except json.JSONDecodeError as e:
    print(f"❌ 錯誤：config.json 格式不正確 ({e})")
    input("請按任意鍵結束程式...")
    sys.exit(1)

host = cfg.get("host")
port = cfg.get("port")
password = cfg.get("password")


# OBS WebSocket 連線與 Replay Buffer 狀態驗證
try:
    cl = ReqClient(host=host, port=port, password=password)
    cl.get_version()
    rb_status = cl.get_replay_buffer_status()
    print("✅ OBS WebSocket 連線成功")
    print("✅ OBS 控制程式啟動")
    if not rb_status.output_active:
        print("⚠️ Replay Buffer 尚未啟動，請先在 OBS 啟用 Replay Buffer！")
        print("請啟動 Replay Buffer 後再重新執行本程式。")
        input("請按任意鍵結束程式...")
    else:
        print("🎥 Replay Buffer 已啟動，開始倒數 5 分鐘...")
except Exception as e:
    print(f"❌ 連線或 Replay Buffer 驗證失敗：{e}")
    print("請確認 OBS WebSocket 連線資訊正確，OBS 已啟動且 WebSocket 插件與 Replay Buffer 已啟用。")
    input("請按任意鍵結束程式...")

total_seconds = 5 * 60 # 5 分鐘

# 倒數計時
for remaining in range(total_seconds, 0, -1):
    mins, secs = divmod(remaining, 60)
    print(f"\r⏳ 剩餘時間：{mins:02d}:{secs:02d}", end="")
    time.sleep(1)

# 存 Replay Buffer
cl.save_replay_buffer()
print("✅ Replay Buffer 已存檔！")

print("🚪 程式執行完成，10 秒後自動關閉...")
for i in range(10, 0, -1):
    print(f"⏳ {i} 秒後關閉...", end="\r")
    time.sleep(1)