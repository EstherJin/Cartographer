import argparse
import csv
import ast
import os
import os.path
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from collections import deque
from PIL import Image, ImageTk

def replace_gui(file_name, dire):
    global root, gui
    with open(file_name, encoding='utf-8-sig') as csv_file:
        csv_reader = list(csv.reader(csv_file, delimiter=','))
        rm_tp = int(csv_reader[-1][0])
        lvl = csv_reader[-3][0]
        csv_reader = csv_reader[1:]
        length = 0
        for row in csv_reader:
            length += 1
        length = length - 7
        width = 0

        for col in csv_reader[0]:
            width += 1

        del gui
        for ele in root.winfo_children():
            ele.destroy()

        gui = GUI(root, width, length, directory=dire, lev=lvl, rm_tp=rm_tp)
        for i in range(width):
            gui.wallButtonStuff(0, i, walldec=int(csv_reader[length][i]))
            gui.wallButtonStuff(2, i, walldec=int(csv_reader[length+1][i]))

        for i in range(length):
            gui.wallButtonStuff(1, i, walldec=int(csv_reader[length+2][i]))
            gui.wallButtonStuff(3, i, walldec=int(csv_reader[length+3][i]))
        gui.updateFloors(csv_reader[:length])


def tint_image(image, tint_color):
    new_img = Image.new('RGB', image.size, tint_color)
    return Image.blend(image, new_img, 0.5)

def get_image_file(image_file):
    basepath = image_file
    images = []
    with os.scandir(basepath) as entries:
        for entry in entries:
            if entry.is_file():
                images.append(entry.name.partition(".")[0])
    return images

class Cell:
    def __init__(self):
        self.tile = 1
        self.floor = 0
        self.decorator = 0
        self.hang = 0
        self.spawn = 0
        self.error1 = False
        self.error2 = False

    def modify_cell_tile(self, tile):
        self.tile = tile

    def modify_cell_decorator(self, decorator):
        self.decorator = decorator

    def modify_cell_floor(self, floor):
        self.floor = floor

    def modify_cell_hang(self, hang):
        self.hang = hang

    def modify_spawn(self):
        self.spawn = (self.spawn + 1) % 4

    def set_spawn(self, spawn):
        self.spawn = spawn

    def get_csv_code(self):
        csv_code = self.tile*1000000000+self.decorator*1000000+self.floor*1000+self.hang
        csv_code = csv_code * 10 + self.spawn
        return csv_code

