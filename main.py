import pygame
import sys
import random
import os
import asyncio

pygame.init()

# Janela
largura, altura = 800, 400
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Jogo do Dinossauro")

# Cores
BRANCO = (255, 255, 255)
VERMELHO = (255, 0, 0)

# Fonte
fonte = pygame.font.SysFont(None, 36)

# Caminho das imagens
pasta_img = "img"

recorde = 0

walk = [pygame.transform.scale(
    pygame.image.load(os.path.join(pasta_img, "walk", f"walk{i}.png")), (60, 60)) for i in range(1, 11)]

jump = [pygame.transform.scale(
    pygame.image.load(os.path.join(pasta_img, "jump", f"jump{i}.png")), (60, 60)) for i in range(1, 13)]

down = [pygame.transform.scale(
    pygame.image.load(os.path.join(pasta_img, "down", "down1.png")), (60, 35))]


cacto_imgs = [
    pygame.transform.scale(pygame.image.load(os.path.join(pasta_img, "cacto1.png")), (40, 60)),
    pygame.transform.scale(pygame.image.load(os.path.join(pasta_img, "cacto2.png")), (30, 50))
]

def gerar_obstaculos():
    return [
        {
            "img": random.choice(cacto_imgs),
            "x": largura + i * 390,
            "y": altura - cacto_imgs[0].get_height() - 50
        }
        for i in range(3)
    ]

def resetar():
    global velocidade_obstaculos
    velocidade_obstaculos = 8
    return {
        "dino_y": altura - 60 - 50,
        "vel_y": 0,
        "pulando": False,
        "abaixado": False,
        "pontos": 0,
        "game_over": False,
        "obstaculos": gerar_obstaculos()
    }

estado = resetar()
gravidade = 1
dino_x = 50

frame_index = 0
frame_count = 0
frame_delay = 5
velocidade_obstaculos = 8

async def main():
    global frame_index, frame_count, animacao_atual, estado, recorde, velocidade_obstaculos
    pygame.event.pump()  # Ajuda o navegador a iniciar o contexto corretamente

    while True:
        await asyncio.sleep(1 / 180)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if (evento.key in [pygame.K_SPACE, pygame.K_UP]) and not estado["pulando"] and not estado["game_over"]:
                    estado["vel_y"] = -15
                    estado["pulando"] = True
                if evento.key == pygame.K_DOWN and not estado["pulando"]:
                    estado["abaixado"] = True
                if evento.key == pygame.K_r and estado["game_over"]:
                    estado = resetar()
                    frame_index = 0
                    frame_count = 0
            if evento.type == pygame.KEYUP:
                if evento.key == pygame.K_DOWN:
                    estado["abaixado"] = False

        dino_altura = 35 if estado["abaixado"] else 60
        chao_y = altura - dino_altura - 50

        if not estado["game_over"]:
            estado["vel_y"] += gravidade
            estado["dino_y"] += estado["vel_y"]

            if estado["dino_y"] >= chao_y:
                estado["dino_y"] = chao_y
                estado["vel_y"] = 0
                estado["pulando"] = False

            for ob in estado["obstaculos"]:
                ob["x"] -= velocidade_obstaculos
                if ob["x"] + ob["img"].get_width() < 0:
                    ob["x"] = largura + random.randint(300, 600)
                    ob["img"] = random.choice(cacto_imgs)
                    ob["y"] = altura - ob["img"].get_height() - 50
                    estado["pontos"] += 1

            if estado["pontos"] % 10 == 0 and estado["pontos"] > 0:
                velocidade_obstaculos = 8 + (estado["pontos"] // 10)

        nova_animacao = jump if estado["pulando"] else down if estado["abaixado"] else walk

        if 'animacao_atual' not in globals() or animacao_atual != nova_animacao:
            frame_index = 0
        animacao_atual = nova_animacao

        frame_count += 1
        if frame_count >= frame_delay:
            frame_count = 0
            frame_index = (frame_index + 1) % len(animacao_atual)

        dino_sprite = animacao_atual[frame_index]

        tela.fill(BRANCO)
        tela.blit(dino_sprite, (dino_x, estado["dino_y"]))

        dino_rect = pygame.Rect(dino_x, estado["dino_y"], 60, dino_altura)

        for ob in estado["obstaculos"]:
            tela.blit(ob["img"], (ob["x"], ob["y"]))
            ob_rect = pygame.Rect(ob["x"], ob["y"], ob["img"].get_width(), ob["img"].get_height())
            if dino_rect.colliderect(ob_rect):
                estado["game_over"] = True

        pontos_txt = fonte.render(f"Pontos: {estado['pontos']}", True, (0, 0, 0))
        tela.blit(pontos_txt, (10, 10))

        recorde_txt = fonte.render(f"Recorde: {recorde}", True, (0, 0, 0))
        tela.blit(recorde_txt, (largura - recorde_txt.get_width() - 10, 10))

        velocidade_txt = fonte.render(f"Velocidade: {velocidade_obstaculos}", True, (0, 0, 0))
        tela.blit(velocidade_txt, (10, 40))

        if estado["pontos"] > recorde:
            recorde = estado["pontos"]

        if estado["game_over"]:
            msg = fonte.render("Game Over! Pressione R para reiniciar", True, VERMELHO)
            msg_rect = msg.get_rect(center=(largura // 2, altura // 2))
            tela.blit(msg, msg_rect)

            
        pygame.display.update()

# Execução do asyncio
asyncio.run(main())
