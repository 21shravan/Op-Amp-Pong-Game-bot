import tkinter as tk
import time
import csv
import os
import sys
try:
    import serial
except Exception:
    serial = None

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
PADDLE_WIDTH = 10
PADDLE_HEIGHT = 100
BALL_SIZE = 20
PADDLE_SPEED = 10
# slowed ball speeds
BALL_SPEED_X = 10
BALL_SPEED_Y = 10
# frame delay in ms (slower update)
FRAME_DELAY = 50

# open serial port COM3 at 115200 if available
ser = None
if serial is not None:
    try:
        ser = serial.Serial('COM3', 115200, timeout=0.1)
        time.sleep(2)
        print('Serial COM3 opened at 115200')
    except Exception as e:
        print(f"Warning: could not open COM3: {e}", file=sys.stderr)

class Paddle:
    def __init__(self, canvas, x, y, color):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.color = color
        self.id = self.canvas.create_rectangle(
            self.x,
            self.y,
            self.x + self.width,
            self.y + self.height,
            fill=self.color,
        )

    def move(self, dy):
        new_y = self.y + dy
        if new_y < 0:
            new_y = 0
        elif new_y + self.height > WINDOW_HEIGHT:
            new_y = WINDOW_HEIGHT - self.height
        self.y = new_y
        self.canvas.coords(self.id, self.x, self.y, self.x + self.width, self.y + self.height)


class Ball:
    def __init__(self, canvas, x, y, size, color):
        self.canvas = canvas
        self.size = size
        self.reset(x, y)
        self.id = self.canvas.create_oval(
            self.x,
            self.y,
            self.x + self.size,
            self.y + self.size,
            fill=color,
        )

    def reset(self, x, y):
        self.x = x
        self.y = y
        self.vx = BALL_SPEED_X
        self.vy = BALL_SPEED_Y

    def update(self):
        self.x += self.vx
        self.y += self.vy

        if self.y <= 0 or self.y + self.size >= WINDOW_HEIGHT:
            self.vy = -self.vy

        self.canvas.coords(self.id, self.x, self.y, self.x + self.size, self.y + self.size)

    def bounce_x(self):
        self.vx = -self.vx

    def bounce_y(self):
        self.vy = -self.vy


class Scoreboard:
    def __init__(self, canvas):
        self.canvas = canvas
        self.left_score = 0
        self.right_score = 0
        self.id = self.canvas.create_text(
            WINDOW_WIDTH // 2,
            40,
            text=self.score_text,
            fill="white",
            font=("Arial", 28),
        )

    @property
    def score_text(self):
        return f"{self.left_score} : {self.right_score}"

    def update(self):
        self.canvas.itemconfig(self.id, text=self.score_text)


