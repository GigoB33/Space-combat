import asyncio
import pygame
import random
import sys
import json
import os

# ============================================================
# ATAQUES ESPACIALES - Versión Web optimizada para Pygbag
# ============================================================

try:
    import numpy as np
    AUDIO_HABILITADO = True
except ImportError:
    AUDIO_HABILITADO = False
    np = None

pygame.init()

# Resolución fija (más estable en web)
ANCHO = 540
ALTO = 960

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Ataques Espaciales")

# Colores
NEGRO = (10, 10, 20)
AZUL_NAVE = (0, 200, 255)
AZUL_SALUD = (0, 150, 255)
AZUL_CURACION = (50, 200, 255)
ROJO_ENEMIGO = (255, 60, 60)
NARANJA_KAMIKAZE = (255, 140, 0)
VIOLETA_MINIJEFE = (180, 50, 255)
VERDE_JEFE = (0, 255, 100)
AMARILLO_BALA = (255, 230, 0)
ROJO_BALA_JEFE = (255, 0, 100)
AZUL_ARTILLERO = (50, 150, 255)
AZUL_BALA_ARTILLERO = (80, 220, 255)
BOTON_COLOR = (40, 40, 65)
BLANCO = (255, 255, 255)
VERDE_REANUDAR = (40, 180, 90)
ROJO_SALIR = (200, 50, 50)
AZUL_CONFIG = (30, 120, 200)
DORADO = (255, 200, 50)
OVERLAY_SOMBRA = (0, 0, 0, 180)

# Fuentes (más seguras para web)
fuente = pygame.font.SysFont("arial", 22)
fuente_grande = pygame.font.SysFont("arial", 32)
fuente_titulo = pygame.font.SysFont("arial", 40)
fuente_jefe = pygame.font.SysFont("arial", 18)
fuente_peque = pygame.font.SysFont("arial", 18)

# Configuración
jugador_tam = 55
velocidad_jugador = 8
velocidad_bala = 14
cadencia_disparo = 12
velocidad_enemigo = 5
max_enemigos_pantalla = 6

estado_juego = "MENU"
tipo_control = "BOTONES"
tipo_layout = "COMPACTO"
mostrar_tutorial = False

# High score simple (en web puede no persistir)
high_score = 0
nuevo_record_alcanzado = False

# Sonidos
sonidos = {}

def generar_sonidos():
    if not AUDIO_HABILITADO or np is None:
        return
    try:
        sample_rate = 22050
        def crear(samples):
            samples = np.clip(samples, -1, 1)
            samples = (samples * 32767).astype(np.int16)
            return pygame.sndarray.make_sound(samples)

        t = np.linspace(0, 0.08, int(sample_rate * 0.08), False)
        onda = 0.3 * np.sin(2 * np.pi * np.linspace(800, 200, len(t)) * t) * (1 - t/0.08)
        sonidos["laser"] = crear(onda)

        t = np.linspace(0, 0.12, int(sample_rate * 0.12), False)
        onda = 0.4 * np.sin(2 * np.pi * np.linspace(180, 40, len(t)) * t) * (1 - t/0.12)**2
        sonidos["impacto"] = crear(onda)

        t = np.linspace(0, 0.35, int(sample_rate * 0.35), False)
        onda = 0.5 * np.random.uniform(-1, 1, len(t)) * (1 - t/0.35)**3
        sonidos["explosion"] = crear(onda)
    except Exception:
        pass

generar_sonidos()

def reproducir(nombre):
    if nombre in sonidos:
        try:
            sonidos[nombre].play()
        except:
            pass