class Grid:
    def __init__(self, length, width):
        self.length = length
        self.width = width
        self.grid = []
        self.wall_row = []
        self.wall_col = []
        self.stack = deque([], maxlen=25)

        for i in range(length):
            self.grid.append([])
            for j in range(width):
                self.grid[i].append(Cell())

        for i in range(2):
            row = [0] * length
            self.wall_row.append(row)
            col = [0] * width
            self.wall_col.append(col)

    def firstys(self, thing):
        return [x[:3] for x in thing]

    def secondys(self, thing):
        for action in thing:
            x = action[0]
            y = action[1]
            type = action[2]
            val = action[3]

            if type == 'T' and self.grid[x][y].tile != val:
                return False
            elif type == 'D' and self.grid[x][y].decorator != val:
                return False
            elif type == 'F'and self.grid[x][y].floor != val:
                return False
            elif type == 'H' and self.grid[x][y].hang != val:
                return False
        return True


    def add_to_stack(self, item):
        cond = False
        if len(self.stack) != 0:
            cond = (self.firstys(item) == self.firstys(self.stack[-1]) and self.secondys(item))
        if not cond:
            self.stack.append(item)

    def undo(self):
        if len(self.stack) != 0:
            item = self.stack.pop()
            for action in item:
                x = action[0]
                y = action[1]
                type = action[2]
                val = action[3]

                if type == 'T':
                    self.grid[x][y].modify_cell_tile(val)
                elif type == 'D':
                    self.grid[x][y].modify_cell_decorator(val)
                elif type == 'F':
                    self.grid[x][y].modify_cell_floor(val)
                elif type == 'H':
                    self.grid[x][y].modify_cell_hang(val)
            return x, y
        return -1, -1

    def error_check(self):
        ret_err = "No Errors :)"
        for i in range(self.length):
            for j in range(self.width):
                if self.grid[i][j].tile == 0:
                    self.grid[i][j].error2 = True
                    return True, "Incomplete Grid"

                if self.grid[i][j].tile == 1 and self.grid[i][j].decorator != 0:
                    for hor in range(max(0,j-1), min(self.width,j+2)):
                        for ver in range(max(0,i-1), min(self.length,i+2)):
                            if self.grid[ver][hor].tile == 2:
                                self.grid[ver][hor].error1 = True
                                self.grid[i][j].error1 = True
                                ret_err = "Water Obstacle Beside Land"

                if self.grid[i][j].tile == 2:
                    if i+1 < self.length and self.grid[i+1][j].tile != 2 and j-1 >= 0 and self.grid[i][j-1].tile != 2 and self.grid[i+1][j-1].tile == 2:
                        self.grid[i][j].error2 = True
                        self.grid[i+1][j-1].error2 = True
                        return True, "Unconnected Diagonal Land Tiles"

                    if i+1 < self.length and self.grid[i+1][j].tile != 2 and j+1 < self.width and self.grid[i][j+1].tile != 2 and self.grid[i+1][j+1].tile == 2:
                        self.grid[i][j].error2 = True
                        self.grid[i+1][j+1].error2 = True
                        return True, "Unconnected Diagonal Land Tiles"

                    if i-1 >= 0 and self.grid[i-1][j].tile != 2 and j-1 >= 0 and self.grid[i][j-1].tile != 2 and self.grid[i-1][j-1].tile == 2:
                        self.grid[i][j].error2 = True
                        self.grid[i-1][j-1].error2 = True
                        return True, "Unconnected Diagonal Land Tiles"

                    if i-1 >= 0 and self.grid[i-1][j].tile != 2 and j+1 < self.width and self.grid[i][j+1].tile != 2 and self.grid[i-1][j+1].tile == 2:
                        grid[i][j].error2 = True
                        grid[i-1][j+1].error2 = True
                        return True, "Unconnected Diagonal Land Tiles"

                if self.grid[i][j].tile == 1:
                    if not ((i-1 >= 0 and self.grid[i-1][j].tile == 1) or (i+1 < self.length and self.grid[i+1][j].tile == 1)):
                        self.grid[i][j].error2 = True
                        return True, "Water Channel Cannot Be 1 Wide"

                    if not ((j-1 >= 0 and self.grid[i][j-1].tile == 1) or (j+1 < self.width and self.grid[i][j+1].tile == 1)):
                        self.grid[i][j].error2 = True
                        return True, "Water Channel Cannot Be 1 Wide"

        if self.grid[0][self.width//2].tile != self.grid[0][self.width//2 -1].tile:
            self.grid[0][self.width//2].error2 = True
            self.grid[0][self.width//2 -1].error2 = True
            return True, "Door Tiles Do Not Match"
        if self.grid[self.length-1][self.width//2].tile != self.grid[self.length-1][self.width//2 -1].tile:
            self.grid[self.length-1][self.width//2].error2 = True
            self.grid[self.length-1][self.width//2 -1].error2 = True
            return True, "Door Tiles Do Not Match"
        if self.grid[self.length//2][0].tile != self.grid[self.length//2-1][0].tile:
            self.grid[self.length//2][0].error2 = True
            self.grid[self.length//2-1][0].error2 = True
            return True, "Door Tiles Do Not Match"
        if self.grid[self.length//2][self.width-1].tile != self.grid[self.length//2-1][self.width-1].tile:
            self.grid[self.length//2][self.width-1].error2 = True
            self.grid[self.length//2-1][self.width-1].error2 = True
            return True, "Door Tiles Do Not Match"

        return False, ret_err

    def to_csv(self, file_name, level, room_type):
        with open(file_name, mode='w', newline='', encoding='utf-8-sig') as output_file:
            output_writer = csv.writer(output_file, delimiter=',')
            output_writer.writerow([self.length, self.width])

            for j in range(self.width):
                row = []
                for i in range(self.length):
                    row.append(self.grid[i][j].get_csv_code())
                output_writer.writerow(row)

            top_row = []
            bot_row = []
            for i in range(self.length):
                top_row.append(self.wall_row[0][i])
                bot_row.append(self.wall_row[1][i])
            output_writer.writerow(top_row)
            output_writer.writerow(bot_row)

            l_col = []
            r_col = []
            for i in range(self.width):
                l_col.append(self.wall_col[0][i])
                r_col.append(self.wall_col[1][i])
            output_writer.writerow(l_col)
            output_writer.writerow(r_col)

            output_writer.writerow([level])
            output_writer.writerow([self.grid[self.length//2][0].tile, self.grid[self.length//2][self.width-1].tile, self.grid[0][self.width//2].tile, self.grid[self.length-1][self.width//2].tile])
            output_writer.writerow([room_type])


class GUI(tk.Frame):
    def __init__(self, parent, length, width, directory='/', lev="1", rm_tp=8):
        self.parent = parent
        w = str(max(120+32*width,600))
        h = str(210+32*length)
        self.parent.geometry(w + "x" + h)
        self.frame = tk.Frame(self.parent)
        self.length = length
        self.width = width

        spawns = get_image_file('./images/spawn')

        tiles = get_image_file('./images/tiles')
        self.tile = tk.StringVar(self.parent)
        self.tile.set(tiles[0])
        self.tile_text = tk.Label(self.parent, text="Tile:").place(x=10,y=10)
        self.tile_dropdown = tk.OptionMenu(self.parent, self.tile, "No Change", *tiles).place(x=40,y=10)

        obstacles = get_image_file('./images/obstacles')
        obstacles_cleaned = [(int(ob.split('-')[0]), ob.split('_')[0]) for ob in obstacles]
        obstacles_cleaned = sorted(obstacles_cleaned, key=lambda x: x[0])
        obstacles_cleaned = [ob[1] for ob in obstacles_cleaned]
        self.obstacle = tk.StringVar(self.parent)
        self.obstacle.set("No Change")
        self.ob_text = tk.Label(self.parent, text="Obstacle:").place(x=190,y=10)
        self.obstacle_dropdown = tk.OptionMenu(self.parent, self.obstacle, "No Change", *obstacles_cleaned).place(x=250,y=10)

        floor = get_image_file('./images/floor')
        floor_cleaned = [(int(ob.split('-')[0]), ob.split('_')[0]) for ob in floor]
        floor_cleaned = sorted(floor_cleaned, key=lambda x: x[0])
        floor_cleaned = [ob[1] for ob in floor_cleaned]
        self.floor = tk.StringVar(self.parent)
        self.floor.set("No Change")
        self.floor_text = tk.Label(self.parent, text="Floor:").place(x=10,y=50)
        self.floor_dropdown = tk.OptionMenu(self.parent, self.floor, "No Change", *floor_cleaned).place(x=50,y=50)

        hang = get_image_file('./images/hang')
        hang_cleaned = [(int(ob.split('-')[0]), ob.split('_')[0]) for ob in hang]
        hang_cleaned = sorted(hang_cleaned, key=lambda x: x[0])
        hang_cleaned = [ob[1] for ob in hang_cleaned]
        self.hang = tk.StringVar(self.parent)
        self.hang.set("No Change")
        self.hang_text = tk.Label(self.parent, text="Hang:").place(x=200,y=50)
        self.hang_dropdown = tk.OptionMenu(self.parent, self.hang, "No Change", *hang_cleaned).place(x=250,y=50)

        walldecs = get_image_file('./images/walls/decorations')
        self.walldec = tk.StringVar(self.parent)
        self.walldec.set(walldecs[0])
        self.walldec_text = tk.Label(self.parent, text="Wall:").place(x=400,y=10)
        self.walldec_dropdown = tk.OptionMenu(self.parent, self.walldec, *walldecs).place(x=430,y=10)

        self.level = tk.StringVar(self.parent)
        self.level.set(lev)
        self.level_text = tk.Label(self.parent, text="Level:").place(x=550,y=10)
        self.level_dropdown = tk.OptionMenu(self.parent, self.level, "1","2","3","4","5","6","7").place(x=590,y=10)

        room_type_list = ["1-Offering", "2-Supply", "3-Trove", "4-Treasure", "5-Trial", "6-MiniBoss", "7-Shop", "8-Combat", "9-Spawn"]
        self.room = tk.StringVar(self.parent)
        self.room.set(room_type_list[rm_tp-1])
        self.room_text = tk.Label(self.parent, text="Room:").place(x=655,y=10)
        self.level_dropdown = tk.OptionMenu(self.parent, self.room, *room_type_list).place(x=700,y=10)

        #self.dir_text = tk.Label(self.parent, text="Directory:").place(x=10,y=50)
        #self.dir_field = tk.Entry(self.parent)
        #self.dir_field.insert(-1, directory)
        #self.dir_field.place(x=70,y=50)
        self.directory = directory

        #self.new_text = tk.Label(self.parent, text="Upload File Name:").place(x=200,y=50)
        #self.new_field = tk.Entry(self.parent)
        #self.new_field.place(x=300,y=50)
        self.new_csv = tk.Button(self.parent, text='Upload CSV', command=self.upload_csv).place(x=400,y=50)

        #self.fn_text = tk.Label(self.parent, text="Save File Name:").place(x=485,y=50)
        #self.fn_field = tk.Entry(self.parent)
        #self.fn_field.place(x=575,y=50)
        self.save_csv = tk.Button(self.parent, text='Save CSV', command=self.saveys).place(x=525,y=50)
        self.error_check = tk.Button(self.parent, text='Error Check', command=self.errorCheck).place(x=650,y=50)

        self.grid = Grid(self.length,self.width)
        self.error = False

        self.canvas = tk.Canvas(root, height=100+32*width, width=110+32*length, bg='white')
        self.canvas.place(x=10,y=100)

        self.parent.wall_imgs = [None] * 8
        wall = Image.open("./images/walls/wall.png")
        corner = Image.open("./images/walls/corner.png")
        self.parent.wall_imgs[0] = wall
        for i in range(4):
            self.parent.wall_imgs[i] = ImageTk.PhotoImage(wall)
            self.parent.wall_imgs[i+4] = ImageTk.PhotoImage(corner)
            wall = wall.transpose(Image.ROTATE_90)
            corner = corner.transpose(Image.ROTATE_90)

        self.parent.walldec_imgs = [{}, {}, {}, {}]
        for w in walldecs:
            img = Image.open("./images/walls/decorations/"+ w +".png")
            for i in range(4):
                num = int(w.split('-')[0])
                self.parent.walldec_imgs[i][num] = ImageTk.PhotoImage(img)
                img = img.transpose(Image.ROTATE_90)

        self.parent.obstacle_imgs = {}
        self.obstacle_dict = {}
        for ob in obstacles:
            num = int(ob.split('-')[0])
            ob_tup = ast.literal_eval(ob.split('_')[1])
            self.obstacle_dict[num] = ob_tup

            img_file = Image.open("./images/obstacles/"+ ob +".png")
            self.parent.obstacle_imgs[num] = ImageTk.PhotoImage(img_file)

        self.parent.floor_imgs = {}
        self.floor_dict = {}
        for f in floor:
            num = int(f.split('-')[0])
            f_tup = ast.literal_eval(f.split('_')[1])
            self.floor_dict[num] = f_tup

            img_file = Image.open("./images/floor/"+ f +".png")
            self.parent.floor_imgs[num] = ImageTk.PhotoImage(img_file)

        self.parent.hang_imgs = {}
        self.hang_dict = {}
        for h in hang:
            num = int(h.split('-')[0])
            h_tup = ast.literal_eval(h.split('_')[1])
            self.hang_dict[num] = h_tup

            img_file = Image.open("./images/hang/"+ h +".png")
            self.parent.hang_imgs[num] = ImageTk.PhotoImage(img_file)

        self.parent.spawn_imgs = {}
        for spawn in spawns:
            img_file = Image.open("./images/spawn/"+ spawn +".png")
            num = int(spawn.split('-')[0])
            self.parent.spawn_imgs[num] = ImageTk.PhotoImage(img_file)

        self.parent.tile_imgs = {}
        self.parent.tile_imgs1 = {}
        self.parent.tile_imgs2 = {}
        for ti in tiles:
            num = int(ti.split('-')[0]) - 1
            img_file = Image.open("./images/tiles/"+ ti +".png")
            img_file = img_file.convert('RGB')
            self.parent.tile_imgs[num] = ImageTk.PhotoImage(img_file)
            yellow = tint_image(img_file,'yellow')
            self.parent.tile_imgs1[num] = ImageTk.PhotoImage(yellow)
            red = tint_image(img_file,'red')
            self.parent.tile_imgs2[num] = ImageTk.PhotoImage(red)

        self.wall_refs = [[],[],[],[],[]]
        self.dec_refs = [[],[],[],[]]
        corner = self.canvas.create_image(18,18, anchor="nw", image=self.parent.wall_imgs[4])
        self.wall_refs[4].append(corner)
        corner = self.canvas.create_image(18,50+(width)*32, anchor="nw", image=self.parent.wall_imgs[5])
        self.wall_refs[4].append(corner)
        corner = self.canvas.create_image(50+(length)*32,50+(width)*32, anchor="nw", image=self.parent.wall_imgs[6])
        self.wall_refs[4].append(corner)
        corner = self.canvas.create_image(50+(length)*32,18, anchor="nw", image=self.parent.wall_imgs[7])
        self.wall_refs[4].append(corner)
        for i in range(length):
            img_top = self.canvas.create_image(50+(i)*32,18, anchor="nw", image=self.parent.wall_imgs[0])
            img_bot = self.canvas.create_image(50+(i)*32,50+(width)*32, anchor="nw", image=self.parent.wall_imgs[2])
            self.wall_refs[0].append(img_top)
            self.wall_refs[2].append(img_bot)
            self.canvas.tag_bind(self.wall_refs[0][i], '<ButtonPress-1>', self.second_helper(0,i))
            self.canvas.tag_bind(self.wall_refs[2][i], '<ButtonPress-1>', self.second_helper(2,i))

            dec_top = self.canvas.create_image(50+16+(i)*32,18+25, anchor="s", image=self.parent.walldec_imgs[0][0])
            self.canvas.tag_raise(dec_top)
            self.dec_refs[0].append(dec_top)
            self.canvas.tag_bind(self.dec_refs[0][i], '<ButtonPress-1>', self.second_helper(0,i))

            dec_bot = self.canvas.create_image(50+16+(i)*32,50+(width)*32+7, anchor="n", image=self.parent.walldec_imgs[2][0])
            self.canvas.tag_raise(dec_bot)
            self.dec_refs[2].append(dec_bot)
            self.canvas.tag_bind(self.dec_refs[2][i], '<ButtonPress-1>', self.second_helper(2,i))

        self.tile_refs = []
        for i in range(length):
            self.tile_refs.append([])
            for j in range(width):
                img = self.canvas.create_image(50+(i)*32,50+(j)*32, anchor="nw", image=self.parent.tile_imgs[0])
                self.tile_refs[i].append(img)

        self.f_refs = []
        for i in range(length):
            self.f_refs.append([])
            for j in range(width):
                img = self.canvas.create_image(50+32+(i)*32,50+(j)*32, anchor="ne", image=self.parent.floor_imgs[0])
                self.canvas.tag_raise(img)
                self.f_refs[i].append(img)

        self.ob_refs = []
        for i in range(length):
            self.ob_refs.append([])
            for j in range(width):
                img = self.canvas.create_image(50+32+(i)*32,50+(j)*32, anchor="ne", image=self.parent.obstacle_imgs[0])
                self.canvas.tag_raise(img)
                self.ob_refs[i].append(img)

        self.h_refs = []
        for i in range(length):
            self.h_refs.append([])
            for j in range(width):
                img = self.canvas.create_image(50+32+(i)*32,50+32+(j)*32, anchor="se", image=self.parent.hang_imgs[0])
                self.canvas.tag_raise(img)
                self.h_refs[i].append(img)

        self.spawn_refs = []
        for i in range(length):
            self.spawn_refs.append([])
            for j in range(width):
                img = self.canvas.create_image(50+(i)*32,50+(j)*32, anchor="nw", image=self.parent.spawn_imgs[0])
                self.canvas.tag_raise(img)
                self.spawn_refs[i].append(img)

        for j in range(width):
            img_l = self.canvas.create_image(18,50+(j)*32, anchor="nw", image=self.parent.wall_imgs[1])
            img_r = self.canvas.create_image(50+(length)*32,50+(j)*32, anchor="nw", image=self.parent.wall_imgs[3])
            self.wall_refs[3].append(img_r)
            self.wall_refs[1].append(img_l)
            self.canvas.tag_bind(self.wall_refs[3][j], '<ButtonPress-1>', self.second_helper(3,j))
            self.canvas.tag_bind(self.wall_refs[1][j], '<ButtonPress-1>', self.second_helper(1,j))

            dec_r = self.canvas.create_image(18+25, 50+16+(j)*32, anchor="e", image=self.parent.walldec_imgs[1][0])
            self.canvas.tag_raise(dec_r)
            self.dec_refs[1].append(dec_r)
            self.canvas.tag_bind(self.dec_refs[1][j], '<ButtonPress-1>', self.second_helper(1,j))

            dec_l = self.canvas.create_image(50+(length)*32+7, 50+16+(j)*32, anchor="w", image=self.parent.walldec_imgs[3][0])
            self.canvas.tag_raise(dec_l)
            self.dec_refs[3].append(dec_l)
            self.canvas.tag_bind(self.dec_refs[3][j], '<ButtonPress-1>', self.second_helper(3,j))

        self.mouse_pressed = False
        self.canvas.bind("<ButtonPress-1>", self.mouseDown)
        self.canvas.bind("<ButtonRelease-1>", self.mouseUp)
        self.canvas.bind('<Motion>', self.poll)
        self.canvas.bind_all('e', self.click_spawn)
        self.canvas.bind_all('z', self.undo)
        self.canvas.bind("<ButtonPress-2>", self.erase)
        self.canvas.bind("<ButtonPress-3>", self.erase)

    def undo(self, event):
        x, y = self.grid.undo()
        if x != -1:
            self.updateGUI(x, y)

    def mouseDown(self, event):
        self.mouse_pressed = True
        self.poll(event)

    def mouseUp(self, event):
        self.mouse_pressed = False

    def poll(self, event):
        if self.mouse_pressed:
            x = event.x
            y = event.y
            realx = (x - 50) // 32
            realy = (y - 50) // 32

            if realx >= 0 and realx < self.length and  realy >= 0 and realy < self.width:
                self.buttonStuff(realx, realy)

    def click_spawn(self, event=None):
        x = event.x - 10
        y = event.y - 100
        realx = (x - 50) // 32
        realy = (y - 50) // 32

        if realx >= 0 and realx < self.length and  realy >= 0 and realy < self.width:
            self.grid.grid[realx][realy].modify_spawn()
            self.updateGUI(realx, realy)

    def erase(self, event):
        x = event.x
        y = event.y
        realx = (x - 50) // 32
        realy = (y - 50) // 32

        if realx >= 0 and realx < self.length and  realy >= 0 and realy < self.width:
            self.grid.grid[realx][realy].modify_cell_decorator(0)
            self.grid.grid[realx][realy].modify_cell_floor(0)
            self.grid.grid[realx][realy].modify_cell_hang(0)
            self.updateGUI(realx, realy)

    def upload_csv(self):
        csv_name = filedialog.askopenfilename(initialdir = self.directory, title = "Select a File", filetypes = (("CSV Files","*.csv"),("All","*.*")))
        if not csv_name:
            return
        self.directory = os.path.dirname(csv_name)
        if os.path.isfile(csv_name):
            replace_gui(csv_name, self.directory)
        else:
            messagebox.showwarning("Error", "File Not in Directory")

    def saveys(self):
        csv_name = filedialog.asksaveasfilename(initialdir = self.directory, title = "Select a File", filetypes = (("CSV Files","*.csv"),("All","*.*")))
        if not csv_name:
            return
        if not csv_name.endswith('.csv'):
            csv_name += '.csv'
        self.directory = os.path.dirname(csv_name)

        level = int(self.level.get())
        room_text = self.room.get()
        room = int(room_text.partition("-")[0])

        self.grid.to_csv(csv_name, level, room)

    def first_helper(self, i,j):
        return lambda event: self.buttonStuff(i,j)

    def second_helper(self, rot, i):
        return lambda event: self.wallButtonStuff(rot,i)

    def errorCheck(self):
        has_error, error = self.grid.error_check()
        if has_error:
            self.error = True
        messagebox.showwarning("Error Check Results", error)
        self.updateWholeGUI(False)

    def wallButtonStuff(self, rotation, i, walldec=None):
        if walldec == None:
            walldec_val = self.walldec.get()
            walldec_int = int(walldec_val.partition("-")[0])
        else:
            walldec_int = walldec

        if rotation == 0:
            self.grid.wall_row[0][i] = walldec_int
        elif rotation == 1:
            self.grid.wall_col[0][i] = walldec_int
        elif rotation == 2:
            self.grid.wall_row[1][i] = walldec_int
        elif rotation == 3:
            self.grid.wall_col[1][i] = walldec_int
        self.updateWallGUI(rotation, i)

    def updateFloors(self, array):
        tile_count = len(self.parent.tile_imgs)

        row_counter = 0
        for row in array:
            col_counter = 0
            for cell in row:
                tile_int = int(cell[0])
                ob_int = int(cell[1:4])
                f_int = int(cell[4:7])
                h_int = int(cell[7:10])
                s_int = int(cell[10])

                error = ob_int not in self.parent.obstacle_imgs.keys() or f_int not in self.parent.floor_imgs.keys() or h_int not in self.parent.hang_imgs.keys()
                if tile_int > tile_count or error or s_int > 3:
                    messagebox.showwarning("Error", "Problem importing file: Update images Folder")
                    return

                self.grid.grid[col_counter][row_counter].modify_cell_tile(tile_int)
                self.grid.grid[col_counter][row_counter].modify_cell_decorator(ob_int)
                self.grid.grid[col_counter][row_counter].modify_cell_floor(f_int)
                self.grid.grid[col_counter][row_counter].modify_cell_hang(h_int)
                self.grid.grid[col_counter][row_counter].set_spawn(s_int)

                col_counter += 1
            row_counter += 1
        self.updateWholeGUI(True)

    def buttonStuff(self, leng, wid):
        tile_val = self.tile.get()
        obstacle_val = self.obstacle.get()
        floor_val = self.floor.get()
        hang_val = self.hang.get()
        undostuffs = []

        if tile_val != "No Change":
            undostuffs.append((leng, wid, 'T', self.grid.grid[leng][wid].tile))
            tile_int = int(tile_val.partition("-")[0])
            self.grid.grid[leng][wid].modify_cell_tile(tile_int)

        if obstacle_val != "No Change":
            undostuffs.append((leng, wid, 'D', self.grid.grid[leng][wid].decorator))
            obstacle_int = int(obstacle_val.partition("-")[0])
            self.grid.grid[leng][wid].modify_cell_decorator(obstacle_int)

        if floor_val != "No Change":
            undostuffs.append((leng, wid, 'F', self.grid.grid[leng][wid].floor))
            floor_int = int(floor_val.partition("-")[0])
            self.grid.grid[leng][wid].modify_cell_floor(floor_int)

        if hang_val != "No Change":
            undostuffs.append((leng, wid, 'H', self.grid.grid[leng][wid].hang))
            h_int = int(hang_val.partition("-")[0])
            self.grid.grid[leng][wid].modify_cell_hang(h_int)

        if undostuffs:
            self.grid.add_to_stack(undostuffs)

        if self.error:
            self.error = False
            self.updateWholeGUI(True)
        else:
            self.updateGUI(leng, wid)

    def updateWallGUI(self, rotation, i):
        if rotation == 0:
            self.canvas.itemconfig(self.dec_refs[0][i], image = self.parent.walldec_imgs[0][self.grid.wall_row[0][i]])
        elif rotation == 1:
            self.canvas.itemconfig(self.dec_refs[1][i], image = self.parent.walldec_imgs[1][self.grid.wall_col[0][i]])
        elif rotation == 2:
            self.canvas.itemconfig(self.dec_refs[2][i], image = self.parent.walldec_imgs[2][self.grid.wall_row[1][i]])
        elif rotation == 3:
            self.canvas.itemconfig(self.dec_refs[3][i], image = self.parent.walldec_imgs[3][self.grid.wall_col[1][i]])
        return

    def updateGUI(self, leng, wid):
        if self.grid.grid[leng][wid].error2:
            self.canvas.itemconfig(self.tile_refs[leng][wid], image = self.parent.tile_imgs2[self.grid.grid[leng][wid].tile - 1])
        elif self.grid.grid[leng][wid].error1:
            self.canvas.itemconfig(self.tile_refs[leng][wid], image = self.parent.tile_imgs1[self.grid.grid[leng][wid].tile - 1])
        else:
            self.canvas.itemconfig(self.tile_refs[leng][wid], image = self.parent.tile_imgs[self.grid.grid[leng][wid].tile - 1])

        ob_num = self.grid.grid[leng][wid].decorator
        self.canvas.itemconfig(self.ob_refs[leng][wid], image = self.parent.obstacle_imgs[ob_num])
        ob_tup = self.obstacle_dict[ob_num]
        self.canvas.coords(self.ob_refs[leng][wid],50+32+(leng)*32+ob_tup[0],50+(wid)*32+ob_tup[1])

        f_num = self.grid.grid[leng][wid].floor
        self.canvas.itemconfig(self.f_refs[leng][wid], image = self.parent.floor_imgs[f_num])
        f_tup = self.floor_dict[f_num]
        self.canvas.coords(self.f_refs[leng][wid], 50+32+(leng)*32+f_tup[0], 50+(wid)*32+f_tup[1])

        h_num = self.grid.grid[leng][wid].hang
        self.canvas.itemconfig(self.h_refs[leng][wid], image = self.parent.hang_imgs[h_num])
        h_tup = self.hang_dict[h_num]
        self.canvas.coords(self.h_refs[leng][wid], 50+32+(leng)*32+h_tup[0], 50+32+(wid)*32+h_tup[1])

        self.canvas.itemconfig(self.spawn_refs[leng][wid], image = self.parent.spawn_imgs[self.grid.grid[leng][wid].spawn])
        return

    def updateWholeGUI(self, removeError):
        for i in range(self.length):
            for j in range(self.width):
                if removeError:
                    self.grid.grid[i][j].error1 = False
                    self.grid.grid[i][j].error2 = False
                self.updateGUI(i, j)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("length", type=int, help="length of room", default=20, nargs='?')
    parser.add_argument("width", type=int, help="width of room", default=12, nargs='?')
    args = parser.parse_args()

    global root, gui
    root = tk.Tk()
    gui = GUI(root, args.length, args.width)
    root.mainloop()
