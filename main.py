import tkinter as tk
from PIL import Image, ImageTk


class Road:
    def __init__(self, parent, position, thickness, location, direction):
        self.__width_screen = parent.winfo_width()
        self.__height_screen = parent.winfo_height()
        self.__thickness = thickness
        self.__position = position
        self.__size = (0, 0)
        self.__location = location
        self.__frame = tk.Canvas(parent, bg="#292724", highlightthickness=0)
        self.__cars = []
        self.__direction = direction

    @property
    def location(self):
        return self.__location

    @property
    def frame(self):
        return self.__frame

    @property
    def size(self):
        return self.__size

    @property
    def position(self):
        return self.__position

    def state_car(self, id_car, state):
        self.__cars[id_car].state = state

    def get_cars(self):
        return self.__cars

    def render(self):
        position_now = (0, 0)
        if self.__location == "horizontal":
            position_now = (0, self.__position[1] - self.__thickness // 2)
            self.__size = (self.__width_screen, self.__thickness)
        elif self.__location == "vertical":
            position_now = (self.__position[0] - self.__thickness // 2, 0)
            self.__size = (self.__thickness, self.__height_screen)
        self.__position = position_now
        self.__frame.place(x=position_now[0], y=position_now[1], width=self.__size[0], height=self.__size[1])

    def create_car(self, size):
        car = Car(self, "car.png", size, self.__direction)
        self.__cars.append(car)
        self.__cars = self.__cars[::-1]
        car.create()

    def update_road(self):
        if len(self.__cars) > 0:
            for car in self.__cars:
                car.move()
                self.destroy_car(car)

    def destroy_car(self, car):
        if car.position[0] < 0 and self.__direction[0] == -1:
            car.destroy()
            self.__cars.remove(car)
        elif car.position[0] > self.__size[0] and self.__direction[0] == 1:
            car.destroy()
            self.__cars.remove(car)
        elif car.position[1] < 0 and self.__direction[1] == -1:
            car.destroy()
            self.__cars.remove(car)
        elif car.position[1] > self.__size[1] and self.__direction[1] == 1:
            car.destroy()
            self.__cars.remove(car)


class Crossroad:
    def __init__(self, parent, *roads):
        self.__roads = roads
        self.__vertical_road = list(filter(lambda x: x.location == "vertical", self.__roads))[0]
        self.__horizontal_road = list(filter(lambda x: x.location == "horizontal", self.__roads))[0]
        self.__chunk = 50
        self.__position = self.__set_position()
        self.__size = self.__set_size()
        self.__lights = {}
        self.__parent = parent

    def create_lights(self, position, size, location):
        lights = Lights(self.__parent, self, position, size, location)
        self.__lights[position] = lights

    @property
    def position(self):
        return self.__position

    @property
    def size(self):
        return self.__size

    @property
    def chunk(self):
        return self.__chunk

    def __set_position(self):
        x = self.__vertical_road.position[0] - self.__chunk
        y = self.__horizontal_road.position[1] - self.__chunk
        return x, y

    def __set_size(self):
        return self.__vertical_road.size[0] + self.__chunk * 2, self.__horizontal_road.size[1] + self.__chunk * 2

    def render(self):
        if len(self.__lights) > 0:
            for lights in self.__lights:
                self.__lights[lights].render()

    def switch_state_car(self, car):
        light = None
        light_hor = list(filter(lambda x: x.location == "horizontal", self.__lights.values()))
        light_ver = list(filter(lambda x: x.location == "vertical", self.__lights.values()))
        if car.direction[0] != 0:
            for light in light_hor:
                side_n = light if light.side == f"n{car.side()}" else False
                side_s = light if light.side == f"s{car.side()}" else False
                light = side_n if side_n else side_s
        elif car.direction[1] != 0:
            for light in light_ver:
                side_w = light if light.side == f"{car.side()}w" else False
                side_e = light if light.side == f"{car.side()}e" else False
                light = side_w if side_w else side_e
        if light.state in ("go", "get_ready"):
            car.state = "run"
        elif light.state == "stop":
            car.state = "stop"

    def collision_car_crossroad(self):
        horizontal_cars = self.__horizontal_road.get_cars()
        vertical_cars = self.__vertical_road.get_cars()
        cars_collision = []
        for car in horizontal_cars + vertical_cars:
            if car.direction[0] == 1:
                if self.__position[0] < car.position[0] + car.size[0] < self.__position[0] + self.__size[0]:
                    cars_collision.append(car)
            if car.direction[0] == -1:
                if self.__position[0] + self.__size[0] > car.position[0] > self.__position[0]:
                    cars_collision.append(car)
            if car.direction[1] == 1:
                if self.__position[1] + self.__size[1] > car.position[1] + car.size[1] > self.__position[1]:
                    cars_collision.append(car)
            if car.direction[1] == -1:
                if self.__position[1] < car.position[1] < self.__position[1] + self.__size[1]:
                    cars_collision.append(car)
        return cars_collision


class Light:
    def __init__(self, parent, size, bg, position):
        self.__light = tk.Button(parent, bg=bg,)
        self.__light.place(x=position[0], y=position[1], width=size[0], height=size[1])

    @property
    def light(self):
        return self.__light


class Lights:
    def __init__(self, parent, crossroad, position, size, location):
        self.__crossroad = crossroad
        self.__location = location
        self.__size = self.__set_size(size)
        self.__side = position
        self.__position = self.__set_position(position)
        self.__frame = tk.Frame(parent)
        self.__state = "stop"
        self.__light = []
        self.__color = self.__set_color()

    @property
    def location(self):
        return self.__location

    @property
    def state(self):
        return self.__state

    @property
    def side(self):
        return self.__side

    @state.setter
    def state(self, val):
        self.__state = val
        self.__color = self.__set_color()

    def __set_position(self, position):
        position_coord = [0, 0]

        position_crossroad = self.__crossroad.position
        chunk = self.__crossroad.chunk
        if self.__location == "horizontal":
            if position == "nw":
                position_coord = (position_crossroad[0] - self.__size[0] // 2,
                                  position_crossroad[1] + self.__size[1] // 2)
            elif position == "sw":
                position_coord = (position_crossroad[0] - self.__size[0] // 2,
                                  position_crossroad[1] + self.__crossroad.size[1] - chunk + self.__size[1] // 2)
            elif position == "ne":
                position_coord = (position_crossroad[0] + self.__crossroad.size[0] - self.__size[0] // 2,
                                  position_crossroad[1] + self.__size[1] // 2)
            elif position == "se":
                position_coord = (position_crossroad[0] + self.__crossroad.size[0] - self.__size[0] // 2,
                                  position_crossroad[1] + self.__crossroad.size[1] - chunk + self.__size[1] // 2)

        elif self.__location == "vertical":
            if position == "nw":
                position_coord = [position_crossroad[0] + self.__size[0] // 2,
                                  position_crossroad[1] - self.__size[1] // 2]
            elif position == "sw":
                position_coord = (position_crossroad[0] + self.__size[0] // 2,
                                  position_crossroad[1] + self.__crossroad.size[1] - chunk + self.__size[1] // 2)
            elif position == "ne":
                position_coord = (position_crossroad[0] + self.__crossroad.size[0] - chunk + self.__size[0] // 2,
                                  position_crossroad[1] - self.__size[1] // 2)
            elif position == "se":
                position_coord = (position_crossroad[0] + self.__crossroad.size[0] - chunk + self.__size[0] // 2,
                                  position_crossroad[1] + self.__crossroad.size[1] - chunk + self.__size[1] // 2)

        return position_coord

    def __set_size(self, size):
        if self.__location == "horizontal":
            return size[::-1]
        elif self.__location == "vertical":
            return size

    def switch_light(self, event):
        widget = event.widget["bg"]
        if widget == "#0b6b0a":
            self.state = "go"
        elif widget == "#825f00":
            self.state = "get_ready"
        elif widget == "#8a0101":
            self.state = "stop"
        self.render()

    def render(self):
        size_light = (0, 0)
        position = (0, 0)

        if self.__location == "horizontal":
            size_light = (self.__size[0] // 3, self.__size[1])
            position = (size_light[0], 0)
        elif self.__location == "vertical":
            size_light = (self.__size[0], self.__size[1] // 3)
            position = (0, size_light[1])
        for i in range(3):
            light = Light(self.__frame, size_light, self.__color[i], (position[0] * i, position[1] * i))
            light.light.bind("<Button-1>", self.switch_light)
            self.__light.append(light)
        self.__frame.place(x=self.__position[0], y=self.__position[1], width=self.__size[0], height=self.__size[1])

    def __set_color(self):
        if self.__state == "stop":
            return ["#0b6b0a", "#825f00", "#ff0000"]
        elif self.__state == "get_ready":
            return ["#0b6b0a", "#ffe600", "#8a0101"]
        elif self.__state == "go":
            return ["#12d40f", "#825f00", "#8a0101"]


class Car:
    def __init__(self, parent, file_name, size, direction):
        self.__size = size
        self.__direction = direction
        self.__image_car = Image.open(file_name).resize(self.__size, Image.ANTIALIAS)
        self.__position = None
        self.__object = None
        self.__road = parent
        self.__tkinter_image = None
        self.__state = "run"

    @property
    def position(self):
        return self.__position

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, val):
        self.__state = val

    @property
    def direction(self):
        return self.__direction

    def side(self):
        if self.__direction[0] == 1:
            return "e"
        elif self.__direction[0] == -1:
            return "w"
        elif self.__direction[1] == 1:
            return "s"
        elif self.__direction[1] == -1:
            return "n"

    @property
    def size(self):
        return self.__size

    def create(self):
        if self.__direction[0] == 1 or self.__direction[1] == -1:
            self.__image_car = self.__image_car.transpose(Image.FLIP_LEFT_RIGHT)

        if self.__road.location == "vertical":
            self.__position = [25, 100]
            self.__image_car = self.__image_car.rotate(90, expand=True)

        elif self.__road.location == "horizontal":
            self.__position = [100, 25]

        self.__tkinter_image = ImageTk.PhotoImage(self.__image_car)
        self.__object = self.__road.frame.create_image(self.__position[0], self.__position[1],
                                                       image=self.__tkinter_image)
        self.__road.frame.update()

    def destroy(self):
        self.__road.frame.delete(self.__object)
        self.__road.frame.update()

    def run(self):
        self.__position[0] += 1 * self.__direction[0]
        self.__position[1] += 1 * self.__direction[1]
        self.__road.frame.move(self.__object, self.__direction[0], self.__direction[1])
        self.__road.frame.update()

    def move(self):
        if self.__state == "run":
            self.run()
        elif self.__state == "stop":
            self.stop()
        self.__road.frame.update()

    def stop(self):
        self.__road.frame.move(self.__object, 0, 0)


window_root = tk.Tk()
height = 500
width = 500
window_root.geometry(f"{height}x{width}+{height}+{width}")
window_root.title("test")
window_root.resizable(False, False)
window_root.config(bg="#de830b")
window_root.update()

objects = {}
objects["road_hor"] = Road(window_root, (0, 350), 50, "horizontal", (1, 0))
objects["road_ver"] = Road(window_root, (250, 0), 50, "vertical", (0, 1))
objects["cross_road"] = Crossroad(window_root, objects["road_hor"], objects["road_ver"])
objects["cross_road"].create_lights("ne", (20, 60), "horizontal")
objects["cross_road"].create_lights("sw", (20, 60), "vertical")

for object_tk in objects:
    objects[object_tk].render()


def main_events():
    for object_tk in objects:
        if isinstance(objects[object_tk], Road):
            objects[object_tk].update_road()
        if object_tk == "cross_road":
            cars = objects[object_tk].collision_car_crossroad()
            if len(cars) != 0:
                for car in cars:
                    objects[object_tk].switch_state_car(car)
    window_root.after(10, main_events)


def create(event):
    if event.char == "b":
        objects["road_hor"].create_car((80, 50))
    elif event.char == "h":
        objects["road_ver"].create_car((80, 50))


window_root.bind("<Key>", create)
main_events()


window_root.mainloop()
