import os
import sys
import tkinter as tk
from tkinter import Toplevel, Label, Entry, Button

def get_note_file_path():
    # 检测是否打包成了单一文件
    if getattr(sys, 'frozen', False):
        # 如果是打包的可执行文件，则获取其所在目录
        application_path = os.path.dirname(sys.executable)
    else:
        # 如果是脚本，则获取脚本所在目录
        application_path = os.path.dirname(__file__)

    # 将文件名添加到此路径
    return os.path.join(application_path, "sticky_note_data.txt")

def create_sticky_note():
    note_file = get_note_file_path()  # 使用函数获取文件路径

    def save_note():
        with open(note_file, "w", encoding="utf-8") as file:
            file.write(text.get("1.0", tk.END))  # 保存文本框中的内容

    def load_note():
        if os.path.exists(note_file):
            with open(note_file, "r", encoding="utf-8") as file:
                # 读取文本内容，并去除末尾的换行符，否则每加载一次就会多一个空白行
                txt = file.read().rstrip("\n")
                # 插入文本内容到文本框
                text.insert(tk.END, txt)

        # 重置撤销堆栈，避免撤销操作将原始文本清空
        text.edit_reset()

    # 创建主窗口
    note = tk.Tk()
    note.title("桌面便签")
    note.geometry("350x350+1000+200")

    # 创建一个文本框供用户输入
    text = tk.Text(note, wrap="word", undo=True)
    text.pack(expand=True, fill="both")

    # 启动加载便签内容
    load_note()



    # 设置窗口关闭时的行为
    def on_close():
        save_note()  # 保存便签内容
        note.destroy()  # 销毁窗口

    note.protocol("WM_DELETE_WINDOW", on_close)

    # 查找状态标志
    in_find = False

    # 存储当前查找字符串和最后查找到的位置
    current_search_str = ""
    last_search_pos = "1.0"

    find_dialog_open = False  # 查找窗口是否打开的标志

    def find_next():
        nonlocal last_search_pos
        # 移除旧的高亮标记
        text.tag_remove("found", "1.0", tk.END)

        # 搜索字符串并高亮显示
        index = text.search(current_search_str, last_search_pos, tk.END)
        if index:
            length = len(current_search_str)
            end_index = f"{index}+{length}c"
            last_search_pos = end_index  # 更新查找位置

            text.tag_add("found", index, end_index)
            text.tag_config("found", background="yellow")

            # 将视图滚动到找到的文本处
            text.see(index)
        else:
            last_search_pos = "1.0"  # 重置查找位置

    def open_find_dialog():
        nonlocal current_search_str, find_dialog_open

        if find_dialog_open:  # 如果查找窗口已经打开，则不再打开新窗口
            return

        # 创建查找对话框
        find_dialog = Toplevel(note)
        find_dialog.title("查找")
        find_dialog.geometry("200x100")
        find_dialog_open = True  # 更新查找窗口状态

        # 查找窗口关闭时的处理
        def on_find_dialog_close():
            nonlocal find_dialog_open
            find_dialog_open = False  # 更新查找窗口状态
            find_dialog.destroy()  # 销毁查找窗口

        # 设置窗口关闭时的行为
        def on_close():
            save_note()  # 保存便签内容
            note.destroy()  # 销毁窗口

        note.protocol("WM_DELETE_WINDOW", on_close)

        find_dialog.protocol("WM_DELETE_WINDOW", on_find_dialog_close)

        # 绑定 Esc 键以关闭查找窗口
        find_dialog.bind("<Escape>", lambda event: on_find_dialog_close())

        Label(find_dialog, text="查找内容:").pack()
        entry = Entry(find_dialog)
        entry.pack(pady=5)
        entry.focus_set()

        def on_find():
            nonlocal current_search_str
            current_search_str = entry.get()
            find_next()

        find_button = Button(find_dialog, text="查找下一个", command=on_find)
        find_button.pack()
        entry.bind("<Return>", lambda event: on_find())

        # 绑定 Ctrl+F

    note.bind("<Control-f>", lambda event: open_find_dialog())

    def toggle_window(event):
        global is_dragging
        if not is_dragging and not in_find:
            if note.state() == "withdrawn":
                note.deiconify()  # 显示主窗口
                icon_window.withdraw()  # 隐藏图标窗口
            else:
                note.withdraw()  # 隐藏主窗口
                icon_window.deiconify()  # 显示图标窗口

    # 存储图标位置的变量
    icon_pos = {"x": note.winfo_screenwidth() - 70, "y": 0}

    # 创建球状图标窗口
    icon_window = tk.Toplevel(note)
    icon_window.geometry("50x50+{}+0".format(icon_pos["x"]))
    icon_window.overrideredirect(True)  # 移除窗口边框
    icon_window.attributes("-topmost", True)  # 设置图标窗口始终置顶
    icon_window.attributes("-transparentcolor", "white")  # 将白色背景设置为透明

    # 在Canvas中绘制一个简单的图标
    canvas = tk.Canvas(icon_window, width=50, height=50, bg='white', highlightthickness=0)
    canvas.create_oval(10, 10, 40, 40, fill='orange', outline='orange')
    canvas.pack()

    # 拖动状态标志
    is_dragging = False

    def on_drag_start(event):
        global is_dragging
        is_dragging = False
        note.after(200, check_dragging, event.x_root, event.y_root)

    def check_dragging(x, y):
        global is_dragging
        if abs(x - icon_window.winfo_x()) > 5 or abs(y - icon_window.winfo_y()) > 5:
            is_dragging = True

    def on_drag(event):
        global is_dragging
        is_dragging = True
        icon_window.geometry(f"+{event.x_root - 25}+{event.y_root - 25}")
        icon_pos["x"] = event.x_root - 25
        icon_pos["y"] = event.y_root - 25

    canvas.bind("<ButtonPress-1>", on_drag_start)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", toggle_window)

    def on_focus_out(event):
        if event.widget == note and not find_dialog_open:
            note.withdraw()  # 隐藏主窗口
            icon_window.deiconify()  # 显示图标窗口
            icon_window.geometry("50x50+{}+{}".format(icon_pos["x"], icon_pos["y"]))
            save_note()  # 保存便签内容

    # 绑定主窗口失去焦点事件
    note.bind("<FocusOut>", on_focus_out)

    # 添加撤销功能的快捷键绑定
    note.bind("<Control-z>", lambda event: text.edit_undo())

    # 初始化时隐藏球状图标窗口
    icon_window.withdraw()

    # 运行应用程序
    note.mainloop()

# 创建一个便签
create_sticky_note()
