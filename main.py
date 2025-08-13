import sys, time, random
import pygame as pg

try:
    import js
except Exception:
    js = None

WIDTH, HEIGHT = 960, 540
FPS = 60

BG = (14, 16, 22)
FG = (240, 240, 240)
ACCENT = (76, 201, 240)
ACCENT2 = (190, 255, 100)
RED = (255, 90, 90)
YELLOW = (255, 210, 90)
GRAY = (160, 170, 180)
CARD_L = (80, 235, 255)
CARD_R = (120, 140, 200)

pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("IF/ELSE — Trilha da Borborema (Click-only)")
clock = pg.time.Clock()


def load_font(size=24):
    try:
        return pg.font.SysFont("DejaVu Sans Mono", size)
    except Exception:
        return pg.font.SysFont(None, size)


FONT = load_font(22)
FONT_BIG = load_font(36)
FONT_HUGE = load_font(56)


# Background animation
class CodeRain:
    def __init__(self, cols=110):
        self.cols = cols
        self.speed = [random.uniform(40, 140) for _ in range(cols)]
        self.y = [random.uniform(-HEIGHT, 0) for _ in range(cols)]
        self.x = [i * (WIDTH / cols) for i in range(cols)]

    def draw(self, surf, dt):
        for i in range(self.cols):
            self.y[i] += self.speed[i] * dt
            if self.y[i] > HEIGHT + 40:
                self.y[i] = random.uniform(-HEIGHT * 0.5, 0)
                self.speed[i] = random.uniform(60, 160)
            c = (22, 120, 140) if i % 3 == 0 else (24, 28, 36)
            pg.draw.line(surf, c, (self.x[i], self.y[i]), (self.x[i], self.y[i] - 40), 2)


bg = CodeRain()


class State:
    ABERTURA = 0
    JOGO = 1
    DEC1 = 2
    DEC2 = 3
    FINAL = 4


state = State.ABERTURA

# Player & world
player_x, player_y = WIDTH * 0.15, HEIGHT * 0.7
player_vy = 0.0
on_ground = True
gravity = 1800.0
jump_v = -680.0
speed = 240.0
scroll_x = 0.0
obstacles = []
collects = []
commits = 0


def player_rect():
    return pg.Rect(int(player_x), int(player_y) - 48, 32, 48)


def draw_player(surf):
    r = player_rect()
    pg.draw.rect(surf, ACCENT, r, 0, border_radius=8)
    pg.draw.rect(surf, (0, 0, 0), (r.x + 8, r.y + 12, 6, 6))
    pg.draw.rect(surf, (0, 0, 0), (r.x + 18, r.y + 12, 6, 6))


def draw_ground(surf, offset):
    base_y = int(HEIGHT * 0.8)
    pg.draw.rect(surf, (28, 34, 46), (0, base_y, WIDTH, HEIGHT - base_y))
    for i in range(0, WIDTH, 80):
        x = i - int(offset) % 80
        pg.draw.rect(surf, (36, 44, 58), (x, base_y, 40, 6))


