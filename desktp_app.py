import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from main import AadharValidator
import uuid
import threading

class AadhaarDesktopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aadhaar Validator Desktop App")
        self.root.geometry("480x600")
        self.validator = None
        self.session_id = None
        self.captcha_path = None
        self.aadhar_number = tk.StringVar()
        self.captcha_text = tk.StringVar()
        self.result_text = tk.StringVar()
        self.captcha_img_label = None
        self.result_table = None
        self.loader = None
        self._build_ui()

    def _build_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#f5f6fa')
        style.configure('TLabel', background='#f5f6fa', font=('Segoe UI', 11))
        style.configure('TButton', font=('Segoe UI', 11, 'bold'), padding=6)
        style.configure('Treeview', font=('Segoe UI', 11), rowheight=28)
        style.configure('Treeview.Heading', font=('Segoe UI', 12, 'bold'))

        frame = ttk.Frame(self.root, padding=30, style='TFrame')
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Aadhaar Number:", style='TLabel').pack(anchor=tk.W, pady=(0, 5))
        aadhar_entry = ttk.Entry(frame, textvariable=self.aadhar_number, width=32, font=('Segoe UI', 12))
        aadhar_entry.pack(pady=(0, 15))

        self.get_captcha_btn = ttk.Button(frame, text="Get CAPTCHA", command=self.get_captcha_thread, style='TButton')
        self.get_captcha_btn.pack(pady=(0, 20))

        self.captcha_img_label = ttk.Label(frame, style='TLabel')
        self.captcha_img_label.pack(pady=(0, 10))

        ttk.Label(frame, text="Enter CAPTCHA:", style='TLabel').pack(anchor=tk.W, pady=(0, 5))
        captcha_entry = ttk.Entry(frame, textvariable=self.captcha_text, width=20, font=('Segoe UI', 12))
        captcha_entry.pack(pady=(0, 15))

        self.submit_btn = ttk.Button(frame, text="Submit", command=self.submit_captcha_thread, state=tk.DISABLED, style='TButton')
        self.submit_btn.pack(pady=(0, 20))

        ttk.Label(frame, text="Result:", style='TLabel').pack(anchor=tk.W, pady=(0, 5))
        self.result_label = ttk.Label(frame, textvariable=self.result_text, style='TLabel', font=('Segoe UI', 11, 'italic'), wraplength=400, justify=tk.LEFT)
        self.result_label.pack(pady=(0, 10))

        self.result_table = ttk.Treeview(frame, columns=("Field", "Value"), show="headings", height=5, style='Treeview')
        self.result_table.heading("Field", text="Field")
        self.result_table.heading("Value", text="Value")
        self.result_table.column("Field", width=150, anchor=tk.W)
        self.result_table.column("Value", width=250, anchor=tk.W)
        self.result_table.pack(pady=(0, 10), fill=tk.X)
        self.result_table.pack_forget()  # Hide initially

        # Loader (progress bar)
        self.loader = ttk.Progressbar(frame, mode='indeterminate', length=200)
        self.loader.pack(pady=(10, 0))
        self.loader.pack_forget()

    def show_loader(self):
        self.loader.pack()
        self.loader.start(10)
        self.root.update_idletasks()

    def hide_loader(self):
        self.loader.stop()
        self.loader.pack_forget()
        self.root.update_idletasks()

    def get_captcha_thread(self):
        threading.Thread(target=self.get_captcha, daemon=True).start()

    def get_captcha(self):
        self.show_loader()
        aadhar = self.aadhar_number.get().strip()
        if not aadhar or len(aadhar) != 12 or not aadhar.isdigit():
            self.hide_loader()
            messagebox.showerror("Input Error", "Please enter a valid 12-digit Aadhaar number.")
            return
        self.session_id = str(uuid.uuid4())
        self.captcha_path = f"images/captcha_{self.session_id}.png"
        try:
            self.validator = AadharValidator(headless=True)
            self.validator.save_captcha(self.captcha_path)
            self.root.after(0, self.show_captcha_image)
            self.root.after(0, lambda: self.submit_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.result_text.set(""))
            self.root.after(0, lambda: self.result_table.pack_forget())
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to get CAPTCHA: {e}"))
            self.root.after(0, self.cleanup)
        finally:
            self.hide_loader()

    def show_captcha_image(self):
        try:
            img = Image.open(self.captcha_path)
            img = img.resize((220, 80))
            self.tk_img = ImageTk.PhotoImage(img)
            self.captcha_img_label.config(image=self.tk_img)
        except Exception as e:
            self.captcha_img_label.config(text="[CAPTCHA image error]")

    def submit_captcha_thread(self):
        threading.Thread(target=self.submit_captcha, daemon=True).start()

    def submit_captcha(self):
        self.show_loader()
        captcha = self.captcha_text.get().strip()
        aadhar = self.aadhar_number.get().strip()
        if not captcha:
            self.hide_loader()
            messagebox.showerror("Input Error", "Please enter the CAPTCHA text.")
            return
        try:
            result = self.validator.validate_aadhar(aadhar, captcha)
            self.result_table.delete(*self.result_table.get_children())
            if result["status"].startswith("ERROR"):
                self.root.after(0, lambda: self.result_text.set(result["status"]))
                self.root.after(0, lambda: self.result_table.pack_forget())
            elif result["isValid"]:
                self.root.after(0, lambda: self.result_text.set("Aadhaar is VALID."))
                self.root.after(0, lambda: self.result_table.pack())
                for k, v in (result["data"] or {}).items():
                    self.root.after(0, lambda k=k, v=v: self.result_table.insert("", tk.END, values=(k, v)))
            else:
                self.root.after(0, lambda: self.result_text.set("Aadhaar is INVALID."))
                self.root.after(0, lambda: self.result_table.pack_forget())
        except Exception as e:
            self.root.after(0, lambda: self.result_text.set(f"Error: {e}"))
            self.root.after(0, lambda: self.result_table.pack_forget())
        finally:
            self.hide_loader()
            self.root.after(0, self.cleanup)

    def cleanup(self):
        if self.validator:
            try:
                self.validator.close_browser()
            except Exception:
                pass
            self.validator = None
        if self.captcha_path and os.path.exists(self.captcha_path):
            try:
                os.remove(self.captcha_path)
            except Exception:
                pass
        self.submit_btn.config(state=tk.DISABLED)
        self.captcha_img_label.config(image="")
        self.captcha_text.set("")

if __name__ == "__main__":
    if not os.path.exists("images"):
        os.makedirs("images")
    root = tk.Tk()
    app = AadhaarDesktopApp(root)
    root.mainloop()
