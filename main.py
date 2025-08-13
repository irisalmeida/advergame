try:
    import pygbag.aio as asyncio 
except ImportError:
    import asyncio

import pygame as pg
import random
import time


WIDTH, HEIGHT = 960, 540
FPS = 60

BG = (14, 16, 22)
FG = (240, 240, 240)
ACCENT = (0, 180, 255) 
YELLOW = (255, 210, 90)
GREEN = (50, 200, 120) 
RED = (230, 60, 60)  

pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Feira do Empreendedor — Trilha de Oportunidades")
clock = pg.time.Clock()


def load_font(size=24):
    return pg.font.Font(None, size)


FONT = load_font(24)
FONT_BIG = load_font(36)
FONT_HUGE = load_font(56)



class State:
    ABERTURA = 0
    JOGO = 1
    FINAL = 2


state = State.ABERTURA

player_x, player_y = WIDTH * 0.15, HEIGHT * 0.8
player_vy = 0
on_ground = True
gravity = 1800
jump_v = -680
speed = 300
obstacles = []
collects = []
points = 0
t_start = 0
game_duration = 30  

dicas = [
    "Invista em inovação para se destacar.",
    "Conecte-se com outros empreendedores.",
    "Sustentabilidade também gera lucro.",
    "Conheça bem o seu público-alvo.",
    "Marketing digital é essencial hoje.",
    "Agronegócio é oportunidade crescente.",
    "Aposte em parcerias estratégicas.",
    "Adapte-se rápido às mudanças do mercado.",
    "Gerencie bem seu fluxo de caixa.",
    "Ouça o feedback dos clientes.",
    "Aproveite eventos para networking.",
    "Invista na capacitação da sua equipe.",
    "Use tecnologia para otimizar processos.",
    "Crie uma proposta de valor clara.",
    "Analise seus concorrentes e aprenda.",
    "Foque na experiência do cliente.",
    "Defina metas e acompanhe resultados.",
    "Esteja aberto a novas ideias.",
    "Transforme problemas em oportunidades.",
    "Acredite no potencial do seu negócio."
]



def reset_level():
    global obstacles, collects, player_y, player_vy, on_ground, points, t_start
    obstacles = []
    collects = []
    player_y = HEIGHT * 0.8
    player_vy = 0
    on_ground = True
    points = 0
    t_start = time.time()


def player_rect():
    return pg.Rect(int(player_x), int(player_y) - 48, 32, 48)


def try_jump():
    global on_ground, player_vy
    if on_ground:
        player_vy = jump_v
        on_ground = False


def handle_physics(dt):
    global player_y, player_vy, on_ground
    if not on_ground:
        player_vy += gravity * dt
    player_y += player_vy * dt
    ground_y = HEIGHT * 0.8
    if player_y >= ground_y:
        player_y = ground_y
        player_vy = 0
        on_ground = True


def spawn_entities():
    if random.random() < 0.02:
        obstacles.append(pg.Rect(WIDTH, HEIGHT * 0.8 - 32, 32, 32))
    if random.random() < 0.015:
        collects.append(pg.Rect(WIDTH, HEIGHT * 0.8 - 120, 24, 24))


def update_world(dt):
    global points
    pr = player_rect()
    for rect in obstacles[:]:
        rect.x -= int(speed * dt)
        if pr.colliderect(rect):
            points = max(0, points - 1)
            obstacles.remove(rect)
        elif rect.right < 0:
            obstacles.remove(rect)
    for c in collects[:]:
        c.x -= int(speed * dt)
        if pr.colliderect(c):
            points += 1
            show_tip(random.choice(dicas))
            collects.remove(c)
        elif c.right < 0:
            collects.remove(c)



tip_text = ""
tip_timer = 0


def show_tip(text):
    global tip_text, tip_timer
    tip_text = text
    tip_timer = time.time()


def draw_tip():
    if tip_text and time.time() - tip_timer < 2:
        draw_text(screen, tip_text, (WIDTH // 2, 80), FONT, YELLOW, center=True)


def draw_text(surf, text, pos, font, color, center=False):
    img = font.render(text, True, color)
    rect = img.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    surf.blit(img, rect)


def draw_world():
    pg.draw.rect(screen, GREEN, player_rect())  
    for rect in obstacles:
        pg.draw.rect(screen, RED, rect)
    for c in collects:
        pg.draw.rect(screen, ACCENT, c)


def perfil_empreendedor(pontos):
    if pontos <= 5:
        return "Iniciante Visionário"
    elif pontos <= 10:
        return "Empreendedor em Ascensão"
    else:
        return "Líder Transformador"


async def game_loop():
    global state
    reset_level()
    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                if state == State.ABERTURA:
                    state = State.JOGO
                    reset_level()
                elif state == State.JOGO:
                    try_jump()
                elif state == State.FINAL:
                    state = State.ABERTURA

        screen.fill(BG)

        if state == State.ABERTURA:
            draw_text(screen, "Feira do Empreendedor 2025", (WIDTH // 2, 80), FONT_HUGE, ACCENT, center=True)
            draw_text(
                screen,
                "Na Trilha de Oportunidades, você vive a experiência de empreender!",
                (WIDTH // 2, 140),
                FONT,
                FG,
                center=True,
            )
            draw_text(
                screen, "Pegue os ITENS AZUIS para conquistar oportunidades", (WIDTH // 2, 220), FONT_BIG, ACCENT, center=True
            )
            draw_text(screen, "Desvie dos ITENS VERMELHOS para evitar desafios", (WIDTH // 2, 260), FONT_BIG, RED, center=True)
            draw_text(screen, "Clique para pular durante o jogo", (WIDTH // 2, 320), FONT, YELLOW, center=True)
            draw_text(screen, "Clique para começar!", (WIDTH // 2, 400), FONT_BIG, FG, center=True)

        elif state == State.JOGO:
            spawn_entities()
            update_world(dt)
            handle_physics(dt)
            draw_world()
            draw_tip()
            draw_text(screen, f"Pontos: {points}", (20, 20), FONT, FG)
            elapsed = time.time() - t_start
            if elapsed >= game_duration:
                state = State.FINAL

        elif state == State.FINAL:
            draw_text(screen, "Fim de jogo!", (WIDTH // 2, 100), FONT_HUGE, ACCENT, center=True)
            draw_text(screen, f"Sua pontuação: {points}", (WIDTH // 2, 180), FONT_BIG, FG, center=True)
            draw_text(
                screen, f"Perfil Empreendedor: {perfil_empreendedor(points)}", (WIDTH // 2, 250), FONT_BIG, YELLOW, center=True
            )
            draw_text(screen, "Clique para jogar novamente", (WIDTH // 2, 350), FONT, FG, center=True)

        pg.display.flip()
        await asyncio.sleep(0)

    pg.quit()


if __name__ == "__main__":
    asyncio.run(game_loop())
