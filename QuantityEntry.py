import tkinter as tk
import tkinter.ttk as ttk

from PIL import Image, ImageTk

import numpy as np

import threading
import time
import re

class QuantityFormat():
    default_prefix = {"m": 1e-3, "u": 1e-6, "n": 1e-9, "p": 1e-12, "f": 1e-15, "a": 1e-18, "k": 1e3, "M": 1e6, "G": 1e9, "T": 1e12}
    def __init__(self, digits_limit = (9, 9, 3), prefix = None, unit = ""):
        self.digits_limit = digits_limit
        if prefix == None:
            self.prefix = self.default_prefix
        else:
            self.prefix = prefix
        self.unit = unit
        self.re = "^([-])?([0-9]{1,%d})"%digits_limit[0]
        if digits_limit[1] != 0:
            self.re += "(\.[0-9]{1,%d})?"%digits_limit[1]
        else:
            self.re += "(SomeRandomStringThatWillNeverOccur)?"
        if self.prefix != {}:
            self.re += "([%s])?"%"".join(self.prefix.keys())
        else:
            self.re += "(AnotherRandomStringThatWillNeverOccur)?"
        if self.unit != "":
            self.re += "(%s)?$"%unit
        else:
            self.re += "(YetAnotherRandomStringThatWillNeverOccur)?$"
        self.re = re.compile(self.re)

    def match(self, str):
        result = self.re.match(str)
        if result == None:
            return None, None, None
        value = "" if result.group(1) == None else "-"
        value += result.group(2)
        value += "" if result.group(3) == None else result.group(3)
        value = float(value)
        formalized = "" if result.group(1) == None else "-"
        formalized += result.group(2)
        if result.group(3) == None:
            if self.digits_limit[2] != 0:
                formalized += "." + "0" * self.digits_limit[2]
        elif len(result.group(3)) < self.digits_limit[2] + 1:
            formalized += result.group(3) + "0" * (self.digits_limit[2] - len(result.group(3)) + 1)
        else:
            formalized += result.group(3)
        formalized += "" if result.group(4) == None else result.group(4)
        formalized += self.unit
        if result.group(4) == None:
            return result, value, formalized
        else:
            return result, value * self.prefix[result.group(4)], formalized
        
    def break_up(self, formalized):
        digits_re = re.compile("[0-9\.]+")
        digits = digits_re.findall(formalized)
        split = digits[0].split(".")
        minus = False if formalized[0] != "-" else True
        if len(split) == 1:
            integer = split[0]
            fraction = ""
        else:
            integer = split[0]
            fraction = split[1]
        return minus, integer, fraction