def reset_level():
    global obstacles, collects, scroll_x, player_y, player_vy, on_ground, commits, t0
    obstacles, collects = [], []
    scroll_x = 0.0
    player_y = HEIGHT * 0.7
    player_vy = 0.0
    on_ground = True
    commits = 0
    t0 = time.time()
    for i in range(10):
        x = WIDTH + i * 320 + random.randint(-60, 60)
        w = random.randint(40, 70)
        h = random.randint(24, 40)
        y = HEIGHT * 0.78
        obstacles.append(pg.Rect(x, y, w, h))
        if random.random() < 0.7:
            collects.append(pg.Rect(x + w // 2 - 8, y - 120, 16, 16))


def handle_physics(dt):
    global player_y, player_vy, on_ground
    if not on_ground:
        player_vy += gravity * dt
    player_y += player_vy * dt
    ground_y = HEIGHT * 0.8
    if player_y >= ground_y:
        player_y = ground_y
        player_vy = 0.0
        on_ground = True


def try_jump():
    global on_ground, player_vy
    if on_ground:
        player_vy = jump_v
        on_ground = False


def update_world(dt):
    global scroll_x, commits
    scroll_x += speed * dt
    pr = player_rect()
    for rect in obstacles:
        rect.x -= int(speed * dt)
        if pr.colliderect(rect):
            try_jump()
    for c in collects[:]:
        c.x -= int(speed * dt)
        if pr.colliderect(c):
            commits += 1
            collects.remove(c)


def draw_world(surf, dt):
    bg.draw(surf, dt)
    draw_ground(surf, scroll_x)
    for rect in obstacles:
        pg.draw.rect(surf, RED, rect, 0, border_radius=6)
    for c in collects:
        pg.draw.rect(surf, YELLOW, c, 0, border_radius=4)


def draw_text(surf, text, pos, font=FONT, color=FG, center=False):
    if isinstance(text, (list, tuple)):
        y = pos[1]
        for line in text:
            img = font.render(line, True, color)
            rect = img.get_rect()
            rect.topleft = (pos[0], y)
            if center:
                rect.centerx = pos[0]
            surf.blit(img, rect)
            y += rect.height + 2
        return
    img = font.render(text, True, color)
    rect = img.get_rect()
    rect.topleft = pos
    if center:
        rect.centerx = pos[0]
    surf.blit(img, rect)


def rect_card(surf, rect, title, who, meta, color):
    pg.draw.rect(surf, color, rect, 0, border_radius=18)
    pg.draw.rect(surf, (0, 0, 0), rect, 2, border_radius=18)
    pad = 14
    x = rect.x + pad
    y = rect.y + pad
    draw_text(surf, title, (x, y), FONT_BIG, (0, 0, 0))
    y += 34
    draw_text(surf, who, (x, y), FONT, (20, 20, 20))
    y += 24
    draw_text(surf, meta, (x, y), FONT, (32, 32, 32))


OPT1_A = {
    "id": "21_inovacao",
    "title": "Liderando com inovação",
    "who": "Dafna Blaschkauer",
    "meta": "Palco Mandacaru | 21/08 — 18h30",
}
OPT1_B = {
    "id": "21_carreira",
    "title": "Carreira, Empreendedorismo e Economia Criativa",
    "who": "Carlinhos Brown & Marc Tawill",
    "meta": "Palco Principal | 21/08 — 20h",
}
OPT2_A = {
    "id": "22_ia",
    "title": "IA aplicada à rotina dos pequenos negócios",
    "who": "Andrea Formiga",
    "meta": "Palco Angico | 22/08 — 15h30",
}
OPT2_B = {
    "id": "22_criativo",
    "title": "O futuro é criativo",
    "who": "Caio Viana",
    "meta": "Palco Broto de Catingueiras | 22/08 — 16h45",
}

choices = {"d1": None, "d2": None}

# Buttons (final screen)
BTN_DOWNLOAD = pg.Rect(WIDTH // 2 - 180, HEIGHT - 110, 160, 50)
BTN_RESTART = pg.Rect(WIDTH // 2 + 20, HEIGHT - 110, 160, 50)


def save_local(data):
    if js is None:
        return
    try:
        js.window.localStorage.setItem("ifelse_trilha_last", pg.json.dumps(data))
    except Exception:
        try:
            js.window.localStorage.setItem("ifelse_trilha_last", str(data))
        except Exception:
            pass


def download_csv(rows, filename="trilha.csv"):
    if js is None:
        print("CSV:", rows)
        return
    try:
        header = "timestamp,d1,d2,commits\n"
        body = "".join([",".join(map(str, r)) + "\n" for r in rows])
        text = header + body
        blob = js.Blob.new([text], {"type": "text/csv"})
        url = js.URL.createObjectURL(blob)
        a = js.document.createElement("a")
        a.href = url
        a.download = filename
        js.document.body.appendChild(a)
        a.click()
        js.document.body.removeChild(a)
        js.URL.revokeObjectURL(url)
    except Exception as e:
        print("CSV download error:", e)


def decision_screen(title, left, right, time_left):
    screen.fill(BG)
    draw_text(screen, title, (WIDTH // 2, 50), FONT_BIG, ACCENT2, center=True)
    L = pg.Rect(80, 120, WIDTH // 2 - 120, 320)
    R = pg.Rect(WIDTH // 2 + 40, 120, WIDTH // 2 - 120, 320)
    rect_card(screen, L, left["title"], left["who"], left["meta"], CARD_L)
    rect_card(screen, R, right["title"], right["who"], right["meta"], CARD_R)
    # countdown bar
    bar_w = int((time_left / 5.0) * (WIDTH - 160))
    pg.draw.rect(screen, (50, 56, 70), (80, 460, WIDTH - 160, 10), border_radius=6)
    pg.draw.rect(screen, ACCENT, (80, 460, max(10, bar_w), 10), border_radius=6)
    draw_text(screen, "Clique no cartão para escolher (auto B em 5s)", (WIDTH // 2, 485), FONT, FG, center=True)
    return L, R


def final_screen():
    screen.fill(BG)
    draw_text(screen, "Trilha Compilada", (WIDTH // 2, 40), FONT_HUGE, ACCENT2, center=True)
    y = 120
    for label, opt in (("Dia 21", choices["d1"]), ("Dia 22", choices["d2"])):
        r = pg.Rect(80, y, WIDTH - 160, 96)
        pg.draw.rect(screen, (28, 34, 46), r, 0, border_radius=14)
        pg.draw.rect(screen, (0, 0, 0), r, 2, border_radius=14)
        draw_text(screen, f"{label}: {opt['title']}", (r.x + 16, r.y + 12), FONT_BIG, FG)
        draw_text(screen, f"{opt['who']} | {opt['meta']}", (r.x + 16, r.y + 52), FONT, (200, 210, 220))
        y += 112
    # Buttons
    pg.draw.rect(screen, (32, 120, 90), BTN_DOWNLOAD, 0, border_radius=12)
    pg.draw.rect(screen, (0, 0, 0), BTN_DOWNLOAD, 2, border_radius=12)
    draw_text(screen, "Baixar CSV", (BTN_DOWNLOAD.centerx, BTN_DOWNLOAD.centery - 12), FONT_BIG, (0, 0, 0), center=True)
    pg.draw.rect(screen, (120, 40, 60), BTN_RESTART, 0, border_radius=12)
    pg.draw.rect(screen, (0, 0, 0), BTN_RESTART, 2, border_radius=12)
    draw_text(screen, "Reiniciar", (BTN_RESTART.centerx, BTN_RESTART.centery - 12), FONT_BIG, (0, 0, 0), center=True)
    draw_text(screen, f"Commits coletados: {commits}", (WIDTH - 260, 16), FONT, YELLOW)


def main():
    global state, choices
    reset_level()
    state = State.ABERTURA
    decision_timer = 5.0
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if state == State.ABERTURA:
                    # qualquer clique começa
                    state = State.JOGO
                    reset_level()
                elif state == State.JOGO:
                    # clique = pulo
                    try_jump()
                elif state == State.DEC1:
                    L, R = decision_screen("Dia 21 — Selecione sua ênfase", OPT1_A, OPT1_B, decision_timer)
                    if L.collidepoint(mx, my):
                        choices["d1"] = OPT1_A
                        state = State.JOGO
                        reset_level()
                        decision_timer = 5.0
                    elif R.collidepoint(mx, my):
                        choices["d1"] = OPT1_B
                        state = State.JOGO
                        reset_level()
                        decision_timer = 5.0
                elif state == State.DEC2:
                    L, R = decision_screen("Dia 22 — Selecione sua ênfase", OPT2_A, OPT2_B, decision_timer)
                    if L.collidepoint(mx, my):
                        choices["d2"] = OPT2_A
                        state = State.FINAL
                    elif R.collidepoint(mx, my):
                        choices["d2"] = OPT2_B
                        state = State.FINAL
                elif state == State.FINAL:
                    if BTN_DOWNLOAD.collidepoint(mx, my):
                        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                        row = [ts, choices["d1"]["id"], choices["d2"]["id"], str(commits)]
                        download_csv([row])
                    elif BTN_RESTART.collidepoint(mx, my):
                        choices = {"d1": None, "d2": None}
                        state = State.ABERTURA

        # Render
        if state == State.ABERTURA:
            screen.fill(BG)
            bg.draw(screen, dt)
            draw_text(screen, "IF/ELSE — Trilha da Borborema", (WIDTH // 2, 140), FONT_HUGE, ACCENT2, center=True)
            draw_text(
                screen,
                ["Clique para começar.", "Durante o jogo: clique para pular.", "Nas escolhas: clique no cartão desejado."],
                (WIDTH // 2, 240),
                FONT_BIG,
                FG,
                center=True,
            )
        elif state == State.JOGO:
            update_world(dt)
            screen.fill(BG)
            draw_world(screen, dt)
            draw_player(screen)
            draw_text(screen, f"Commits: {commits}", (20, 16), FONT, YELLOW)
            # triggers
            dist = int((time.time() - t0) * speed)
            if choices["d1"] is None and dist > 900:
                state = State.DEC1
                decision_timer = 5.0
            elif choices["d1"] is not None and choices["d2"] is None and dist > 1800:
                state = State.DEC2
                decision_timer = 5.0
            handle_physics(dt)
        elif state == State.DEC1:
            decision_timer -= dt
            decision_screen("Dia 21 — Selecione sua ênfase", OPT1_A, OPT1_B, max(0, decision_timer))
            if decision_timer <= 0:
                choices["d1"] = OPT1_B  # auto B
                state = State.JOGO
                reset_level()
                decision_timer = 5.0
        elif state == State.DEC2:
            decision_timer -= dt
            decision_screen("Dia 22 — Selecione sua ênfase", OPT2_A, OPT2_B, max(0, decision_timer))
            if decision_timer <= 0:
                choices["d2"] = OPT2_B  # auto B
                state = State.FINAL
        elif state == State.FINAL:
            final_screen()
            save_local({"timestamp": time.time(), "d1": choices["d1"]["id"], "d2": choices["d2"]["id"], "commits": commits})
        pg.display.flip()
    pg.quit()
    sys.exit()


if __name__ == "__main__":
    main()
