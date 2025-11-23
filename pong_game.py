import pygame
import serial
import time
import random

# ---------------- Serial Setup ----------------
try:
    ser = serial.Serial(port='COM5', baudrate=115200, timeout=1)
    print("Connected to ESP32!")
    ser.flushInput()
except:
    ser = None
    print("ESP32 not connected.")

# ---------------- Pygame Setup ----------------
pygame.init()
WIDTH, HEIGHT = 900, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong – ESP32 Sync Edition")

WHITE = (255,255,255)
BLACK = (0,0,0)
GREY  = (150,150,150)

font = pygame.font.Font(None, 36)
debug_font = pygame.font.Font(None, 28)

# Game objects
ball = pygame.Rect(WIDTH//2, HEIGHT//2, 20, 20)
left_paddle  = pygame.Rect(30, HEIGHT//2 - 50, 12, 120)
right_paddle = pygame.Rect(WIDTH - 42, HEIGHT//2 - 50, 12, 120)

ball_speed = [4,4]
paddle_speed = 5

left_score = 0
right_score = 0

clock = pygame.time.Clock()
running = True


# ---------------- Main Loop ----------------
while running:
    dt = clock.tick(60)
    fps = clock.get_fps()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            if ser: ser.close()

    # --------------- Player Paddle ----------------
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and left_paddle.top > 0:
        left_paddle.y -= paddle_speed
    if keys[pygame.K_s] and left_paddle.bottom < HEIGHT:
        left_paddle.y += paddle_speed

    # ---------------- SEND DATA TO ESP32 ----------------
    if ser:
        msg = f"{ball.y},{right_paddle.y}\n"
        ser.write(msg.encode())
        reply = ser.readline().decode().strip()

        if reply == "1" and right_paddle.top > 0:
            right_paddle.y -= paddle_speed
        elif reply == "0" and right_paddle.bottom < HEIGHT:
            right_paddle.y += paddle_speed

    # ---------------- Ball movement ----------------
    ball.x += ball_speed[0]
    ball.y += ball_speed[1]

    # Bounce on top/bottom
    if ball.top <= 0 or ball.bottom >= HEIGHT:
        ball_speed[1] *= -1

    # Paddle collisions
    if ball.colliderect(left_paddle) or ball.colliderect(right_paddle):
        ball_speed[0] *= -1

    # ---------------- Scoring ----------------
    if ball.left <= 0:
        right_score += 1
        ball.x, ball.y = WIDTH//2, random.randint(20, 480)
        ball_speed[0] = abs(ball_speed[0])

    if ball.right >= WIDTH:
        left_score += 1
        ball.x, ball.y = WIDTH//2, random.randint(20, 480)
        ball_speed[0] = -abs(ball_speed[0])

    # ---------------- Draw everything ----------------
    screen.fill(BLACK)

    # Middle dashed line
    for i in range(0, HEIGHT, 25):
        pygame.draw.rect(screen, GREY, (WIDTH//2 - 2, i, 4, 15))

    # Paddles + ball
    pygame.draw.rect(screen, WHITE, left_paddle, border_radius=6)
    pygame.draw.rect(screen, WHITE, right_paddle, border_radius=6)
    pygame.draw.ellipse(screen, WHITE, ball)

    # ---------------- Scoreboard ----------------
    score_text = font.render(f"{left_score}    :    {right_score}", True, WHITE)
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 20))

    # Labels
    screen.blit(font.render("PLAYER", True, WHITE), (30, 20))
    screen.blit(font.render("CIRCUIT BOT", True, WHITE), (WIDTH - 200, 20))

    # ---------------- FPS + DEBUG OVERLAY ----------------
    debug_info = f"FPS: {fps:.1f}   Ball Y: {ball.y}   RightPaddle Y: {right_paddle.y}"
    debug_surf = debug_font.render(debug_info, True, GREY)
    screen.blit(debug_surf, (20, HEIGHT - 40))

    pygame.display.flip()

pygame.quit()
if ser:
    ser.close()