class QuantityEntry(tk.Text):
    def __init__(self, master = None, formater = QuantityFormat(), report = lambda x: None, **kw):
        super().__init__(master, wrap = tk.NONE, height = 1, **kw)
        self.format = formater
        self.report = report
        self.stored = ""
        self.state = "changed"
        self.result = None
        self.value = None

        self.bind("<Key>", self.handle_key)
        self.bind("<Button-1>", self.handle_button)
        self.bind("<<Selection>>", self.handle_selection)
        self.bind("<<Destroy>>", self.destroy)
    
        self.destroying = False
        self.check_thread = threading.Thread(target = self.check, args = (), daemon = True)
        self.check_thread.start()

        self.tag_config("unchanged", background = "white", foreground = "black")
        self.tag_config("changed", background = "yellow", foreground = "black")
        self.tag_config("selected", background = "black", foreground = "white")
        self.tag_config("highlight", background = "blue", foreground = "white")
        self.tag_config("disabled", background = "#d3d3d3", foreground = "black")
        
    def call(self):
        self.report()

    def set(self, str):
        self.delete("1.0", "end-1c")
        self.insert("1.0", str)

    def get_value(self):
        return self.value

    def get_text(self):
        return self.get("1.0", "end-1c")

    def check(self):
        last_state = None
        while True:
            time.sleep(0.05)
            if self.destroying:
                return
            if self.state == "unchanged" and self.get("1.0", "end-1c") != self.stored:
                self.state = "changed"
                self.tag_remove("unchanged", "1.0", "end-1c")
            if self.state == "changed":
                self.tag_add("changed", "1.0", "end-1c")
            if self["state"] != last_state:
                last_state = self["state"]
                if self["state"] == "disabled":
                    self.tag_add("disabled", "1.0", "end-1c")
                    self["bg"] = "#d3d3d3"
                else:
                    self.tag_remove("disabled", "1.0", "end-1c")
                    self["bg"] = "white"
             
    def handle_key(self, event):
        if self["state"] == "disabled":
            return "break"
        match self.state:
            case "unchanged":
                return self.unchanged_handle_key(event)
            case "changed":
                return self.changed_handle_key(event)
            case "rolling":
                return self.rolling_handle_key(event)

    def unchanged_handle_key(self, event):
        match event.keysym:
            case "Return":
                return "break"
            case "Left" | "Right":
                return self.enter_roll(event)
            case _:
                return
            
    def changed_handle_key(self, event):
        match event.keysym:
            case "Return":
                self.store()
                self.report()
                return "break"
            case "Left" | "Right":
                return "break"
            case _:
                return
            
    def rolling_handle_key(self, event):
        match event.keysym:
            case "Return":
                return self.exit_roll_key(event)
            case "Up" | "Down" | "Left" | "Right":
                return self.roll(event) 
            case "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" | "0":
                # return self.overwrite(event)
                return "break"
            case _:
                return "break"
            
    def handle_button(self, event):
        if self["state"] == "disabled":
            return "break"
        match self.state:
            case "unchanged":
                return self.unchanged_handle_button(event)
            case "changed":
                return self.changed_handle_button(event)
            case "rolling":
                return self.rolling_handle_button(event)
            
    def unchanged_handle_button(self, event):
        return
    
    def changed_handle_button(self, event):
        return
    
    def rolling_handle_button(self, event):
        return self.exit_roll_button(event)

    def handle_selection(self, event):
        if self["state"] == "disabled":
            return "break"
        match self.state:
            case "unchanged":
                self.tag_remove("highlight", "1.0", "end")
                try:
                    start = self.index("sel.first")
                    end = self.index("sel.last")
                    if self.compare(end, "==", "end") or self.get(end) == "\n":
                        self.tag_remove("sel", "end-1c", "end")
                        end = "end-1c"
                    self.tag_add("highlight", start, end)
                except:
                    pass
            case "changed":
                self.tag_remove("highlight", "1.0", "end")
                try:
                    start = self.index("sel.first")
                    end = self.index("sel.last")
                    if self.compare(end, "==", "end") or self.get(end) == "\n":
                        self.tag_remove("sel", "end-1c", "end")
                        end = "end-1c"
                    self.tag_add("highlight", start, end)
                except:
                    pass
            case "rolling":
                return
            
    def destroy(self):
        self.destroying = True

    def store(self):
        text = self.get("1.0", "end-1c")
        self.result, self.value, self.formalized = self.format.match(text)
        if self.result != None:
            self.delete("1.0", "end-1c")
            self.insert("1.0", self.formalized)
            self.stored = self.formalized
            self.state = "unchanged"
            self.tag_remove("changed", "1.0", "end-1c")
            self.tag_add("unchanged", "1.0", "end-1c")
        return "break"

    def enter_roll(self, event):
        self["insertwidth"] = 0
        self.state = "rolling"
        self.minus, self.integer, self.fraction = self.format.break_up(self.formalized)
        self.quantity = self.integer if self.fraction == "" else self.integer + "." + self.fraction
        self.tag_remove("highlight", "1.0", "end")
        if event.keysym == "Left":
            self.selected = 0
            if self.minus == False:
                self.tag_remove("unchanged", "1.0", "1.1")
                self.tag_add("selected", "1.0", "1.1")
            else:
                self.tag_remove("unchanged", "1.1", "1.2")
                self.tag_add("selected", "1.1", "1.2")
        else:
            self.selected = len(self.quantity) - 1
            if self.minus == False:
                self.tag_remove("unchanged", "1.%d"%(self.selected), "1.%d"%(self.selected + 1))
                self.tag_add("selected", "1.%d"%(self.selected), "1.%d"%(self.selected + 1))
            else:
                self.tag_remove("unchanged", "1.%d"%(self.selected + 1), "1.%d"%(self.selected + 2))
                self.tag_add("selected", "1.%d"%(self.selected + 1), "1.%d"%(self.selected + 2))
        return "break"

    def break_up(self, quantity):
        split = quantity.split(".")
        if len(split) == 1:
            return split[0], ""
        else:
            return split[0], split[1]

    def roll(self, event):
        match event.keysym, self.minus:
            case "Up", False:
                if self.quantity[self.selected] != "9":
                    self.quantity = self.quantity[:self.selected] + str(int(self.quantity[self.selected]) + 1) + self.quantity[self.selected + 1:]
                    self.delete("1.%d"%(self.selected), "1.%d"%(self.selected + 1))
                    self.insert("1.%d"%(self.selected), self.quantity[self.selected])
                    self.tag_add("selected", "1.%d"%(self.selected), "1.%d"%(self.selected + 1))
                    self.integer, self.fraction = self.break_up(self.quantity)
                elif len(self.integer) < self.format.digits_limit[0] or any(x != "9" and x != "." for x in self.quantity[:self.selected]):
                    current = self.selected
                    while (self.quantity[current] == "9" or self.quantity[current] == ".") and current >= 0:
                        if self.quantity[current] == "9":
                            self.quantity = self.quantity[:current] + "0" + self.quantity[current + 1:]
                            self.delete("1.%d"%(current), "1.%d"%(current + 1))
                            self.insert("1.%d"%(current), "0")
                        current -= 1
                    if current < 0:
                        self.quantity = "1" + self.quantity
                        self.insert("1.0", "1")
                        self.selected += 1
                    else:
                        self.quantity = self.quantity[:current] + str(int(self.quantity[current]) + 1) + self.quantity[current + 1:]
                        self.delete("1.%d"%(current), "1.%d"%(current + 1))
                        self.insert("1.%d"%(current), self.quantity[current])
                    self.tag_add("selected", "1.%d"%(self.selected), "1.%d"%(self.selected + 1))
                    self.integer, self.fraction = self.break_up(self.quantity)
                text = self.get("1.0", "end-1c")
                self.result, self.value, self.formalized = self.format.match(text)
                self.report()
            case "Down", False:
                if self.quantity[self.selected] != "0":
                    self.quantity = self.quantity[:self.selected] + str(int(self.quantity[self.selected]) - 1) + self.quantity[self.selected + 1:]
                    self.delete("1.%d"%(self.selected), "1.%d"%(self.selected + 1))
                    self.insert("1.%d"%(self.selected), self.quantity[self.selected])
                    self.tag_add("selected", "1.%d"%(self.selected), "1.%d"%(self.selected + 1))
                    self.integer, self.fraction = self.break_up(self.quantity)
                elif self.selected != 0 and any(x != "0" and x != "." for x in self.quantity[:self.selected]):
                    current = self.selected
                    while self.quantity[current] == "0" or self.quantity[current] == ".":
                        if self.quantity[current] == "0":
                            self.quantity = self.quantity[:current] + "9" + self.quantity[current + 1:]
                            self.delete("1.%d"%(current), "1.%d"%(current + 1))
                            self.insert("1.%d"%(current), "9")
                        current -= 1
                    if current == 0 and self.quantity[0] == "1" and self.quantity[1] != ".":
                        self.quantity = self.quantity[1:]
                        self.delete("1.0")
                        self.selected -= 1
                    else:
                        self.quantity = self.quantity[:current] + str(int(self.quantity[current]) - 1) + self.quantity[current + 1:]
                        self.delete("1.%d"%(current), "1.%d"%(current + 1))
                        self.insert("1.%d"%(current), self.quantity[current])
                    self.tag_add("selected", "1.%d"%(self.selected), "1.%d"%(self.selected + 1))
                    self.integer, self.fraction = self.break_up(self.quantity)
                else:
                    self.minus = True
                    self.insert("1.0", "-")
                    if self.selected != len(self.quantity) - 1 and any(x != "0" and x != "." for x in self.quantity[self.selected + 1:]):
                        new_quantity = self.quantity[:self.selected + 1]
                        for i in range(self.selected + 1, len(self.quantity)):
                            if self.quantity[i] != ".":
                                if i == len(self.quantity) - 1 or all(x == "0" or x == "." for x in self.quantity[i + 1:]):
                                    new_quantity += str(10 - int(self.quantity[i]))
                                    for j in range(i + 1, len(self.quantity)):
                                        new_quantity += "0"
                                    break
                                else:
                                    new_quantity += str(9 - int(self.quantity[i]))
                            else:
                                new_quantity += "."
                        self.quantity = new_quantity
                    else:
                        self.quantity = self.quantity[:self.selected] + "1" + self.quantity[self.selected + 1:]
                    self.delete("1.1", "1.%d"%(len(self.quantity) + 1))
                    self.insert("1.1", self.quantity)
                    self.tag_add("selected", "1.%d"%(self.selected + 1), "1.%d"%(self.selected + 2))
                    self.integer, self.fraction = self.break_up(self.quantity)
                text = self.get("1.0", "end-1c")
                self.result, self.value, self.formalized = self.format.match(text)
                self.report()
            case "Left", False:
                if self.selected > 0 and self.selected < len(self.quantity) - 1 or len(self.quantity) != 1 and self.selected == len(self.quantity) - 1 and (self.quantity[-1] != "0" or len(self.fraction) <= self.format.digits_limit[2]):
                    self.tag_remove("selected", "1.%d"%(self.selected), "1.%d"%(self.selected + 1))
                    self.tag_add("unchanged", "1.%d"%(self.selected), "1.%d"%(self.selected + 1))
                    self.selected -= 1
                    if self.quantity[self.selected] == ".":
                        self.selected -= 1
                    self.tag_remove("unchanged", "1.%d"%(self.selected), "1.%d"%(self.selected + 1))
                    self.tag_add("selected", "1.%d"%(self.selected), "1.%d"%(self.selected + 1))
                elif self.selected == 0 and self.format.digits_limit[0] > len(self.integer):
                    self.tag_remove("selected", "1.0", "1.1")
                    self.tag_add("unchanged", "1.0", "1.1")
                    self.quantity = "0" + self.quantity
                    self.integer, self.fraction = self.break_up(self.quantity)
                    self.insert("1.0", "0")
                    self.tag_add("selected", "1.0", "1.1")
                elif self.selected == len(self.quantity) - 1 and self.quantity[-1] == "0" and len(self.fraction) > self.format.digits_limit[2]:
                    self.quantity = self.quantity[:-1]
                    self.delete("1.%d"%(self.selected), "1.%d"%(self.selected + 1))
                    self.selected -= 1
                    if self.quantity[-1] == ".":
                        self.quantity = self.quantity[:-1]
                        self.delete("1.%d"%(self.selected), "1.%d"%(self.selected + 1))
                        self.selected -= 1
                    self.integer, self.fraction = self.break_up(self.quantity)
                    self.tag_remove("unchanged", "1.%d"%(self.selected), "1.%d"%(self.selected + 1))
                    self.tag_add("selected", "1.%d"%(self.selected), "1.%d"%(self.selected + 1))
            case "Right", False:
                if self.selected < len(self.quantity) - 1 and self.selected > 0 or len(self.quantity) != 1 and self.selected == 0 and (self.quantity[0] != "0" or self.integer == "0"):
                    self.tag_remove("selected", "1.%d"%(self.selected), "1.%d"%(self.selected + 1))
                    self.tag_add("unchanged", "1.%d"%(self.selected), "1.%d"%(self.selected + 1))
                    self.selected += 1
                    if self.quantity[self.selected] == ".":
                        self.selected += 1
                    self.tag_remove("unchanged", "1.%d"%(self.selected), "1.%d"%(self.selected + 1))
                    self.tag_add("selected", "1.%d"%(self.selected), "1.%d"%(self.selected + 1))
                elif self.selected == len(self.quantity) - 1 and self.format.digits_limit[1] > len(self.fraction):
                    self.tag_remove("selected", "1.%d"%(self.selected), "1.%d"%(self.selected + 1))
                    self.tag_add("unchanged", "1.%d"%(self.selected), "1.%d"%(self.selected + 1))
                    if self.fraction == "":
                        self.quantity += "."
                        self.insert("1.%d"%(self.selected + 1), ".")
                        self.selected += 1
                    self.quantity += "0"
                    self.insert("1.%d"%(self.selected + 1), "0")
                    self.selected += 1
                    self.integer, self.fraction = self.break_up(self.quantity)
                    self.tag_add("selected", "1.%d"%(self.selected), "1.%d"%(self.selected + 1))
                elif self.selected == 0 and self.quantity[0] == "0" and self.integer != "0":
                    self.quantity = self.quantity[1:]
                    self.delete("1.0", "1.1")
                    self.integer, self.fraction = self.break_up(self.quantity)
                    self.tag_remove("unchanged", "1.0", "1.1")
                    self.tag_add("selected", "1.0", "1.1")
            case "Up", True:
                if self.quantity[self.selected] != "0":
                    self.quantity = self.quantity[:self.selected] + str(int(self.quantity[self.selected]) - 1) + self.quantity[self.selected + 1:]
                    self.delete("1.%d"%(self.selected + 1), "1.%d"%(self.selected + 2))
                    self.insert("1.%d"%(self.selected + 1), self.quantity[self.selected])
                    self.tag_add("selected", "1.%d"%(self.selected + 1), "1.%d"%(self.selected + 2))
                    self.integer, self.fraction = self.break_up(self.quantity)
                    if all(x == "0" or x == "." for x in self.quantity):
                        self.minus = False
                        self.delete("1.0")  
                elif self.selected != 0 and any(x != "0" and x != "." for x in self.quantity[:self.selected]):
                    current = self.selected
                    while self.quantity[current] == "0" or self.quantity[current] == ".":
                        if self.quantity[current] == "0":
                            self.quantity = self.quantity[:current] + "9" + self.quantity[current + 1:]
                            self.delete("1.%d"%(current + 1), "1.%d"%(current + 2))
                            self.insert("1.%d"%(current + 1), "9")
                        current -= 1
                    if current == 0 and self.quantity[0] == "1" and self.quantity[1] != ".":
                        self.quantity = self.quantity[1:]
                        self.delete("1.1")
                        self.selected -= 1
                    else:
                        self.quantity = self.quantity[:current] + str(int(self.quantity[current]) - 1) + self.quantity[current + 1:]
                        self.delete("1.%d"%(current + 1), "1.%d"%(current + 2))
                        self.insert("1.%d"%(current + 1), self.quantity[current])
                    self.tag_add("selected", "1.%d"%(self.selected + 1), "1.%d"%(self.selected + 2))
                    self.integer, self.fraction = self.break_up(self.quantity)
                else:
                    self.minus = False
                    self.delete("1.0")
                    if self.selected != len(self.quantity) - 1 and any(x != "0" and x != "." for x in self.quantity[self.selected + 1:]):
                        new_quantity = self.quantity[:self.selected + 1]
                        for i in range(self.selected + 1, len(self.quantity)):
                            if self.quantity[i] != ".":
                                if i == len(self.quantity) - 1 or all(x == "0" or x == "." for x in self.quantity[i + 1:]):
                                    new_quantity += str(10 - int(self.quantity[i]))
                                    for j in range(i + 1, len(self.quantity)):
                                        new_quantity += "0"
                                    break
                                else:
                                    new_quantity += str(9 - int(self.quantity[i]))
                            else:
                                new_quantity += "."
                        self.quantity = new_quantity
                    else:
                        self.quantity = self.quantity[:self.selected] + "1" + self.quantity[self.selected + 1:]
                    self.delete("1.0", "1.%d"%len(self.quantity))
                    self.insert("1.0", self.quantity)
                    self.tag_add("selected", "1.%d"%(self.selected), "1.%d"%(self.selected + 1))
                    self.integer, self.fraction = self.break_up(self.quantity)
                text = self.get("1.0", "end-1c")
                self.result, self.value, self.formalized = self.format.match(text)
                self.report()
            case "Down", True:
                if self.quantity[self.selected] != "9":
                    self.quantity = self.quantity[:self.selected] + str(int(self.quantity[self.selected]) + 1) + self.quantity[self.selected + 1:]
                    self.delete("1.%d"%(self.selected + 1), "1.%d"%(self.selected + 2))
                    self.insert("1.%d"%(self.selected + 1), self.quantity[self.selected])
                    self.tag_add("selected", "1.%d"%(self.selected + 1), "1.%d"%(self.selected + 2))
                    self.integer, self.fraction = self.break_up(self.quantity)
                elif len(self.integer) < self.format.digits_limit[0] or any(x != "9" and x != "." for x in self.quantity[:self.selected]):
                    current = self.selected
                    while (self.quantity[current] == "9" or self.quantity[current] == ".") and current >= 0:
                        if self.quantity[current] == "9":
                            self.quantity = self.quantity[:current] + "0" + self.quantity[current + 1:]
                            self.delete("1.%d"%(current + 1), "1.%d"%(current + 2))
                            self.insert("1.%d"%(current + 1), "0")
                        current -= 1
                    if current < 0:
                        self.quantity = "1" + self.quantity
                        self.insert("1.1", "1")
                        self.selected += 1
                    else:
                        self.quantity = self.quantity[:current] + str(int(self.quantity[current]) + 1) + self.quantity[current + 1:]
                        self.delete("1.%d"%(current + 1), "1.%d"%(current + 2))
                        self.insert("1.%d"%(current + 1), self.quantity[current])
                    self.tag_add("selected", "1.%d"%(self.selected + 1), "1.%d"%(self.selected + 2))
                    self.integer, self.fraction = self.break_up(self.quantity)
                text = self.get("1.0", "end-1c")
                self.result, self.value, self.formalized = self.format.match(text)
                self.report()
            case "Left", True:
                if self.selected > 0 and self.selected < len(self.quantity) - 1 or len(self.quantity) != 1 and self.selected == len(self.quantity) - 1 and (self.quantity[-1] != "0" or len(self.fraction) <= self.format.digits_limit[2]):
                    self.tag_remove("selected", "1.%d"%(self.selected + 1), "1.%d"%(self.selected + 2))
                    self.tag_add("unchanged", "1.%d"%(self.selected + 1), "1.%d"%(self.selected + 2))
                    self.selected -= 1
                    if self.quantity[self.selected] == ".":
                        self.selected -= 1
                    self.tag_remove("unchanged", "1.%d"%(self.selected + 1), "1.%d"%(self.selected + 2))
                    self.tag_add("selected", "1.%d"%(self.selected + 1), "1.%d"%(self.selected + 2))
                elif self.selected == 0 and self.format.digits_limit[0] > len(self.integer):
                    self.tag_remove("selected", "1.1", "1.2")
                    self.tag_add("unchanged", "1.1", "1.2")
                    self.quantity = "0" + self.quantity
                    self.integer, self.fraction = self.break_up(self.quantity)
                    self.insert("1.1", "0")
                    self.tag_add("selected", "1.1", "1.2")
                elif self.selected == len(self.quantity) - 1 and self.quantity[-1] == "0" and len(self.fraction) > self.format.digits_limit[2]:
                    self.quantity = self.quantity[:-1]
                    self.delete("1.%d"%(self.selected + 1), "1.%d"%(self.selected + 2))
                    self.selected -= 1
                    if self.quantity[-1] == ".":
                        self.quantity = self.quantity[:-1]
                        self.delete("1.%d"%(self.selected + 1), "1.%d"%(self.selected + 2))
                        self.selected -= 1
                    self.integer, self.fraction = self.break_up(self.quantity)
                    self.tag_remove("unchanged", "1.%d"%(self.selected + 1), "1.%d"%(self.selected + 2))
                    self.tag_add("selected", "1.%d"%(self.selected + 1), "1.%d"%(self.selected + 2))
            case "Right", True:
                if self.selected < len(self.quantity) - 1 and self.selected > 0 or len(self.quantity) != 1 and self.selected == 0 and (self.quantity[0] != "0" or self.integer == "0"):
                    self.tag_remove("selected", "1.%d"%(self.selected + 1), "1.%d"%(self.selected + 2))
                    self.tag_add("unchanged", "1.%d"%(self.selected + 1), "1.%d"%(self.selected + 2))
                    self.selected += 1
                    if self.quantity[self.selected] == ".":
                        self.selected += 1
                    self.tag_remove("unchanged", "1.%d"%(self.selected + 1), "1.%d"%(self.selected + 2))
                    self.tag_add("selected", "1.%d"%(self.selected + 1), "1.%d"%(self.selected + 2))
                elif self.selected == len(self.quantity) - 1 and self.format.digits_limit[1] > len(self.fraction):
                    self.tag_remove("selected", "1.%d"%(self.selected + 1), "1.%d"%(self.selected + 2))
                    self.tag_add("unchanged", "1.%d"%(self.selected + 1), "1.%d"%(self.selected + 2))
                    if self.fraction == "":
                        self.quantity += "."
                        self.insert("1.%d"%(self.selected + 2), ".")
                        self.selected += 1
                    self.quantity += "0"
                    self.insert("1.%d"%(self.selected + 2), "0")
                    self.selected += 1
                    self.integer, self.fraction = self.break_up(self.quantity)
                    self.tag_add("selected", "1.%d"%(self.selected + 1), "1.%d"%(self.selected + 2))
                elif self.selected == 0 and self.quantity[0] == "0" and self.integer != "0":
                    self.quantity = self.quantity[1:]
                    self.delete("1.1", "1.2")
                    self.integer, self.fraction = self.break_up(self.quantity)
                    self.tag_remove("unchanged", "1.1", "1.2")
                    self.tag_add("selected", "1.1", "1.2")
        return "break"

    def overwrite(self, event):
        self.quantity = self.quantity[:self.selected] + event.char + self.quantity[self.selected + 1:]
        if self.minus == False:
            self.delete("1.%d"%(self.selected), "1.%d"%(self.selected + 1))
            self.insert("1.%d"%(self.selected), event.char)
        else:
            self.delete("1.%d"%(self.selected + 1), "1.%d"%(self.selected + 2))
            self.insert("1.%d"%(self.selected + 1), event.char)
        if self.selected != len(self.quantity) - 1:
            self.selected += 1
            if self.quantity[self.selected] == ".":
                self.selected += 1
        elif len(self.fraction) == 0:
            self.quantity += ".0"
            self.insert("1.%d"%(self.selected + 1), ".0")
            self.selected += 2
        elif len(self.fraction) < self.format.digits_limit[1]:
            self.quantity += "0"
            self.insert("1.%d"%(self.selected + 1), "0")
            self.selected += 1
        if self.minus == False:
            self.tag_add("selected", "1.%d"%(self.selected), "1.%d"%(self.selected + 1))
        else:
            self.tag_add("selected", "1.%d"%(self.selected + 1), "1.%d"%(self.selected + 2))
        self.integer, self.fraction = self.break_up(self.quantity)
        self.result, self.value, self.formalized = self.format.match(self.get("1.0", "end-1c"))
        self.report()
        return "break"

    def exit_roll_key(self, event):
        self["insertwidth"] = 1
        self.state = "unchanged"
        self.tag_remove("selected", "1.0", "end-1c")
        self.tag_add("unchanged", "1.0", "end-1c")
        self.store()
        self.report()
        return "break"
    
    def exit_roll_button(self, event):
        self["insertwidth"] = 1
        self.state = "unchanged"
        self.tag_remove("selected", "1.0", "end-1c")
        self.tag_add("unchanged", "1.0", "end-1c")
        self.store()
        self.report()
        return