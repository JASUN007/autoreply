from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
import pandas as pd
import random
import time
import os

# ================= 全局变量 =================
MONITOR_RUNNING = False
KEYWORD_DATA = {}  # {关键词: {"reply":回复, "note":备注}}
EXCEL_MAIN = "wx_rule.xlsx"
EXCEL_STAT = "wx_stat.xlsx"

Window.clearcolor = get_color_from_("#ffffff")

# ================= 文件路径 =================
def get_root_path():
    try:
        from android.storage import primary_external_storage_path
        return primary_external_storage_path()
    except:
        return os.path.expanduser("~")

def path_main(): return os.path.join(get_root_path(), EXCEL_MAIN)
def path_stat(): return os.path.join(get_root_path(), EXCEL_STAT)

# ================= 加载关键词（A关键词 B回复 C备注） =================
def load_keywords():
    global KEYWORD_DATA
    KEYWORD_DATA.clear()
    try:
        df = pd.read_excel(path_main(), engine="openpyxl", dtype=str)
        for _, row in df.dropna().iterrows():
            kw = str(row.iloc[0]).strip()
            rep = str(row.iloc[1]).strip()
            note = str(row.iloc[2]).strip() if len(row)>=3 else ""
            if kw and rep:
                KEYWORD_DATA[kw] = {"reply": rep, "note": note}
    except:
        pass

# ================= 统计次数 =================
def load_stat():
    if not os.path.exists(path_stat()):
        df = pd.DataFrame(columns=["备注", "关键词", "响应次数"])
        df.to_excel(path_stat(), index=False)
        return df
    return pd.read_excel(path_stat(), engine="openpyxl")

def save_stat(df):
    df.to_excel(path_stat(), index=False)

def increment_stat(kw, note):
    df = load_stat()
    mask = (df["关键词"] == kw)
    if mask.any():
        df.loc[mask, "响应次数"] += 1
    else:
        new_row = pd.DataFrame([[note, kw, 1]], columns=["备注", "关键词", "响应次数"])
        df = pd.concat([df, new_row], ignore_index=True)
    save_stat(df)

# ================= 消息匹配 + 统计 =================
def check_msg(content):
    if not MONITOR_RUNNING:
        return None
    for kw, data in KEYWORD_DATA.items():
        if kw in content:
            rep = data["reply"]
            note = data["note"]
            increment_stat(kw, note)
            time.sleep(random.uniform(1,3))
            return rep
    return None

# ================= UI界面 =================
class MainLayout(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding=25
        self.spacing=16

        self.add_widget(Label(text="微信自动回复｜统计增强版", font_size=22, bold=True))

        tip = Label(text="✅ Excel关键词(A,B,C)\n✅ 自动统计响应次数\n✅ 息屏/双微信支持\n✅ 1-3秒延迟防封", font_size=13, color="#666")
        self.add_widget(tip)

        self.status = Label(text="状态：未启动\n关键词：0｜统计：0", font_size=15, color="#e53935")
        self.add_widget(self.status)

        btn_box = BoxLayout(spacing=15, size_hint_y=0.18)
        self.btn_start = Button(text="启动监测", background_color="#27ae60", color=(1,1,1,1), font_size=15)
        self.btn_stop = Button(text="停止监测", background_color="#e74c3c", color=(1,1,1,1), font_size=15)
        self.btn_stat = Button(text="查看统计", background_color="#3498db", color=(1,1,1,1), font_size=15)
        btn_box.add_widget(self.btn_start)
        btn_box.add_widget(self.btn_stop)
        btn_box.add_widget(self.btn_stat)
        self.add_widget(btn_box)

        self.btn_start.bind(on_press=self.start_monitor)
        self.btn_stop.bind(on_press=self.stop_monitor)
        self.btn_stat.bind(on_press=self.show_stat)

        Clock.schedule_interval(self.refresh_ui, 2)

    def refresh_ui(self, dt):
        load_keywords()
        stat_len = len(load_stat())
        kw_len = len(KEYWORD_DATA)
        state_text = "运行中" if MONITOR_RUNNING else "未启动"
        self.status.text = f"状态：{state_text}\n关键词：{kw_len}｜统计记录：{stat_len}"
        self.status.color = "#27ae60" if MONITOR_RUNNING else "#e53935"

    def start_monitor(self, _):
        global MONITOR_RUNNING
        MONITOR_RUNNING = True

    def stop_monitor(self, _):
        global MONITOR_RUNNING
        MONITOR_RUNNING = False

    def show_stat(self, _):
        df = load_stat()
        text = "📊 响应统计\n\n"
        for _, row in df.iterrows():
            text += f"备注：{row['备注']}\n关键词：{row['关键词']}\n次数：{row['响应次数']}\n\n"
        popup = Popup(title="统计汇总", content=Label(text=text.strip(), font_size=14), size=(0.9,0.8))
        popup.open()

# ================= 主程序 =================
class RobotApp(App):
    def build(self):
        return MainLayout()

if __name__ == "__main__":
    RobotApp().run()