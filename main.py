import asyncio
import pygame

async def main():
    pygame.init()

    ANCHO, ALTO = 540, 960
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Prueba")

    fuente = pygame.font.SysFont(None, 48)

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return

        pantalla.fill((15, 25, 45))

        texto = fuente.render("¡FUNCIONA!", True, (0, 255, 150))
        pantalla.blit(texto, (ANCHO//2 - texto.get_width()//2, ALTO//2 - 30))

        texto2 = fuente.render("Pygbag OK", True, (100, 200, 255))
        pantalla.blit(texto2, (ANCHO//2 - texto2.get_width()//2, ALTO//2 + 30))

        pygame.display.flip()
        await asyncio.sleep(0)

asyncio.run(main())
