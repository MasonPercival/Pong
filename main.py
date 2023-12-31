import tkinter as tk

class Game(tk.Frame):
  
    def __init__(self, master):
       
        tk.Frame.__init__(self, master)
        self.lives = 3
        self.width = 610
        self.height = 400
       
        self.canvas = tk.Canvas(self, bg='#aaaaff', width=self.width,
                                height=self.height)

       
        self.canvas.pack()
        self.pack()

        self.items = {}
        self.ball = None
        self._paddle_y_start = 326
        self.paddle = Paddle(self.canvas, self.width / 2, self._paddle_y_start)

       
        self.items[self.paddle.item] = self.paddle

       
        for x in range(5, self.width - 5, 75):  
            self.add_brick(x + 37.5, 50, 2)
            self.add_brick(x + 37.5, 70, 1)
            self.add_brick(x + 37.5, 90, 1)
            self.add_brick(x + 37.5, 110, 1)

        self.hud = None

      
        self.setup_game()

       
        self.canvas.focus_set()  

        self.canvas.bind('<Left>', lambda _: self.paddle.move(-10))
        self.canvas.bind('<Right>', lambda _: self.paddle.move(10))

    def setup_game(self):
  
        self.add_ball()
        self.update_lives_text()
        self.text = self.draw_text(300, 200, "Press Spacebar to start")

        self.canvas.bind('<space>', lambda _: self.start_game())

    def add_ball(self):

        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position()

        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        self.ball = Ball(self.canvas, x, 310)
        self.paddle.set_ball(self.ball)  

    def add_brick(self, x, y, hits):
    


        brick = Brick(self.canvas, x, y, hits)
       
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, size='40'):
  
        font = ('Helvetica', size)
        return self.canvas.create_text(x, y, text=text, font=font)

    def update_lives_text(self):

        text = "Lives: {}".format(self.lives)
        if self.hud is None:
            self.hud = self.draw_text(50, 20, text, 15)
        else:
            self.canvas.itemconfig(self.hud, text=text)

    def start_game(self):
 
        self.canvas.unbind('<space>')
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.game_loop()

    def game_loop(self):
    
        self.check_collisions()
  
        num_bricks = len(self.canvas.find_withtag('brick'))
        if num_bricks == 0:
            self.ball.speed = None
            self.draw_text(300, 200, "You've won!")
        elif self.ball.get_position()[3] >= self.height:
           
            self.ball.speed = None
            self.lives -= 1
            if self.lives < 0:
                self.draw_text(300, 200, "Game Over")
            else:
                self.after(1000, self.setup_game)
        else:
            self.ball.update()  
      
            self.after(50, self.game_loop)

    def check_collisions(self):
      


       
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords) # list
       
        collideables = [self.items[x] for x in items if x in self.items]
        self.ball.collide(collideables)


class GameObject():
    
    def __init__(self, canvas, item):
   
        self.canvas = canvas
        self.item = item

    def get_position(self):
     
        return self.canvas.coords(self.item)

    def move(self, x, y):
        
        self.canvas.move(self.item, x, y)

    def delete(self):
      
        self.canvas.delete(self.item)


class Ball(GameObject):
 
    def __init__(self, canvas, x, y):
        
        self.radius = 10
        self.direction = [1, -1]  
        self.speed = 10

    
        item = canvas.create_oval(x - self.radius, y - self.radius,
                                  x + self.radius, y + self.radius,
                                  fill='white')
        
        GameObject.__init__(self, canvas, item)

    def update(self):
        

 
        ball_coords = self.get_position()
        width = self.canvas.winfo_width()

        if ball_coords[0] <= 0 or ball_coords[2] >= width:
            self.direction[0] *= -1  
        if ball_coords[1] <= 0:
            self.direction[1] *= -1  
        x = self.direction[0] * self.speed  
        y = self.direction[1] * self.speed
        self.move(x, y) 


    def collide(self, game_objects):

        ball_coords = self.get_position()
        ball_center_x = (ball_coords[0] + ball_coords[2]) * 0.5  

        if len(game_objects) > 1: 
            self.direction[1] *= -1
        elif len(game_objects) == 1:  
            game_object = game_objects[0]
            coords = game_object.get_position()
            if ball_center_x > coords[2]:
                self.direction[0] = 1
            elif ball_center_x < coords[0]:
                self.direction[0] = -1
            else:
                self.direction[1] *= -1
       
        for game_object in game_objects:
            if isinstance(game_object, Brick):
                game_object.hit() 


class Paddle(GameObject):
  
    def __init__(self, canvas, x, y):
      
        self.width = 80
        self.height = 10
        self.ball = None

      
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill='blue')
     
        GameObject.__init__(self, canvas, item)

    def set_ball(self, ball):
       
        self.ball = ball

    def move(self, offset):
       
        coords = self.get_position()  
        width = self.canvas.winfo_width()
       
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            GameObject.move(self, offset, 0)  
           
            if self.ball is not None:
                self.ball.move(offset, 0)  


class Brick(GameObject):
   
    COLORS = {1: '#999999', 2: '#555555', 3: '#222222'}

    def __init__(self, canvas, x, y, hits):
       
        self.width = 75
        self.height = 20
        self.hits = hits
        color = Brick.COLORS[hits]

    
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=color, tags='brick')
       
        GameObject.__init__(self, canvas, item)

    def hit(self):
       
        self.hits -= 1
        if self.hits == 0:
            self.delete()  
        else: 
            self.canvas.itemconfig(self.item, fill=Brick.COLORS[self.hits])



if __name__ == "__main__":
   
    ROOT = tk.Tk()
    ROOT.title('Tkinter Breakout')
   
    GAME = Game(ROOT)
    GAME.mainloop()
