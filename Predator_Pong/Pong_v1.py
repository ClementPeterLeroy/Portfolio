"""
╔══════════════════════════════════════╗
║       P R E D A T O R   PONG         ║
╚══════════════════════════════════════╝
Current : v1.0.1
Predator is a pong game desgined to explore pygame and refresh some OOP mechanics for more finance projects later on.

VERSION NOTES : 
Predator Pong v1.0.1
Simple one window game with two paddles and a ball, counts to 5 and has constant speed.
No menu, no sounds or music. Bare bones.

Roadmap for next versions:
v1.0.2
encapsulating the classes in files for better architecture ?
Starting sequence and menu (here or v2)
Music in background
Sound effect when hitting, losing point and ending game

v1.0.3
Speed is variable depending on where it's hit on the paddle, can speed up or down
Angle also variable

v2.0
[Planned for v1.0.2][Addiding a launch screen and a menu with options]
Adding a 'Special game' mode with special powers:
- Larger ball
- Sinus movement
- Powercharge and special canoon
- Trap powerup, ball turns into a star and must not be touched ? 

v3.0
Adding Mode 4x4 with 4 players
Adding AI agents to play against us (with tensorflow library)
"""

import pygame
import sys

## Constants -----------------------------------------------------------------
WIDTH, HEIGHT = 800, 600
FPS = 60
WINNING_SCORE = 5

# Colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (40, 40, 40)

# Ball
BALL_SIZE = 14
BALL_SPEED = 5 # constant magnitude (pixels / frame)

# Paddles
PADDLE_W, PADDLE_H = 12, 90
PADDLE_SPEED = 6
PADDLE_MARGIN = 20 # distance from the side wall


## Classes  -----------------------------------------------------------------

class Ball:
    """Bouncing ball.  Speed magnitude is always constant."""

    def __init__(self):
        self.rect = pygame.Rect(0, 0, BALL_SIZE, BALL_SIZE)
        self.vel_x = BALL_SPEED
        self.vel_y = BALL_SPEED
        self.reset()

    # ------------------------------------------------------------------ reset
    def reset(self, direction: int = 1):
        """Place ball at centre and send it toward `direction` (±1)."""
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.vel_x = BALL_SPEED * direction
        self.vel_y = BALL_SPEED

    # ------------------------------------------------------------------ update
    def update(self, paddle_left: "Paddle", paddle_right: "Paddle") -> int:
        """Move the ball and return the side that scored (0 = no score,
        -1 = left player scored, +1 = right player scored)."""
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        ## top / bottom wall bounce -----------------------------------------------------------------
        if self.rect.top <= 0:
            self.rect.top = 0
            self.vel_y = abs(self.vel_y)
        elif self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
            self.vel_y = -abs(self.vel_y)

        ## paddle collisions -----------------------------------------------------------------
        if self.vel_x < 0 and self.rect.colliderect(paddle_left.rect):
            self.rect.left = paddle_left.rect.right
            self.vel_x = abs(self.vel_x)   # bounce right

        elif self.vel_x > 0 and self.rect.colliderect(paddle_right.rect):
            self.rect.right = paddle_right.rect.left
            self.vel_x = -abs(self.vel_x)  # bounce left

        ## scoring -----------------------------------------------------------------
        if self.rect.right <= 0:          # ball exits left  → right scores
            return 1
        if self.rect.left >= WIDTH:       # ball exits right → left scores
            return -1
        return 0

    # ------------------------------------------------------------------ draw
    def draw(self, surface: pygame.Surface):
        pygame.draw.ellipse(surface, WHITE, self.rect)


# -----------------------------------------------------------------

class Paddle:
    """A side paddle controlled by keyboard keys."""

    def __init__(self, x: int, up_key: int, down_key: int):
        self.rect = pygame.Rect(x, (HEIGHT - PADDLE_H) // 2, PADDLE_W, PADDLE_H)
        self.up_key = up_key
        self.down_key = down_key

    # ------------------------------------------------------------------ update
    def update(self, keys):
        if keys[self.up_key]:
            self.rect.y -= PADDLE_SPEED
        if keys[self.down_key]:
            self.rect.y += PADDLE_SPEED

        # clamp inside field
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(HEIGHT, self.rect.bottom)

    # ------------------------------------------------------------------ draw
    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, WHITE, self.rect, border_radius=4)


