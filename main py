import asyncio
import pygame
import random
import sys

async def main():
    pygame.init()

    # ======================
    # CONFIGURACIÓN PANTALLA
    # ======================
    ANCHO = 540
    ALTO = 960
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Ataques Espaciales")

    # ======================
    # COLORES
    # ======================
    NEGRO = (10, 10, 20)
    AZUL_NAVE = (0, 200, 255)
    AZUL_SALUD = (0, 150, 255)
    ROJO_ENEMIGO = (255, 60, 60)
    NARANJA_KAMIKAZE = (255, 140, 0)
    AMARILLO_BALA = (255, 230, 0)
    BOTON_COLOR = (40, 40, 65)
    BLANCO = (255, 255, 255)
    VERDE = (40, 180, 90)
    ROJO = (200, 50, 50)
    AZUL_CONFIG = (30, 120, 200)
    DORADO = (255, 200, 50)
    OVERLAY = (0, 0, 0, 180)

    # ======================
    # FUENTES
    # ======================
    fuente = pygame.font.SysFont(None, 26)
    fuente_grande = pygame.font.SysFont(None, 40)
    fuente_titulo = pygame.font.SysFont(None, 48)
    fuente_peque = pygame.font.SysFont(None, 22)

    # ======================
    # VARIABLES DEL JUEGO
    # ======================
    jugador_tam = 55
    velocidad_jugador = 8
    velocidad_bala = 14
    cadencia = 11
    velocidad_enemigo = 5
    max_enemigos = 7

    estado = "MENU"
    tipo_control = "BOTONES"      # BOTONES o DESLIZAR
    tipo_layout = "COMPACTO"      # CLASICO, LATERALES, COMPACTO
    mostrar_tutorial = False

    high_score = 0
    nuevo_record = False

    # ======================
    # BOTONES MENÚ
    # ======================
    bw = int(ANCHO * 0.72)
    bh = 56
    bx = ANCHO // 2 - bw // 2

    btn_iniciar = pygame.Rect(bx, 340, bw, bh)
    btn_tutorial = pygame.Rect(bx, 415, bw, bh)
    btn_opciones = pygame.Rect(bx, 490, bw, bh)
    btn_salir = pygame.Rect(bx, 565, bw, bh)

    btn_modo = pygame.Rect(bx, 360, bw, bh)
    btn_layout = pygame.Rect(bx, 445, bw, bh)
    btn_volver = pygame.Rect(bx, 545, bw, bh)

    btn_pausa = pygame.Rect(ANCHO - 70, 18, 55, 42)
    btn_reanudar = pygame.Rect(ANCHO//2 - 140, ALTO//2 - 30, 280, 55)
    btn_menu_pausa = pygame.Rect(ANCHO//2 - 140, ALTO//2 + 50, 280, 55)
    btn_reintentar = pygame.Rect(ANCHO//2 - 140, ALTO//2 + 10, 280, 55)
    btn_menu_go = pygame.Rect(ANCHO//2 - 140, ALTO//2 + 85, 280, 55)
    btn_cerrar_tut = pygame.Rect(ANCHO//2 - 130, 780, 260, 52)

    # ======================
    # BOTONES DE CONTROL
    # ======================
    def crear_botones_control():
        nonlocal btn_izq, btn_der, btn_arr, btn_aba
        if tipo_layout == "CLASICO":
            btn_izq = pygame.Rect(0, ALTO - 95, ANCHO//2, 95)
            btn_der = pygame.Rect(ANCHO//2, ALTO - 95, ANCHO//2, 95)
            btn_arr = pygame.Rect(ANCHO//2 - 65, ALTO - 185, 130, 65)
            btn_aba = pygame.Rect(ANCHO//2 - 65, ALTO - 115, 130, 55)
        elif tipo_layout == "LATERALES":
            btn_izq = pygame.Rect(12, ALTO//2 - 70, 85, 140)
            btn_der = pygame.Rect(ANCHO - 97, ALTO//2 - 70, 85, 140)
            btn_arr = pygame.Rect(ANCHO//2 - 55, ALTO - 190, 110, 65)
            btn_aba = pygame.Rect(ANCHO//2 - 55, ALTO - 110, 110, 60)
        else:  # COMPACTO
            base = ALTO - 165
            btn_izq = pygame.Rect(18, base, 145, 75)
            btn_der = pygame.Rect(ANCHO - 163, base, 145, 75)
            btn_arr = pygame.Rect(ANCHO//2 - 58, base - 85, 116, 65)
            btn_aba = pygame.Rect(ANCHO//2 - 58, base + 10, 116, 55)

    btn_izq = btn_der = btn_arr = btn_aba = pygame.Rect(0, 0, 10, 10)
    crear_botones_control()

    # ======================
    # ESTRELLAS
    # ======================
    estrellas = []
    for _ in range(65):
        estrellas.append({
            "x": random.randint(0, ANCHO),
            "y": random.randint(0, ALTO),
            "vel": random.uniform(1.4, 3.8),
            "r": random.randint(1, 2)
        })

    reloj = pygame.time.Clock()
    menu_offset = 0.0
    menu_dir = 1

    # ======================
    # FUNCIONES DE DIBUJO
    # ======================
    def dibujar_boton(rect, texto, color):
        sombra = rect.move(3, 3)
        pygame.draw.rect(pantalla, (15, 15, 25), sombra, border_radius=14)
        pygame.draw.rect(pantalla, color, rect, border_radius=14)
        txt = fuente.render(texto, True, BLANCO)
        pantalla.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))

    def dibujar_nave(x, y, tam):
        fuego = (255, 140, 0) if random.randint(0, 1) else (255, 210, 40)
        pygame.draw.polygon(pantalla, fuego, [
            (x + tam*0.35, y + tam),
            (x + tam*0.65, y + tam),
            (x + tam*0.5, y + tam + 16)
        ])
        pygame.draw.polygon(pantalla, (0, 90, 170), [
            (x, y + tam), (x + tam*0.25, y + tam*0.4), (x + tam*0.25, y + tam)
        ])
        pygame.draw.polygon(pantalla, (0, 90, 170), [
            (x + tam, y + tam), (x + tam*0.75, y + tam*0.4), (x + tam*0.75, y + tam)
        ])
        pygame.draw.polygon(pantalla, (0, 180, 255), [
            (x + tam*0.5, y),
            (x + tam*0.2, y + tam*0.9),
            (x + tam*0.8, y + tam*0.9)
        ])
        pygame.draw.polygon(pantalla, (190, 240, 255), [
            (x + tam*0.5, y + tam*0.28),
            (x + tam*0.37, y + tam*0.58),
            (x + tam*0.63, y + tam*0.58)
        ])

    def reset_game():
        nonlocal puntos, en_pausa, game_over, jugador_x, jugador_y
        nonlocal balas, enemigos, cooldown, tiempo_enemigo
        nonlocal salud, salud_max, nuevo_record

        puntos = 0
        en_pausa = False
        game_over = False
        nuevo_record = False
        salud_max = 10
        salud = 10
        jugador_x = ANCHO // 2 - jugador_tam // 2
        jugador_y = int(ALTO * 0.70)
        cooldown = 0
        tiempo_enemigo = 0
        balas = []
        enemigos = []

    # Inicializar variables de juego
    puntos = 0
    en_pausa = False
    game_over = False
    jugador_x = ANCHO // 2 - jugador_tam // 2
    jugador_y = int(ALTO * 0.70)
    balas = []
    enemigos = []
    cooldown = 0
    tiempo_enemigo = 0
    salud = 10
    salud_max = 10

    # ======================
    # BUCLE PRINCIPAL
    # ======================
    while True:
        reloj.tick(60)
        mover_izq = mover_der = mover_arr = mover_aba = False

        # Estrellas
        for e in estrellas:
            e["y"] += e["vel"]
            if e["y"] > ALTO:
                e["y"] = 0
                e["x"] = random.randint(0, ANCHO)

        # Animación menú
        menu_offset += 0.35 * menu_dir
        if abs(menu_offset) > 11:
            menu_dir *= -1

        # Eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return

            if evento.type == pygame.MOUSEBUTTONDOWN:
                pos = evento.pos

                if estado == "MENU":
                    if mostrar_tutorial:
                        if btn_cerrar_tut.collidepoint(pos):
                            mostrar_tutorial = False
                    else:
                        if btn_iniciar.collidepoint(pos):
                            reset_game()
                            estado = "JUGANDO"
                        elif btn_tutorial.collidepoint(pos):
                            mostrar_tutorial = True
                        elif btn_opciones.collidepoint(pos):
                            estado = "OPCIONES"
                        elif btn_salir.collidepoint(pos):
                            return

                elif estado == "OPCIONES":
                    if btn_modo.collidepoint(pos):
                        tipo_control = "DESLIZAR" if tipo_control == "BOTONES" else "BOTONES"
                    elif btn_layout.collidepoint(pos):
                        orden = ["CLASICO", "LATERALES", "COMPACTO"]
                        tipo_layout = orden[(orden.index(tipo_layout) + 1) % 3]
                        crear_botones_control()
                    elif btn_volver.collidepoint(pos):
                        estado = "MENU"

                elif estado == "JUGANDO":
                    if game_over:
                        if btn_reintentar.collidepoint(pos):
                            reset_game()
                        elif btn_menu_go.collidepoint(pos):
                            estado = "MENU"
                    elif btn_pausa.collidepoint(pos):
                        en_pausa = not en_pausa
                    elif en_pausa:
                        if btn_reanudar.collidepoint(pos):
                            en_pausa = False
                        elif btn_menu_pausa.collidepoint(pos):
                            estado = "MENU"

        # ======================
        # LÓGICA DEL JUEGO
        # ======================
        if estado == "JUGANDO" and not en_pausa and not game_over:

            # Controles
            if tipo_control == "BOTONES":
                if pygame.mouse.get_pressed()[0]:
                    pos = pygame.mouse.get_pos()
                    if btn_izq.collidepoint(pos): mover_izq = True
                    if btn_der.collidepoint(pos): mover_der = True
                    if btn_arr.collidepoint(pos): mover_arr = True
                    if btn_aba.collidepoint(pos): mover_aba = True
            else:  # DESLIZAR
                if pygame.mouse.get_pressed()[0]:
                    pos = pygame.mouse.get_pos()
                    if not btn_pausa.collidepoint(pos):
                        jugador_x += (pos[0] - jugador_tam//2 - jugador_x) * 0.22
                        jugador_y += (pos[1] - jugador_tam//2 - jugador_y) * 0.22

            if mover_izq:
                jugador_x -= velocidad_jugador
            if mover_der:
                jugador_x += velocidad_jugador
            if mover_arr:
                jugador_y -= velocidad_jugador
            if mover_aba:
                jugador_y += velocidad_jugador

            # Límites
            jugador_x = max(0, min(ANCHO - jugador_tam, jugador_x))
            jugador_y = max(int(ALTO * 0.26), min(ALTO - 190, jugador_y))

            # Disparo
            cooldown += 1
            if cooldown >= cadencia:
                balas.append(pygame.Rect(jugador_x + jugador_tam//2 - 3, jugador_y, 7, 16))
                cooldown = 0

            for b in balas[:]:
                b.y -= velocidad_bala
                if b.y < -20:
                    balas.remove(b)

            # Enemigos
            tiempo_enemigo += 1
            if tiempo_enemigo >= 42 and len(enemigos) < max_enemigos:
                ex = random.randint(10, ANCHO - 55)
                tipo = "COMUN"
                if puntos > 400 and random.random() < 0.22:
                    tipo = "KAMIKAZE"
                enemigos.append({
                    "rect": pygame.Rect(ex, -50, 48, 48),
                    "tipo": tipo,
                    "vida": 2 if tipo == "KAMIKAZE" else 1
                })
                tiempo_enemigo = 0

            for e in enemigos[:]:
                if e["tipo"] == "KAMIKAZE":
                    e["rect"].y += int(velocidad_enemigo * 1.45)
                    # persigue un poco
                    if e["rect"].centerx < jugador_x + 20:
                        e["rect"].x += 3
                    elif e["rect"].centerx > jugador_x + 30:
                        e["rect"].x -= 3
                else:
                    e["rect"].y += velocidad_enemigo

                if e["rect"].y > ALTO + 20:
                    enemigos.remove(e)

            # Colisiones
            rect_j = pygame.Rect(jugador_x, jugador_y, jugador_tam, jugador_tam)

            for e in enemigos[:]:
                if rect_j.colliderect(e["rect"]):
                    daño = 4 if e["tipo"] == "KAMIKAZE" else 2
                    salud -= daño
                    enemigos.remove(e)
                    if salud <= 0:
                        salud = 0
                        game_over = True
                        if puntos > high_score:
                            high_score = puntos
                            nuevo_record = True

            for e in enemigos[:]:
                for b in balas[:]:
                    if b.colliderect(e["rect"]):
                        balas.remove(b)
                        e["vida"] -= 1
                        if e["vida"] <= 0:
                            puntos += 15 if e["tipo"] == "KAMIKAZE" else 10
                            enemigos.remove(e)
                        break

        # ======================
        # DIBUJADO
        # ======================
        pantalla.fill(NEGRO)

        for e in estrellas:
            pygame.draw.circle(pantalla, BLANCO, (int(e["x"]), int(e["y"])), e["r"])

        # ----- MENÚ -----
        if estado == "MENU":
            titulo = fuente_titulo.render("ATAQUES ESPACIALES", True, AZUL_NAVE)
            pantalla.blit(titulo, (ANCHO//2 - titulo.get_width()//2, 110))

            hs = fuente_grande.render(f"MEJOR: {high_score}", True, DORADO)
            pantalla.blit(hs, (ANCHO//2 - hs.get_width()//2, 185))

            dibujar_boton(btn_iniciar, "INICIAR JUEGO", VERDE)
            dibujar_boton(btn_tutorial, "CÓMO JUGAR", AZUL_CONFIG)
            dibujar_boton(btn_opciones, "OPCIONES", BOTON_COLOR)
            dibujar_boton(btn_salir, "SALIR", ROJO)

            dibujar_nave(ANCHO//2 - 28, 790 + int(menu_offset), 56)

            if mostrar_tutorial:
                s = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
                s.fill((0, 0, 0, 210))
                pantalla.blit(s, (0, 0))

                panel = pygame.Rect(35, 160, ANCHO - 70, 580)
                pygame.draw.rect(pantalla, (22, 26, 48), panel, border_radius=18)
                pygame.draw.rect(pantalla, AZUL_NAVE, panel, 2, border_radius=18)

                t = fuente_grande.render("CÓMO JUGAR", True, AZUL_NAVE)
                pantalla.blit(t, (panel.centerx - t.get_width()//2, 185))

                lineas = [
                    "• Muévete en 4 direcciones",
                    "• Botones o deslizar el dedo",
                    "",
                    "• Naves naranjas = Kamikaze",
                    "  (hacen más daño)",
                    "",
                    "• Destruye enemigos para puntos",
                    "• Evita chocar",
                    "",
                    "• Cambia el layout en Opciones"
                ]
                y = 250
                for linea in lineas:
                    pantalla.blit(fuente.render(linea, True, BLANCO), (60, y))
                    y += 36

                dibujar_boton(btn_cerrar_tut, "ENTENDIDO", VERDE)

        # ----- OPCIONES -----
        elif estado == "OPCIONES":
            t = fuente_grande.render("OPCIONES", True, AZUL_NAVE)
            pantalla.blit(t, (ANCHO//2 - t.get_width()//2, 170))

            dibujar_boton(btn_modo, f"CONTROL: {tipo_control}", AZUL_CONFIG)
            dibujar_boton(btn_layout, f"LAYOUT: {tipo_layout}", (80, 50, 140))
            dibujar_boton(btn_volver, "VOLVER AL MENÚ", ROJO)

        # ----- JUEGO -----
        elif estado == "JUGANDO":
            # Balas
            for b in balas:
                pygame.draw.rect(pantalla, AMARILLO_BALA, b, border_radius=2)

            # Enemigos
            for e in enemigos:
                color = NARANJA_KAMIKAZE if e["tipo"] == "KAMIKAZE" else ROJO_ENEMIGO
                r = e["rect"]
                pygame.draw.polygon(pantalla, color, [
                    (r.centerx, r.bottom),
                    (r.left, r.top),
                    (r.right, r.top)
                ])

            # Jugador
            dibujar_nave(jugador_x, jugador_y, jugador_tam)

            # Botones de control
            if tipo_control == "BOTONES":
                for b, txt in [(btn_izq, "←"), (btn_der, "→"), (btn_arr, "↑"), (btn_aba, "↓")]:
                    pygame.draw.rect(pantalla, BOTON_COLOR, b, border_radius=12)
                    pygame.draw.rect(pantalla, (90, 90, 130), b, 2, border_radius=12)
                    t = fuente.render(txt, True, BLANCO)
                    pantalla.blit(t, (b.centerx - t.get_width()//2, b.centery - t.get_height()//2))

            # HUD
            pantalla.blit(fuente.render(f"SCORE: {puntos}", True, BLANCO), (16, 16))
            pantalla.blit(fuente.render(f"BEST: {high_score}", True, DORADO), (16, 46))

            # Vida
            for i in range(salud_max):
                color = AZUL_SALUD if i < salud else (45, 45, 65)
                pygame.draw.rect(pantalla, color, (16 + i * 19, 82, 15, 15), border_radius=3)

            # Botón pausa
            pygame.draw.rect(pantalla, BOTON_COLOR, btn_pausa, border_radius=8)
            pygame.draw.rect(pantalla, BLANCO, (btn_pausa.x + 16, btn_pausa.y + 11, 8, 20))
            pygame.draw.rect(pantalla, BLANCO, (btn_pausa.x + 31, btn_pausa.y + 11, 8, 20))

            # Pausas / Game Over
            if en_pausa or game_over:
                s = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
                s.fill(OVERLAY)
                pantalla.blit(s, (0, 0))

                if en_pausa:
                    t = fuente_grande.render("PAUSA", True, BLANCO)
                    pantalla.blit(t, (ANCHO//2 - t.get_width()//2, ALTO//2 - 120))
                    dibujar_boton(btn_reanudar, "REANUDAR", VERDE)
                    dibujar_boton(btn_menu_pausa, "MENÚ PRINCIPAL", ROJO)

                if game_over:
                    t = fuente_grande.render("GAME OVER", True, ROJO_ENEMIGO)
                    pantalla.blit(t, (ANCHO//2 - t.get_width()//2, ALTO//2 - 130))
                    if nuevo_record:
                        r = fuente.render("¡NUEVO RÉCORD!", True, DORADO)
                        pantalla.blit(r, (ANCHO//2 - r.get_width()//2, ALTO//2 - 80))
                    sc = fuente.render(f"Puntaje: {puntos}", True, BLANCO)
                    pantalla.blit(sc, (ANCHO//2 - sc.get_width()//2, ALTO//2 - 45))
                    dibujar_boton(btn_reintentar, "REINTENTAR", VERDE)
                    dibujar_boton(btn_menu_go, "MENÚ PRINCIPAL", ROJO)

        pygame.display.flip()
        await asyncio.sleep(0)

asyncio.run(main())
