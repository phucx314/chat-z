import tkinter as tk

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command=None, radius=10):
        super().__init__(parent, width=100, height=40, bg="black")
        self._cmd = command
        self.create_rectangle(0,0,100,40, fill="red")
        self.create_text(50,20, text=text, fill="white")
        self.bind("<Button-1>", self._on_click)
        
    def _on_click(self, event):
        print("Clicked!")
        if self._cmd:
            self._cmd()

root = tk.Tk()
b = RoundedButton(root, "Test", command=lambda: print("Command executed"))
b.pack()
b.event_generate("<Button-1>", x=50, y=20)
root.update()
