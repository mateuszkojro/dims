import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo


def send(code):
    return lambda event=None: print(code)


def show_popup(title, content):
    return lambda event=None: showinfo(title, content)

class App(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        self.up = tk.Button(padx=30, pady=30, text="Up", command=send("Up"))
        self.down = tk.Button(padx=30,
                              pady=30,
                              text="Down",
                              command=send("Down"))
        self.left = tk.Button(padx=30,
                              pady=30,
                              text="Left",
                              command=send("Left"))
        self.right = tk.Button(padx=30,
                               pady=30,
                               text="Right",
                               command=send("Right"))
        self.enter = tk.Button(padx=30,
                               pady=30,
                               text="Enter",
                               command=send("Enter"))

        self.esc = tk.Button(padx=30, pady=30, text="Esc", command=send("Esc"))

        help_text = "You can either use the displayed controlls or just use your keboard:\n Move with arrow keys, accept with \"enter\", cancel with \"esc\" key."
        self.info_button = tk.Button(padx=30,
                                     pady=30,
                                     text="Help",
                                     command=show_popup("Help", help_text))


        self.up.grid(row=0, column=1)
        self.down.grid(row=2, column=1)
        self.left.grid(row=1, column=0)
        self.right.grid(row=1, column=2)
        self.enter.grid(row=4, column=0)
        self.esc.grid(row=4, column=1)
        self.info_button.grid(row=4, column=2)

        # Define a callback for when the user hits return.
        # It prints the current value of the variable.
        self.master.bind('<Key-Up>', send("Up"))
        self.master.bind('<Key-Down>', send("Down"))
        self.master.bind('<Key-Left>', send("Left"))
        self.master.bind('<Key-Right>', send("Right"))
        self.master.bind('<Key-Return>', send("Enter"))
        self.master.bind('<Key-Escape>', send("Esc"))

    def print_contents(self, event):
        print("Hi. The current entry content is:", self.contents.get())

if __name__ == '__main__':
    root = tk.Tk()
    root.title("Remote joystick")
    style = ttk.Style(root)

    try:
        style.theme_use("vista")
    except:
        print("Theme vista not found going back to default theme")

    myapp = App(root)

    myapp.mainloop()