def reset_game():
    global puntos, en_pausa, game_over, jugador_x, jugador_y
    global balas, balas_jefe, balas_artillero, orbes_curacion, enemigos
    global cooldown_disparo, tiempo_nuevo_enemigo, jefe_actual
    global salud_barras, salud_maxima, nuevo_record_alcanzado
    global siguiente_umbral_jefe, siguiente_tipo_jefe

    puntos = 0
    en_pausa = False
    game_over = False
    nuevo_record_alcanzado = False
    salud_maxima = 10
    salud_barras = 10
    jugador_x = ANCHO // 2 - jugador_tam // 2
    jugador_y = int(ALTO * 0.72)
    cooldown_disparo = 0
    balas = []
    balas_jefe = []
    balas_artillero = []
    orbes_curacion = []
    enemigos = []
    tiempo_nuevo_enemigo = 0
    jefe_actual = None
    siguiente_umbral_jefe = 1700
    siguiente_tipo_jefe = "MINI_JEFE"

reset_game()

# Botones
btn_m_ancho = int(ANCHO * 0.70)
btn_m_alto = 55
pos_m_x = ANCHO // 2 - btn_m_ancho // 2

btn_iniciar = pygame.Rect(pos_m_x, 340, btn_m_ancho, btn_m_alto)
btn_tutorial = pygame.Rect(pos_m_x, 410, btn_m_ancho, btn_m_alto)
btn_opciones = pygame.Rect(pos_m_x, 480, btn_m_ancho, btn_m_alto)
btn_salir = pygame.Rect(pos_m_x, 550, btn_m_ancho, btn_m_alto)

btn_modo = pygame.Rect(pos_m_x, 360, btn_m_ancho, btn_m_alto)
btn_layout = pygame.Rect(pos_m_x, 440, btn_m_ancho, btn_m_alto)
btn_volver = pygame.Rect(pos_m_x, 540, btn_m_ancho, btn_m_alto)