class Game:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Simple Pong")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(
            self.root,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            bg="black",
        )
        self.canvas.pack()

        self.canvas.create_line(
            WINDOW_WIDTH / 2,
            0,
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT,
            fill="white",
            dash=(8, 8),
        )
        self.canvas.create_text(
            WINDOW_WIDTH // 4,
            WINDOW_HEIGHT - 30,
            text="Analog circuit controlled",
            fill="white",
            font=("Arial", 14),
        )
        self.canvas.create_text(
            WINDOW_WIDTH * 3 // 4,
            WINDOW_HEIGHT - 30,
            text="Keyboard button controlled",
            fill="white",
            font=("Arial", 14),
        )

        self.left_paddle = Paddle(self.canvas, 30, WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2, "white")
        self.right_paddle = Paddle(self.canvas, WINDOW_WIDTH - 30 - PADDLE_WIDTH, WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2, "white")
        self.ball = Ball(self.canvas, WINDOW_WIDTH // 2 - BALL_SIZE // 2, WINDOW_HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, "white")
        self.scoreboard = Scoreboard(self.canvas)
        self.paused = False

        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<KeyRelease>", self.on_key_release)

        self.move_up_left = False
        self.move_down_left = False
        self.move_up_right = False
        self.move_down_right = False
        self.digital_input_state = None

        # prepare CSV logging for incoming serial lines
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            log_dir = os.path.dirname(__file__)
            self.log_path = os.path.join(log_dir, f"serial_log_{timestamp}.csv")
            self.log_file = open(self.log_path, "w", newline="", encoding="utf-8")
            self.log_writer = csv.writer(self.log_file)
            self.log_writer.writerow(["timestamp", "paddle_sent", "ball_sent", "paddle_move"])
        except Exception as e:
            print(f"Could not open log file: {e}", file=sys.stderr)
            self.log_file = None
            self.log_writer = None

        # graceful shutdown handler to save log
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.loop()
        self.root.mainloop()

    def on_key_press(self, event):
        key = event.keysym
        if key == "w":
            self.move_up_left = True
        elif key == "s":
            self.move_down_left = True
        elif key == "Up":
            self.move_up_right = True
        elif key == "Down":
            self.move_down_right = True
        elif key == "space":
            self.paused = not self.paused

    def on_key_release(self, event):
        key = event.keysym
        if key == "w":
            self.move_up_left = False
        elif key == "s":
            self.move_down_left = False
        elif key == "Up":
            self.move_up_right = False
        elif key == "Down":
            self.move_down_right = False

    def loop(self):
        global ser
        if not self.paused:
            self.update_paddles()
            self.ball.update()
            self.check_collisions()
            self.check_score()

            # map ball vertical position (0..WINDOW_HEIGHT-BALL_SIZE) to 0..255
            max_y_ball = max(1, WINDOW_HEIGHT - self.ball.size)
            raw_ball_y = max(0, min(self.ball.y, max_y_ball))
            ball_value = int((raw_ball_y / max_y_ball) * 255)

            # map left paddle vertical position (0..WINDOW_HEIGHT-PADDLE_HEIGHT) to 0..255
            max_y_paddle = max(1, WINDOW_HEIGHT - self.left_paddle.height)
            raw_paddle_y = max(0, min(self.left_paddle.y, max_y_paddle))
            paddle_value = int((raw_paddle_y / max_y_paddle) * 255)

            packet = f"{paddle_value},{ball_value}\n"

            if ser is not None:
                try:
                    ser.write(packet.encode())
                except Exception as e:
                    print(f"Serial write error: {e}", file=sys.stderr)
                    try:
                        ser.close()
                    except Exception:
                        pass
                    ser = None

            self.read_esp32_state()
            state_text = self.digital_input_state or "N/A"

            # log parsed values: timestamp, paddle_sent, ball_sent, paddle_move
            try:
                if self.log_writer:
                    self.log_writer.writerow([time.time(), paddle_value, ball_value, state_text])
                    if self.log_file:
                        self.log_file.flush()
            except Exception:
                pass

            print(f"Sent: {paddle_value},{ball_value}  Received: {state_text}", end="\r", flush=True)

        self.root.after(FRAME_DELAY, self.loop)

    def update_paddles(self):
        if self.digital_input_state == "HIGH":
            self.left_paddle.move(-PADDLE_SPEED)
        elif self.digital_input_state == "LOW":
            self.left_paddle.move(PADDLE_SPEED)

        if self.move_up_right:
            self.right_paddle.move(-PADDLE_SPEED)
        if self.move_down_right:
            self.right_paddle.move(PADDLE_SPEED)

    def check_collisions(self):
        ball_left = self.ball.x
        ball_right = self.ball.x + self.ball.size
        ball_top = self.ball.y
        ball_bottom = self.ball.y + self.ball.size

        left_top = self.left_paddle.y
        left_bottom = self.left_paddle.y + self.left_paddle.height
        left_right = self.left_paddle.x + self.left_paddle.width

        right_top = self.right_paddle.y
        right_bottom = self.right_paddle.y + self.right_paddle.height
        right_left = self.right_paddle.x

        if ball_left <= left_right and ball_top < left_bottom and ball_bottom > left_top:
            self.ball.bounce_x()
            self.ball.x = left_right

        if ball_right >= right_left and ball_top < right_bottom and ball_bottom > right_top:
            self.ball.bounce_x()
            self.ball.x = right_left - self.ball.size

    def check_score(self):
        if self.ball.x < 0:
            self.scoreboard.right_score += 1
            self.scoreboard.update()
            self.reset_ball(direction=1)
        elif self.ball.x + self.ball.size > WINDOW_WIDTH:
            self.scoreboard.left_score += 1
            self.scoreboard.update()
            self.reset_ball(direction=-1)

    def read_esp32_state(self):
        global ser
        if ser is None:
            return

        try:
            while ser.in_waiting:
                line = ser.readline().decode(errors="ignore").strip()
                if not line:
                    continue
                if line == "1":
                    self.digital_input_state = "HIGH"
                elif line == "0":
                    self.digital_input_state = "LOW"
        except Exception as e:
            print(f"Serial read error: {e}", file=sys.stderr)
            try:
                ser.close()
            except Exception:
                pass
            ser = None

    def on_close(self):
        try:
            if hasattr(self, 'log_file') and self.log_file:
                try:
                    self.log_file.flush()
                except Exception:
                    pass
                try:
                    self.log_file.close()
                except Exception:
                    pass
                try:
                    print(f"\nSaved serial log: {self.log_path}")
                except Exception:
                    pass
        except Exception:
            pass

        try:
            global ser
            if ser:
                try:
                    ser.close()
                except Exception:
                    pass
        except Exception:
            pass

        try:
            self.root.destroy()
        except Exception:
            pass

    def reset_ball(self, direction=1):
        self.ball.reset(WINDOW_WIDTH // 2 - BALL_SIZE // 2, WINDOW_HEIGHT // 2 - BALL_SIZE // 2)
        self.ball.vx = BALL_SPEED_X * direction
        self.ball.vy = BALL_SPEED_Y if direction > 0 else -BALL_SPEED_Y


if __name__ == "__main__":
    Game()
