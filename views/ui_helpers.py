# -*- coding: utf-8 -*-
"""
views/ui_helpers.py
ฟังก์ชันช่วยเหลือที่ใช้ร่วมกันหลายหน้าจอ เพื่อไม่ให้โค้ดซ้ำกันในแต่ละไฟล์ view
"""

import io
import urllib.request
import tkinter as tk
from tkinter import font as tkfont, ttk

from PIL import Image, ImageTk

import config

_image_cache = {}  # (url_or_path, size) -> ImageTk.PhotoImage เก็บกันโหลดรูปเดิมซ้ำจากเน็ตทุกครั้ง


def get_ui_font(size=None, bold=False):
    """
    คืนค่า tkinter.font.Font โดยใช้ Tahoma (มากับ Windows ทุกเครื่อง รองรับภาษาไทย)
    ถ้าเครื่องไหนไม่มี Tahoma จริงๆ (เช่นทดสอบบน Linux/Mac) tkinter จะเลือกฟอนต์ใกล้เคียงให้อัตโนมัติ
    """
    return tkfont.Font(
        family=config.UI_FONT_FAMILY,
        size=size or config.UI_FONT_SIZE_NORMAL,
        weight="bold" if bold else "normal",
    )


def apply_global_font(root: tk.Tk):
    """
    ตั้งฟอนต์ default ของ Tk เองให้เป็น Tahoma ด้วย เพื่อให้ widget ที่ "ไม่ได้" ระบุ font=...
    ตรงๆ ในโค้ด (เช่น กล่อง messagebox.showinfo/showwarning/showerror/askyesno และ
    dropdown list ของ ttk.Combobox) ใช้ฟอนต์เดียวกับส่วนอื่นของโปรแกรมด้วย ไม่ใช่ฟอนต์ default
    ของระบบปฏิบัติการ (เช่น Segoe UI บน Windows) ซึ่งอาจวางสระ/วรรณยุกต์ภาษาไทยผิดตำแหน่ง
    ต้องเรียกครั้งเดียวหลังสร้าง root window (tk.Tk()) แต่ละหน้าต่างหลัก (LoginWindow, MainWindow)
    """
    for font_name in ("TkDefaultFont", "TkTextFont", "TkHeadingFont", "TkCaptionFont", "TkMenuFont"):
        try:
            tkfont.nametofont(font_name).configure(
                family=config.UI_FONT_FAMILY, size=config.UI_FONT_SIZE_NORMAL
            )
        except tk.TclError:
            pass

    root.option_add("*TCombobox*Listbox.font", (config.UI_FONT_FAMILY, config.UI_FONT_SIZE_NORMAL))


def load_photo_image(image_url: str, size=(80, 80)):
    """
    โหลดรูปภาพสินค้าจาก URL (เก็บเป็นลิงก์ในฐานข้อมูล ไม่ใช่ไฟล์ในเครื่องอีกต่อไป เพราะฐานข้อมูล
    ใช้ร่วมกับเว็บแอปที่รันบนเซิร์ฟเวอร์อื่น) แล้ว resize ให้พอดีกับที่ต้องการแสดงผล
    ถ้าไม่มีลิงก์ หรือโหลดจากเน็ตไม่ได้ (เช่น เน็ตหลุด) ให้ใช้รูป default ในเครื่องแทนเสมอ
    คืนค่าเป็น ImageTk.PhotoImage พร้อมใช้กับ tk.Label(image=...)
    """
    cache_key = (image_url, size)
    if cache_key in _image_cache:
        return _image_cache[cache_key]

    img = None
    fetch_succeeded = False
    if image_url:
        try:
            # Cloudflare (R2 public URL) ปฏิเสธ request ที่ไม่มี User-Agent แบบเบราว์เซอร์ด้วย 403
            # user-agent เริ่มต้นของ urllib คือ "Python-urllib/x.x" จึงต้องใส่เองเพื่อให้โหลดรูปผ่าน
            request = urllib.request.Request(image_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(request, timeout=5) as response:
                img = Image.open(io.BytesIO(response.read()))
            fetch_succeeded = True
        except Exception:
            img = None

    if img is None:
        img = Image.open(config.DEFAULT_PRODUCT_IMAGE)

    img = img.convert("RGB")
    img.thumbnail(size)
    photo = ImageTk.PhotoImage(img)
    if fetch_succeeded:
        # cache เฉพาะตอนโหลดจากเน็ตสำเร็จ ถ้าเน็ตหลุดชั่วคราวจะได้ลองใหม่ครั้งหน้าแทนที่จะติด fallback ไปตลอด session
        _image_cache[cache_key] = photo
    return photo


def configure_treeview_style():
    """
    ตั้งค่าฟอนต์และความสูงแถวให้ ttk.Treeview โดยเฉพาะ

    ทำไมต้องมีฟังก์ชันนี้แยกต่างหาก:
    ttk.Treeview ไม่รับ option font=... ตรงๆ เหมือน tk.Label/tk.Button
    ต้องตั้งผ่าน ttk.Style() เท่านั้น ถ้าไม่ตั้งไว้ Treeview จะใช้ฟอนต์ default ของระบบ
    ซึ่งบางเครื่อง Windows จะเลือกฟอนต์ที่ไม่รองรับการวางสระ/วรรณยุกต์ภาษาไทยอย่างถูกต้อง
    ทำให้ตัวอักษรซ้อนทับกัน นอกจากนี้ยังเพิ่ม rowheight ให้สูงพอสำหรับสระบน-ล่างของภาษาไทยด้วย
    เรียกฟังก์ชันนี้ครั้งเดียวก่อนสร้าง Treeview วิดเจ็ตแรกในแต่ละหน้าต่าง (Tk root) ก็เพียงพอ
    """
    style = ttk.Style()
    row_font = (config.UI_FONT_FAMILY, config.UI_FONT_SIZE_NORMAL)
    heading_font = (config.UI_FONT_FAMILY, config.UI_FONT_SIZE_NORMAL, "bold")
    style.configure("Treeview", font=row_font, rowheight=32)
    style.configure("Treeview.Heading", font=heading_font)


def center_window(window: tk.Tk, width: int, height: int):
    """จัดหน้าต่างให้อยู่กึ่งกลางจอ"""
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))
    window.geometry(f"{width}x{height}+{x}+{y}")


def show_loading(parent, text="กำลังโหลดข้อมูล..."):
    """
    แสดง overlay หน้าจอ 'กำลังโหลด' ระหว่างทำงานกับข้อมูล (ตามข้อกำหนด UX)
    คืนค่า widget ที่สร้าง เพื่อให้เรียก .destroy() ปิดทีหลังได้
    """
    overlay = tk.Frame(parent, bg="#f0f0f0")
    overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
    label = tk.Label(overlay, text=text, font=get_ui_font(size=12), bg="#f0f0f0")
    label.place(relx=0.5, rely=0.5, anchor="center")
    overlay.update()
    return overlay


def format_currency(amount) -> str:
    try:
        return f"{float(amount):,.2f} บาท"
    except (TypeError, ValueError):
        return "-"
