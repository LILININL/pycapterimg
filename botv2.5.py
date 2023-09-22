import tkinter as tk
from tkinter import ttk
import threading
import pyautogui
from PIL import Image, ImageTk
import time
import cv2

class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("InBot")
        self.root.geometry("424x424")  # เปลี่ยนขนาด UI เป็น 424x380
        
        self.is_running = False
        self.rounds = 1
        self.success_rounds = 0
        self.error_rounds = 0

        self.image_paths = ['photo/s1.png', 'photo/s2.png', 'photo/s3.png', 'photo/s4.png']

        # โหลดไอคอนและแสดงใน Label
        icon_image = Image.open("photo/325.jpg")  # เปลี่ยนชื่อไฟล์ไอคอนตามที่คุณต้องการ
        icon_image = icon_image.resize((100, 100))  # ปรับขนาดไอคอนตามที่ต้องการ
        self.icon = ImageTk.PhotoImage(icon_image,)
        self.icon_label = ttk.Label(root, image=self.icon)
        self.icon_label.pack()

        button_frame = ttk.Frame(root)
        button_frame.pack()

        # self.start_button = ttk.Button(button_frame, text="เริ่ม", command=self.start_clicker)
        self.stop_button = ttk.Button(button_frame, text="หยุด", command=self.stop_clicker)
        self.unlimited_button = ttk.Button(button_frame, text="เริ่มทำงาน (ไม่จำกัดรอบ)", command=self.start_unlimited)

        # self.start_button.pack(side="left", padx=5,expand=30)  # ปุ่ม "เริ่ม" อยู่ด้านซ้าย
        self.stop_button.pack(side="left", padx=5,expand=30)  # ปุ่ม "หยุด" อยู่ด้านขวา
        self.unlimited_button.pack(side="left", padx=5,expand=30)  # ปุ่ม "เริ่มทำงาน (ไม่จำกัดรอบ)" อยู่ตรงกลาง

        self.rounds_label = ttk.Label(root, text="จำนวนรอบ:")
        self.rounds_entry = ttk.Entry(root)
        self.log_text = tk.Text(root, height=10, width=50)  # สร้างช่องแสดง log การทำงาน

        self.success_error_frame = ttk.Frame(root)
        self.success_label = ttk.Label(self.success_error_frame, text="สำเร็จ: 0")
        self.error_label = ttk.Label(self.success_error_frame, text="ผิดพลาด: 0")

        self.rounds_label.pack()
        self.rounds_entry.pack()        
        self.success_error_frame.pack()
        self.success_label.pack(side="left", padx=10)  # ช่องแสดง "สำเร็จ"
        self.error_label.pack(side="left" , padx=10)  # ช่องแสดง "ผิดพลาด"
        self.log_text.pack(padx=10)
    
    def log(self, message):
        # เพิ่มข้อความ log ในช่องแสดง log การทำงาน
        self.log_text.insert(tk.END, f'{message}\n')
        self.log_text.see(tk.END)  # ให้ scrollbar แสดงข้อความล่าสุด
    
    def start_clicker(self):
        if not self.is_running:
            rounds = self.rounds_entry.get()
            if not rounds.isdigit() or int(rounds) <= 0 or rounds == "0" or rounds == "inf":
                self.log("ใส่แค่ตัวเลขเท่านั้น  '1' หรือ '999'")
                return

            self.is_running = True
            self.rounds = int(rounds)
            self.success_rounds = 0
            self.error_rounds = 0
            self.update_round_labels()
            self.rounds_entry.config(state='disabled')
            self.start_button.config(state='disabled')
            self.stop_button.config(state='active')
            self.unlimited_button.config(state='disabled')
            
            self.auto_click_thread = threading.Thread(target=self.auto_click)
            self.auto_click_thread.start()
    
    def start_unlimited(self):
        if not self.is_running:
            self.is_running = True
            self.rounds = float('inf')  # รอบไม่จำกัด
            self.success_rounds = 0
            self.error_rounds = 0
            self.update_round_labels()
            self.rounds_entry.config(state='disabled')
            # self.start_button.config(state='disabled')
            self.stop_button.config(state='active')
            self.unlimited_button.config(state='disabled')
            
            self.auto_click_thread = threading.Thread(target=self.auto_click)
            self.auto_click_thread.start()
    
    def stop_clicker(self):
        self.is_running = False
        self.rounds_entry.config(state='normal')
        # self.start_button.config(state='active')
        self.stop_button.config(state='disabled')
        self.unlimited_button.config(state='active')
    
    def find_and_double_click(self, image_path, confidence=0.8):
        # โหลดรูปภาพที่ต้องการค้นหา
        template = cv2.imread(image_path)
        h, w = template.shape[:-1]

        # ค้นหารูปภาพในหน้าจอปัจจุบัน
        screenshot = pyautogui.screenshot()
        screenshot.save('screenshot.png')  # เซฟรูปหน้าจอเพื่อตรวจสอบ

        screenshot = cv2.imread('screenshot.png')
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)

        # หาตำแหน่งที่มีความเหมือนสูงสุด
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= confidence:
            # คำนวณตำแหน่งที่ต้องการคลิก
            top_left = max_loc
            bottom_right = (top_left[0] + w, top_left[1] + h)

            # คลิกที่ตำแหน่งที่พบรูปภาพ 2 ครั้ง (ดับเบิ้ลคลิก)
            x, y = pyautogui.center((top_left[0], top_left[1], w, h))
            pyautogui.doubleClick(x, y)
            return True
        else:
            return False

    def auto_click(self):
        current_image_index = 0

        while self.is_running and self.rounds >= 0:
            image_path = self.image_paths[current_image_index]
            found = self.find_and_double_click(image_path)

            if found:
                self.success_rounds += 1
            else:
                self.error_rounds += 1

            self.update_round_labels()

            if found:
                self.rounds -= 1
            
            current_image_index = (current_image_index ) % len(self.image_paths)

            if not found and current_image_index == 0:
                # ถ้าไม่พบรูปภาพใด ๆ และมาถึงรูปภาพสุดท้ายในรายการ
                # จะเริ่มการค้นหารูปภาพใหม่ตั้งแต่รูปแรก
                self.log("ไม่พบรูปภาพใด ๆ และกำลังเริ่มการค้นหาใหม่")
                time.sleep(5)  # สร้างการดีเลย์ 5 วินาทีก่อนการค้นหารูปภาพใหม่

        self.is_running = False
        self.rounds_entry.config(state='normal')
        self.start_button.config(state='active')
        self.stop_button.config(state='disabled')
        self.unlimited_button.config(state='active')

    def update_round_labels(self):
        self.success_label.config(text=f"สำเร็จ: {self.success_rounds}")
        self.error_label.config(text=f"ผิดพลาด: {self.error_rounds}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClickerApp(root)
    root.mainloop()