btn_pausa = pygame.Rect(ANCHO - 70, 15, 55, 40)
btn_reanudar = pygame.Rect(ANCHO//2 - 140, ALTO//2 - 40, 280, 55)
btn_menu_pausa = pygame.Rect(ANCHO//2 - 140, ALTO//2 + 40, 280, 55)
btn_reintentar = pygame.Rect(ANCHO//2 - 140, ALTO//2, 280, 55)
btn_menu_go = pygame.Rect(ANCHO//2 - 140, ALTO//2 + 80, 280, 55)
btn_cerrar_tut = pygame.Rect(ANCHO//2 - 120, 750, 240, 50)

def crear_botones():
    global btn_izq, btn_der, btn_arr, btn_aba
    if tipo_layout == "CLASICO":
        btn_izq = pygame.Rect(0, ALTO-90, ANCHO//2, 90)
        btn_der = pygame.Rect(ANCHO//2, ALTO-90, ANCHO//2, 90)
        btn_arr = pygame.Rect(ANCHO//2-60, ALTO-180, 120, 60)
        btn_aba = pygame.Rect(ANCHO//2-60, ALTO-110, 120, 50)
    elif tipo_layout == "LATERALES":
        btn_izq = pygame.Rect(10, ALTO//2-60, 80, 120)
        btn_der = pygame.Rect(ANCHO-90, ALTO//2-60, 80, 120)
        btn_arr = pygame.Rect(ANCHO//2-50, ALTO-180, 100, 60)
        btn_aba = pygame.Rect(ANCHO//2-50, ALTO-100, 100, 60)
    else:  # COMPACTO
        base = ALTO - 160
        btn_izq = pygame.Rect(20, base, 140, 70)
        btn_der = pygame.Rect(ANCHO-160, base, 140, 70)
        btn_arr = pygame.Rect(ANCHO//2-55, base-80, 110, 60)
        btn_aba = pygame.Rect(ANCHO//2-55, base+10, 110, 55)

crear_botones()

# Estrellas
estrellas = [{"x": random.randint(0, ANCHO), "y": random.randint(0, ALTO),
              "vel": random.uniform(1.5, 4), "radio": random.randint(1, 2)} for _ in range(60)]

reloj = pygame.time.Clock()
menu_offset = 0
menu_dir = 1

def dibujar_boton(rect, texto, color):
    pygame.draw.rect(pantalla, (20, 20, 30), rect.move(3, 3), border_radius=12)
    pygame.draw.rect(pantalla, color, rect, border_radius=12)
    txt = fuente.render(texto, True, BLANCO)
    pantalla.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))

def dibujar_nave(x, y, tam):
    fuego = (255, 120, 0) if random.randint(0,1) else (255, 200, 0)
    pygame.draw.polygon(pantalla, fuego, [(x+tam*0.35, y+tam), (x+tam*0.65, y+tam), (x+tam*0.5, y+tam+18)])
    pygame.draw.polygon(pantalla, (0,100,180), [(x, y+tam), (x+tam*0.25, y+tam*0.4), (x+tam*0.25, y+tam)])
    pygame.draw.polygon(pantalla, (0,100,180), [(x+tam, y+tam), (x+tam*0.75, y+tam*0.4), (x+tam*0.75, y+tam)])
    pygame.draw.polygon(pantalla, (0,180,255), [(x+tam*0.5, y), (x+tam*0.2, y+tam*0.9), (x+tam*0.8, y+tam*0.9)])
    pygame.draw.polygon(pantalla, (200,245,255), [(x+tam*0.5, y+tam*0.3), (x+tam*0.38, y+tam*0.6), (x+tam*0.62, y+tam*0.6)])

async def main():
    global estado_juego, mostrar_tutorial, tipo_control, tipo_layout
    global en_pausa, game_over, puntos, high_score, nuevo_record_alcanzado
    global jugador_x, jugador_y, salud_barras
    global balas, balas_jefe, balas_artillero, orbes_curacion, enemigos
    global cooldown_disparo, tiempo_nuevo_enemigo, jefe_actual
    global siguiente_umbral_jefe, siguiente_tipo_jefe
    global menu_offset, menu_dir

    ejecutando = True

    while ejecutando:
        reloj.tick(60)
        mover_izq = mover_der = mover_arr = mover_aba = False

        for est in estrellas:
            est["y"] += est["vel"]
            if est["y"] > ALTO:
                est["y"] = 0
                est["x"] = random.randint(0, ANCHO)

        menu_offset += 0.4 * menu_dir
        if abs(menu_offset) > 12:
            menu_dir *= -1

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
            if evento.type == pygame.MOUSEBUTTONDOWN:
                pos = evento.pos
                if estado_juego == "MENU":
                    if mostrar_tutorial:
                        if btn_cerrar_tut.collidepoint(pos):
                            mostrar_tutorial = False
                    else:
                        if btn_iniciar.collidepoint(pos):
                            reset_game()
                            estado_juego = "JUGANDO"
                        elif btn_tutorial.collidepoint(pos):
                            mostrar_tutorial = True
                        elif btn_opciones.collidepoint(pos):
                            estado_juego = "OPCIONES"
                        elif btn_salir.collidepoint(pos):
                            ejecutando = False
                elif estado_juego == "OPCIONES":
                    if btn_modo.collidepoint(pos):
                        tipo_control = "DESLIZAR" if tipo_control == "BOTONES" else "BOTONES"
                    elif btn_layout.collidepoint(pos):
                        layouts = ["CLASICO", "LATERALES", "COMPACTO"]
                        tipo_layout = layouts[(layouts.index(tipo_layout) + 1) % 3]
                        crear_botones()
                    elif btn_volver.collidepoint(pos):
                        estado_juego = "MENU"
                elif estado_juego == "JUGANDO":
                    if game_over:
                        if btn_reintentar.collidepoint(pos):
                            reset_game()
                        elif btn_menu_go.collidepoint(pos):
                            estado_juego = "MENU"
                    elif btn_pausa.collidepoint(pos):
                        en_pausa = not en_pausa
                    elif en_pausa:
                        if btn_reanudar.collidepoint(pos):
                            en_pausa = False
                        elif btn_menu_pausa.collidepoint(pos):
                            estado_juego = "MENU"

        # ---- GAMEPLAY ----
        if estado_juego == "JUGANDO" and not en_pausa and not game_over:
            if tipo_control == "BOTONES" and pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                if btn_izq.collidepoint(pos): mover_izq = True
                if btn_der.collidepoint(pos): mover_der = True
                if btn_arr.collidepoint(pos): mover_arr = True
                if btn_aba.collidepoint(pos): mover_aba = True
            elif tipo_control == "DESLIZAR" and pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                if not btn_pausa.collidepoint(pos):
                    jugador_x += (pos[0] - jugador_tam//2 - jugador_x) * 0.2
                    jugador_y += (pos[1] - jugador_tam//2 - jugador_y) * 0.2

            if mover_izq: jugador_x -= velocidad_jugador
            if mover_der: jugador_x += velocidad_jugador
            if mover_arr: jugador_y -= velocidad_jugador
            if mover_aba: jugador_y += velocidad_jugador

            jugador_x = max(0, min(ANCHO - jugador_tam, jugador_x))
            jugador_y = max(int(ALTO*0.28), min(ALTO - 180, jugador_y))

            cooldown_disparo += 1
            if cooldown_disparo >= cadencia_disparo:
                balas.append(pygame.Rect(jugador_x + jugador_tam//2 - 3, jugador_y, 6, 16))
                reproducir("laser")
                cooldown_disparo = 0

            for b in balas[:]:
                b.y -= velocidad_bala
                if b.y < 0: balas.remove(b)

            # Enemigos simples (versión reducida para estabilidad)
            tiempo_nuevo_enemigo += 1
            if tiempo_nuevo_enemigo >= 45 and len(enemigos) < max_enemigos_pantalla:
                ex = random.randint(0, ANCHO - 45)
                enemigos.append({"rect": pygame.Rect(ex, -45, 45, 45), "vida": 1, "tipo": "COMUN"})
                tiempo_nuevo_enemigo = 0

            for e in enemigos[:]:
                e["rect"].y += velocidad_enemigo
                if e["rect"].y > ALTO:
                    enemigos.remove(e)

            # Colisiones básicas
            rect_j = pygame.Rect(jugador_x, jugador_y, jugador_tam, jugador_tam)
            for e in enemigos[:]:
                if rect_j.colliderect(e["rect"]):
                    salud_barras -= 2
                    reproducir("impacto")
                    enemigos.remove(e)
                    if salud_barras <= 0:
                        game_over = True
                        if puntos > high_score:
                            high_score = puntos
                            nuevo_record_alcanzado = True

            for e in enemigos[:]:
                for b in balas[:]:
                    if b.colliderect(e["rect"]):
                        balas.remove(b)
                        e["vida"] -= 1
                        if e["vida"] <= 0:
                            puntos += 10
                            reproducir("impacto")
                            enemigos.remove(e)
                        break

        # ---- RENDER ----
        pantalla.fill(NEGRO)
        for est in estrellas:
            pygame.draw.circle(pantalla, BLANCO, (int(est["x"]), int(est["y"])), est["radio"])

        if estado_juego == "MENU":
            titulo = fuente_titulo.render("ATAQUES ESPACIALES", True, AZUL_NAVE)
            pantalla.blit(titulo, (ANCHO//2 - titulo.get_width()//2, 120))
            hs = fuente_grande.render(f"MEJOR: {high_score}", True, DORADO)
            pantalla.blit(hs, (ANCHO//2 - hs.get_width()//2, 200))

            dibujar_boton(btn_iniciar, "INICIAR JUEGO", VERDE_REANUDAR)
            dibujar_boton(btn_tutorial, "CÓMO JUGAR", AZUL_CONFIG)
            dibujar_boton(btn_opciones, "OPCIONES", BOTON_COLOR)
            dibujar_boton(btn_salir, "SALIR", ROJO_SALIR)

            dibujar_nave(ANCHO//2 - 30, 780 + int(menu_offset), 60)

            if mostrar_tutorial:
                s = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
                s.fill((0,0,0,200))
                pantalla.blit(s, (0,0))
                panel = pygame.Rect(40, 180, ANCHO-80, 520)
                pygame.draw.rect(pantalla, (25,28,50), panel, border_radius=16)
                t = fuente_grande.render("CÓMO JUGAR", True, AZUL_NAVE)
                pantalla.blit(t, (panel.centerx - t.get_width()//2, 200))
                lineas = [
                    "• Muévete con botones o deslizando",
                    "• Destruye las naves enemigas",
                    "• Evita chocar",
                    "• ¡Consigue la mayor puntuación!"
                ]
                y = 280
                for l in lineas:
                    pantalla.blit(fuente.render(l, True, BLANCO), (70, y))
                    y += 40
                dibujar_boton(btn_cerrar_tut, "ENTENDIDO", VERDE_REANUDAR)

        elif estado_juego == "OPCIONES":
            t = fuente_grande.render("OPCIONES", True, AZUL_NAVE)
            pantalla.blit(t, (ANCHO//2 - t.get_width()//2, 180))
            dibujar_boton(btn_modo, f"CONTROL: {tipo_control}", AZUL_CONFIG)
            dibujar_boton(btn_layout, f"LAYOUT: {tipo_layout}", (70,50,140))
            dibujar_boton(btn_volver, "VOLVER", ROJO_SALIR)

        elif estado_juego == "JUGANDO":
            for b in balas:
                pygame.draw.rect(pantalla, AMARILLO_BALA, b)
            for e in enemigos:
                pygame.draw.polygon(pantalla, ROJO_ENEMIGO, [
                    (e["rect"].centerx, e["rect"].bottom),
                    (e["rect"].left, e["rect"].top),
                    (e["rect"].right, e["rect"].top)
                ])
            dibujar_nave(jugador_x, jugador_y, jugador_tam)

            if tipo_control == "BOTONES":
                for b, txt in [(btn_izq,"←"), (btn_der,"→"), (btn_arr,"↑"), (btn_aba,"↓")]:
                    pygame.draw.rect(pantalla, BOTON_COLOR, b, border_radius=10)
                    t = fuente.render(txt, True, BLANCO)
                    pantalla.blit(t, (b.centerx-t.get_width()//2, b.centery-t.get_height()//2))

            pantalla.blit(fuente.render(f"SCORE: {puntos}", True, BLANCO), (15, 15))
            pantalla.blit(fuente.render(f"BEST: {high_score}", True, DORADO), (15, 45))
            # Vida
            for i in range(salud_maxima):
                color = AZUL_SALUD if i < salud_barras else (40,40,60)
                pygame.draw.rect(pantalla, color, (15 + i*18, 80, 14, 14), border_radius=2)

            pygame.draw.rect(pantalla, BOTON_COLOR, btn_pausa, border_radius=6)
            pygame.draw.rect(pantalla, BLANCO, (btn_pausa.x+15, btn_pausa.y+10, 8, 20))
            pygame.draw.rect(pantalla, BLANCO, (btn_pausa.x+32, btn_pausa.y+10, 8, 20))

            if en_pausa or game_over:
                s = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
                s.fill(OVERLAY_SOMBRA)
                pantalla.blit(s, (0,0))
                if en_pausa:
                    t = fuente_grande.render("PAUSA", True, BLANCO)
                    pantalla.blit(t, (ANCHO//2-t.get_width()//2, ALTO//2-120))
                    dibujar_boton(btn_reanudar, "REANUDAR", VERDE_REANUDAR)
                    dibujar_boton(btn_menu_pausa, "MENÚ", ROJO_SALIR)
                if game_over:
                    t = fuente_grande.render("GAME OVER", True, ROJO_ENEMIGO)
                    pantalla.blit(t, (ANCHO//2-t.get_width()//2, ALTO//2-120))
                    if nuevo_record_alcanzado:
                        r = fuente.render("¡NUEVO RÉCORD!", True, DORADO)
                        pantalla.blit(r, (ANCHO//2-r.get_width()//2, ALTO//2-70))
                    dibujar_boton(btn_reintentar, "REINTENTAR", VERDE_REANUDAR)
                    dibujar_boton(btn_menu_go, "MENÚ", ROJO_SALIR)

        pygame.display.flip()
        await asyncio.sleep(0)

    pygame.quit()

asyncio.run(main())
