# -*- coding: utf-8 -*-
"""
views/backup_view.py
หน้า "สำรองข้อมูล" (เห็นเฉพาะ admin เท่านั้น)

หมายเหตุ: ตั้งแต่ย้ายไปใช้ฐานข้อมูล TiDB ร่วมกับเว็บแอป (มีคนอื่น/อุปกรณ์อื่นเข้าถึงพร้อมกันได้ตลอดเวลา)
ฟีเจอร์ "กู้คืนข้อมูล" แบบเขียนทับทั้งฐานข้อมูลถูกตัดออกไปแล้ว เพราะเสี่ยงเขียนทับข้อมูลที่คนอื่น
กำลังใช้งานอยู่จริงโดยไม่มีทางแจ้งเตือนได้ ถ้าต้องการกู้คืนข้อมูลจริงๆ ให้ใช้ฟีเจอร์ Backup/PITR
ในหน้าคอนโซลของ TiDB Cloud โดยตรง ที่นี่มีไว้แค่ export ข้อมูลปัจจุบันเป็นไฟล์ JSON ไว้ดูย้อนหลัง/ตรวจสอบ
"""

from tkinter import filedialog, messagebox
import tkinter as tk

from controllers import backup_controller
from views import ui_helpers
import config


class BackupView(tk.Frame):
    def __init__(self, parent, current_user):
        super().__init__(parent, bg="white")
        self.current_user = current_user
        self._build_ui()

    def _build_ui(self):
        header = tk.Label(
            self, text="สำรองข้อมูล", font=ui_helpers.get_ui_font(size=config.UI_FONT_SIZE_HEADER, bold=True),
            bg="white", anchor="w",
        )
        header.pack(fill="x", padx=20, pady=(20, 10))

        info_frame = tk.LabelFrame(self, text="เกี่ยวกับฟีเจอร์นี้", bg="white", font=ui_helpers.get_ui_font())
        info_frame.pack(fill="x", padx=20, pady=(0, 15))
        tk.Label(
            info_frame,
            text=(
                "ฐานข้อมูลของระบบนี้ใช้ร่วมกับเว็บแอป (TiDB Cloud) ซึ่งอาจมีคนอื่นใช้งานพร้อมกันอยู่ตลอดเวลา\n"
                "หน้านี้จึงทำได้แค่ \"export\" ข้อมูลปัจจุบันออกเป็นไฟล์ JSON ไว้เก็บสำรอง/ตรวจสอบย้อนหลังเท่านั้น\n"
                "ถ้าต้องการกู้คืนข้อมูลจริงๆ ให้ใช้ฟีเจอร์ Backup/PITR ในหน้าคอนโซลของ TiDB Cloud โดยตรง"
            ),
            font=ui_helpers.get_ui_font(size=9), fg="#666666", bg="white", justify="left",
        ).pack(anchor="w", padx=10, pady=10)

        export_frame = tk.LabelFrame(self, text="สำรองข้อมูล (Export)", bg="white", font=ui_helpers.get_ui_font())
        export_frame.pack(fill="x", padx=20, pady=(0, 15))
        tk.Label(
            export_frame,
            text="บันทึกข้อมูลสินค้า, ผู้ใช้งาน (ไม่รวม PIN), ราคา, ประวัติสต็อก และบันทึกกิจกรรมทั้งหมด "
                 "เป็นไฟล์ JSON ไว้ในเครื่อง",
            font=ui_helpers.get_ui_font(size=9), fg="#666666", bg="white", wraplength=700, justify="left",
        ).pack(anchor="w", padx=10, pady=(10, 5))
        tk.Button(
            export_frame, text="สำรองข้อมูลตอนนี้...", font=ui_helpers.get_ui_font(bold=True),
            bg="#2e7d32", fg="white", cursor="hand2", command=self._on_export_click,
        ).pack(anchor="w", padx=10, pady=(0, 10))

    def _on_export_click(self):
        destination = filedialog.asksaveasfilename(
            title="บันทึกไฟล์สำรองข้อมูล",
            initialfile=backup_controller.default_export_filename(),
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
        )
        if not destination:
            return

        try:
            backup_controller.export_snapshot(destination, self.current_user)
        except Exception as e:
            messagebox.showerror("สำรองข้อมูลไม่สำเร็จ", str(e), parent=self)
            return

        messagebox.showinfo("สำเร็จ", f"สำรองข้อมูลเรียบร้อยแล้วที่:\n{destination}", parent=self)