# -------------------------------------------------------------------

class ScoreBoard:
    """Keeps and renders the score for both players."""

    def __init__(self, font: pygame.font.Font):
        self.font = font
        self.score_left = 0
        self.score_right  = 0

    # ----------------------------------------------------------------- update
    def update(self, result: int):
        if result == -1:
            self.score_left  += 1
        elif result == 1:
            self.score_right += 1

    # ----------------------------------------------------------------- winner
    def winner(self) -> str | None:
        if self.score_left  >= WINNING_SCORE:
            return "Left"
        if self.score_right >= WINNING_SCORE:
            return "Right"
        return None

    # ----------------------------------------------------------------- draw
    def draw(self, surface: pygame.Surface):
        left_surf  = self.font.render(str(self.score_left),  True, WHITE)
        right_surf = self.font.render(str(self.score_right), True, WHITE)
        surface.blit(left_surf,  (WIDTH // 4 - left_surf.get_width()  // 2, 20))
        surface.blit(right_surf, (3 * WIDTH // 4 - right_surf.get_width() // 2, 20))


# -----------------------------------------------------------------

class Game:
    """Top-level game controller."""

    def __init__(self):
        pygame.init()
        self.screen  = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pong")
        self.clock   = pygame.time.Clock()

        self.font_score = pygame.font.SysFont("monospace", 64, bold=True)
        self.font_msg   = pygame.font.SysFont("monospace", 36)

        self._build_objects()

    # ---------------------------------------------------------------- helpers
    def _build_objects(self):
        self.paddle_left = Paddle(PADDLE_MARGIN, pygame.K_z, pygame.K_s)
        self.paddle_right = Paddle(WIDTH - PADDLE_MARGIN - PADDLE_W, pygame.K_UP, pygame.K_DOWN)
        self.ball = Ball()
        self.scoreboard = ScoreBoard(self.font_score)

    def _draw_field(self):
        self.screen.fill(BLACK)
        # centre dashed line
        dash_h = 18
        for y in range(0, HEIGHT, dash_h * 2):
            pygame.draw.rect(self.screen, GREY, (WIDTH // 2 - 2, y, 4, dash_h))

    def _show_message(self, lines: list[str]):
        """Render one or more centred lines and wait for a key press."""
        self.screen.fill(BLACK)
        total_h = len(lines) * 50
        start_y = (HEIGHT - total_h) // 2
        for i, line in enumerate(lines):
            surf = self.font_msg.render(line, True, WHITE)
            self.screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, start_y + i * 50))
        pygame.display.flip()
        self._wait_for_key()

    def _wait_for_key(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._quit()
                if event.type == pygame.KEYDOWN:
                    return

    def _quit(self):
        pygame.quit()
        sys.exit()

    # ------------------------------------------------------------------- run
    def run(self):
        self._show_message(["PONG",
                            "Left:  Z / S",
                            "Right: ↑ / ↓",
                            "Press any key to start"])

        direction = 1   # first serve goes right
        self.ball.reset(direction)

        while True:
            #  events -------------------------------------------------------------------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._quit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self._quit()

            #  update -------------------------------------------------------------------
            keys = pygame.key.get_pressed()
            self.paddle_left.update(keys)
            self.paddle_right.update(keys)

            result = self.ball.update(self.paddle_left, self.paddle_right)

            if result != 0:
                self.scoreboard.update(result)
                winner = self.scoreboard.winner()
                if winner:
                    self._show_message([f"{winner} player wins!",
                                        "Press any key to restart"])
                    self._build_objects()
                else:
                    direction = result   # serve toward the player who just lost
                    self.ball.reset(direction)

            #  draw -------------------------------------------------------------------
            self._draw_field()
            self.paddle_left.draw(self.screen)
            self.paddle_right.draw(self.screen)
            self.ball.draw(self.screen)
            self.scoreboard.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(FPS)


# Entry point -------------------------------------------------------------------

if __name__ == "__main__":
    Game().run()
