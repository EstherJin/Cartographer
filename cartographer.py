import csv
import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

def tint_image(image, tint_color):
    new_img = Image.new('RGB', image.size, tint_color)
    return Image.blend(image, new_img, 0.5)

def get_tiles():
    basepath = './images/tiles'
    tiles = []
    with os.scandir(basepath) as entries:
        for entry in entries:
            if entry.is_file():
                tiles.append(entry.name.partition(".")[0])
    return tiles

def get_obstacles():
    basepath = './images/obstacles'
    obstacles = []
    with os.scandir(basepath) as entries:
        for entry in entries:
            if entry.is_file():
                obstacles.append(entry.name.partition(".")[0])
    return obstacles

def get_walldecs():
    basepath = './images/walls/decorations'
    walldecs = []
    with os.scandir(basepath) as entries:
        for entry in entries:
            if entry.is_file():
                walldecs.append(entry.name.partition(".")[0])
    return walldecs

class Cell:
    def __init__(self):
        self.tile = 1
        self.decorator = 0
        self.error1 = False
        self.error2 = False

    def modify_cell_tile(self, tile):
        self.tile = tile

    def modify_cell_decorator(self, decorator):
        self.decorator = decorator

    def get_csv_code(self):
        return self.tile*1000+self.decorator

class Grid:
    def __init__(self, length, width):
        self.length = length
        self.width = width
        self.grid = []
        self.wall_row = []
        self.wall_col = []

        for i in range(length):
            self.grid.append([])
            for j in range(width):
                self.grid[i].append(Cell())

        for i in range(2):
            row = [0] * length
            self.wall_row.append(row)
            col = [0] * width
            self.wall_col.append(col)

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
        with open(file_name, mode='w', newline='') as output_file:
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
            output_writer.writerow([self.grid[0][self.width//2].tile, self.grid[self.length-1][self.width//2].tile, self.grid[self.length//2][0].tile, self.grid[self.length//2][self.width-1].tile])
            output_writer.writerow([room_type])


class GUI(tk.Frame):
    def __init__(self, parent, length, width):
        self.parent = parent
        w = str(max(120+32*width,600))
        h = str(210+32*length)
        self.parent.geometry(w + "x" + h)
        self.frame = tk.Frame(self.parent)
        self.length = length
        self.width = width

        tiles = get_tiles()
        self.tile = tk.StringVar(self.parent)
        self.tile.set(tiles[0])
        self.tile_text = tk.Label(self.parent, text="Tile:").place(x=10,y=10)
        self.tile_dropdown = tk.OptionMenu(self.parent, self.tile, "No Change", *tiles).place(x=40,y=10)

        obstacles = get_obstacles()
        self.obstacle = tk.StringVar(self.parent)
        self.obstacle.set(obstacles[0])
        self.ob_text = tk.Label(self.parent, text="Obstacle:").place(x=190,y=10)
        self.obstacle_dropdown = tk.OptionMenu(self.parent, self.obstacle, "No Change", *obstacles).place(x=250,y=10)

        walldecs = get_walldecs()
        self.walldec = tk.StringVar(self.parent)
        self.walldec.set(walldecs[0])
        self.walldec_text = tk.Label(self.parent, text="Wall:").place(x=400,y=10)
        self.walldec_dropdown = tk.OptionMenu(self.parent, self.walldec, *walldecs).place(x=430,y=10)

        self.fn_text = tk.Label(self.parent, text="File Name:").place(x=10,y=50)
        self.fn_field = tk.Entry(self.parent)
        self.fn_field.place(x=70,y=50)
        self.save_csv = tk.Button(self.parent, text='Save As CSV', command=self.saveys).place(x=170,y=50)
        self.error_check = tk.Button(self.parent, text='Error Check', command=self.errorCheck).place(x=260,y=50)

        self.level = tk.StringVar(self.parent)
        self.level.set("1")
        self.level_text = tk.Label(self.parent, text="Level:").place(x=350,y=50)
        self.level_dropdown = tk.OptionMenu(self.parent, self.level, "1","2","3","4","5","6","7").place(x=390,y=50)

        room_type_list = ["1-Offering", "2-Supply", "3-Trove", "4-Treasure", "5-Trial", "6-MiniBoss", "7-Shop", "8-Combat", "9-Spawn"]
        self.room = tk.StringVar(self.parent)
        self.room.set(room_type_list[0])
        self.room_text = tk.Label(self.parent, text="Room:").place(x=455,y=50)
        self.level_dropdown = tk.OptionMenu(self.parent, self.room, *room_type_list).place(x=500,y=50)

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

        self.parent.walldec_imgs = [[], [], [], []]
        for w in walldecs:
            img = Image.open("./images/walls/decorations/"+ w +".png")
            for i in range(4):
                self.parent.walldec_imgs[i].append(ImageTk.PhotoImage(img))
                img = img.transpose(Image.ROTATE_90)

        self.parent.obstacle_imgs = []
        for ob in obstacles:
            img_file = Image.open("./images/obstacles/"+ ob +".png")
            self.parent.obstacle_imgs.append(ImageTk.PhotoImage(img_file))

        self.parent.tile_imgs = []
        self.parent.tile_imgs1 = []
        self.parent.tile_imgs2 = []
        for ti in tiles:
            img_file = Image.open("./images/tiles/"+ ti +".png")
            img_file = img_file.convert('RGB')
            self.parent.tile_imgs.append(ImageTk.PhotoImage(img_file))
            yellow = tint_image(img_file,'yellow')
            self.parent.tile_imgs1.append(ImageTk.PhotoImage(yellow))
            red = tint_image(img_file,'red')
            self.parent.tile_imgs2.append(ImageTk.PhotoImage(red))

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
                self.canvas.tag_bind(self.tile_refs[i][j], '<ButtonPress-1>', self.first_helper(i,j))

        self.ob_refs = []
        for i in range(length):
            self.ob_refs.append([])
            for j in range(width):
                img = self.canvas.create_image(50+16+(i)*32,50+25+(j)*32, anchor="s", image=self.parent.obstacle_imgs[0])
                self.canvas.tag_raise(img)
                self.ob_refs[i].append(img)
                self.canvas.tag_bind(self.ob_refs[i][j], '<ButtonPress-1>', self.first_helper(i,j))

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

    def saveys(self):
        csv_name = self.fn_field.get()
        if csv_name == '':
            csv_name = 'dungeon_level'
        csv_name += '.csv'

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

    def wallButtonStuff(self, rotation, i):
        walldec_val = self.walldec.get()
        walldec_int = int(walldec_val.partition("-")[0])
        if rotation == 0:
            self.grid.wall_row[0][i] = walldec_int
        elif rotation == 1:
            self.grid.wall_col[0][i] = walldec_int
        elif rotation == 2:
            self.grid.wall_row[1][i] = walldec_int
        elif rotation == 3:
            self.grid.wall_col[1][i] = walldec_int
        self.updateWallGUI(rotation, i)

    def buttonStuff(self, leng, wid):
        tile_val = self.tile.get()
        obstacle_val = self.obstacle.get()

        if tile_val != "No Change":
            tile_int = int(tile_val.partition("-")[0])
            self.grid.grid[leng][wid].modify_cell_tile(tile_int)

        if obstacle_val != "No Change":
            obstacle_int = int(obstacle_val.partition("-")[0])
            self.grid.grid[leng][wid].modify_cell_decorator(obstacle_int)

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

        self.canvas.itemconfig(self.ob_refs[leng][wid], image = self.parent.obstacle_imgs[self.grid.grid[leng][wid].decorator])
        return

    def updateWholeGUI(self, removeError):
        for i in range(self.length):
            for j in range(self.width):
                if removeError:
                    self.grid.grid[i][j].error1 = False
                    self.grid.grid[i][j].error2 = False
                self.updateGUI(i, j)


if __name__ == "__main__":
    root = tk.Tk()
    GUI(root,20,12)
    root.mainloop()
