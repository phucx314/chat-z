import tkinter as tk

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text):
        tmp = tk.Label(parent, text=text)
        tmp.update_idletasks()
        tw = tmp.winfo_reqwidth()
        tmp.destroy()
        
        super().__init__(parent, width=tw, height=20)
        self.delete("all")

root = tk.Tk()
topbar = tk.Frame(root)
topbar.pack()
b = RoundedButton(topbar, "Test")
b.pack()
root.update()
print("Success. Widget name:", b._w)
