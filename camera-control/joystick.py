import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo

import serial

from CameraControll import menuPressButton, setMenu


class App(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.dev_name = "/dev/pts/12"

        try:

            self.serial_connection = serial.Serial(
                port=self.dev_name,
                baudrate=9600,
                parity=serial.PARITY_NONE,
                bytesize=serial.EIGHTBITS,
                stopbits=serial.STOPBITS_ONE,
                timeout=1)

        except Exception:
            print(
                f"Could not connect to device: {self.dev_name}, no commands will be sent"
            )
            self.serial_connection = None

        self.master = master

        self.menu_active = False

        self.toggle_menu(False)

        self.up = tk.Button(padx=30,
                            pady=30,
                            text="Up",
                            command=self.menu_send("up"))
        self.down = tk.Button(padx=30,
                              pady=30,
                              text="Down",
                              command=self.menu_send("down"))
        self.left = tk.Button(padx=30,
                              pady=30,
                              text="Left",
                              command=self.menu_send("left"))
        self.right = tk.Button(padx=30,
                               pady=30,
                               text="Right",
                               command=self.menu_send("right"))
        self.enter = tk.Button(padx=30,
                               pady=30,
                               text="Enter",
                               command=self.menu_send("ok"))

        self.menu = tk.Button(padx=30,
                               pady=30,
                               text="Toggle menu",
                               command=self.toggle_menu)

        self.esc = tk.Button(padx=30,
                             pady=30,
                             text="Esc",
                             command=self.menu_send("cancel"))

        help_text = "You can either use the displayed controlls or just use your keboard:\n Move with arrow keys, accept with \"enter\", cancel with \"esc\" key."
        self.info_button = tk.Button(padx=30,
                                     pady=30,
                                     text="Help",
                                     command=self.show_popup(
                                         "Help", help_text))

        self.up.grid(row=0, column=1)
        self.down.grid(row=2, column=1)
        self.left.grid(row=1, column=0)
        self.right.grid(row=1, column=2)
        self.enter.grid(row=4, column=0)
        self.esc.grid(row=4, column=1)
        self.info_button.grid(row=4, column=2)
        self.menu.grid(row=4, column=3)

        # Define a callback for when the user hits return.
        # It prints the current value of the variable.
        self.master.bind('<Key-Up>', self.menu_send("up"))
        self.master.bind('<Key-Down>', self.menu_send("down"))
        self.master.bind('<Key-Left>', self.menu_send("left"))
        self.master.bind('<Key-Right>', self.menu_send("right"))
        self.master.bind('<Key-Return>', self.menu_send("ok"))
        self.master.bind('<Key-Escape>', self.menu_send("cancel"))

    def menu_send(self, code):
        return lambda event=None: menuPressButton(self.serial_connection, code)

    def toggle_menu(self, setting=None):
        setting = setting if setting else not self.menu_active
        setMenu(self.serial_connection, "on" if setting else "off")
        self.menu_active = setting

    def show_popup(self, title, content):
        return lambda event=None: showinfo(title, content)


if __name__ == '__main__':
    root = tk.Tk()
    root.title("Remote joystick")
    style = ttk.Style(root)

    try:
        style.theme_use("vista")
    except Exception:
        print("Theme vista not found going back to default theme")

    myapp = App(root)

    myapp.mainloop()
