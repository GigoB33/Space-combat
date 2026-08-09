import asyncio
import pygame
import random
import sys
import json
import os
import math

# ============================================================
# ATAQUES ESPACIALES - Versión Web (Pygbag)
# ============================================================

try:
    import numpy as np
    AUDIO_HABILITADO = True
except ImportError:
    AUDIO_HABILITADO = False

try:
    from plyer import vibrator
    VIBRACION_DISPONIBLE = True
except Exception:
    VIBRACION_DISPONIBLE = False


def vibrar(duracion_segundos):
    if VIBRACION_DISPONIBLE:
        try:
            vibrator.vibrate(duracion_segundos)
        except Exception:
            pass


try:
    pygame.mixer.pre_init(44100, -16, 1, 512)
except Exception:
    pass

pygame.init()

sonidos = {}


def generar_sonidos_sinteticos():
    if not AUDIO_HABILITADO:
        return

    sample_rate = 44100

    def crear_sound(samples):
        samples = np.clip(samples, -1.0, 1.0)
        samples = (samples * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(samples)

    duracion = 0.08
    t = np.linspace(0, duracion, int(sample_rate * duracion), False)
    freq = np.linspace(800, 200, len(t))
    fase = 2 * np.pi * np.cumsum(freq) / sample_rate
    onda = 0.3 * np.sin(fase) * (1 - t / duracion)
    sonidos['laser'] = crear_sound(onda)

    duracion = 0.12
    t = np.linspace(0, duracion, int(sample_rate * duracion), False)
    freq = np.linspace(180, 40, len(t))
    fase = 2 * np.pi * np.cumsum(freq) / sample_rate
    onda = 0.5 * np.sin(fase) * (1 - t / duracion) ** 2
    sonidos['impacto'] = crear_sound(onda)

    duracion = 0.18
    t = np.linspace(0, duracion, int(sample_rate * duracion), False)
    freq = np.linspace(300, 900, len(t))
    fase = 2 * np.pi * np.cumsum(freq) / sample_rate
    onda = 0.4 * np.sin(fase) * (1 - t / duracion)
    sonidos['curacion'] = crear_sound(onda)

    duracion = 0.35
    t = np.linspace(0, duracion, int(sample_rate * duracion), False)
    ruido = np.random.uniform(-1, 1, len(t))
    envolvente = (1 - t / duracion) ** 3
    onda = 0.5 * ruido * envolvente
    sonidos['explosion'] = crear_sound(onda)


generar_sonidos_sinteticos()


def reproducir_sonido(nombre):
    if AUDIO_HABILITADO and nombre in sonidos:
        try:
            sonidos[nombre].play()
        except Exception:
            pass


# ------------------------------------------------------------
# HIGH SCORE
# ------------------------------------------------------------

ARCHIVO_HS = "highscore.json"


def cargar_high_score():
    if os.path.exists(ARCHIVO_HS):
        try:
            with open(ARCHIVO_HS, "r") as archivo:
                datos = json.load(archivo)
                return datos.get("high_score", 0)
        except Exception:
            return 0
    return 0


def guardar_high_score(nuevo_record):
    try:
        with open(ARCHIVO_HS, "w") as archivo:
            json.dump({"high_score": nuevo_record}, archivo)
    except Exception:
        pass


high_score = cargar_high_score()
nuevo_record_alcanzado = False


# ------------------------------------------------------------
# PANTALLA
# ------------------------------------------------------------

info_pantalla = pygame.display.Info()
ANCHO = info_pantalla.current_w if info_pantalla.current_w > 0 else 540
ALTO = info_pantalla.current_h if info_pantalla.current_h > 0 else 960

# En web a veces es mejor forzar un tamaño más controlado
if ANCHO < 300 or ALTO < 400:
    ANCHO, ALTO = 540, 960

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Ataques Espaciales")


# ------------------------------------------------------------
# COLORES
# ------------------------------------------------------------

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
VERDE_REINTENTAR = (40, 180, 90)
ROJO_SALIR = (200, 50, 50)
AZUL_CONFIG = (30, 120, 200)
OVERLAY_SOMBRA = (0, 0, 0, 180)
DORADO = (255, 200, 50)


# ------------------------------------------------------------
# CONFIGURACIÓN
# ------------------------------------------------------------

alto_boton = int(ALTO * 0.11)
jugador_tam = int(ANCHO * 0.11)
velocidad_jugador = int(ANCHO * 0.017)
velocidad_bala = int(ALTO * 0.018)
cadencia_disparo = 12
velocidad_enemigo = int(ALTO * 0.006)
max_enemigos_pantalla = 6

estado_juego = 'MENU'
tipo_control = 'BOTONES'
tipo_layout = 'COMPACTO'
mostrar_tutorial = False


# ------------------------------------------------------------
# RESET DEL JUEGO
# ------------------------------------------------------------

def reset_game():
    global puntos, en_pausa, game_over, jugador_x, jugador_y
    global balas, balas_jefe, balas_artillero
    global cooldown_disparo, cooldown_jefe
    global enemigos, tiempo_nuevo_enemigo
    global jefe_actual
    global salud_barras, salud_maxima
    global orbes_curacion
    global nuevo_record_alcanzado
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
    cooldown_jefe = 0

    balas = []
    balas_jefe = []
    balas_artillero = []
    orbes_curacion = []
    enemigos = []
    tiempo_nuevo_enemigo = 0

    jefe_actual = None

    siguiente_umbral_jefe = 1700
    siguiente_tipo_jefe = 'MINI_JEFE'


reset_game()


# ------------------------------------------------------------
# BOTONES MENÚ
# ------------------------------------------------------------

btn_m_ancho = int(ANCHO * 0.68)
btn_m_alto = int(ALTO * 0.065)
pos_m_x = ANCHO // 2 - btn_m_ancho // 2

btn_iniciar_rect = pygame.Rect(pos_m_x, int(ALTO * 0.36), btn_m_ancho, btn_m_alto)
btn_tutorial_rect = pygame.Rect(pos_m_x, int(ALTO * 0.445), btn_m_ancho, btn_m_alto)
btn_opciones_rect = pygame.Rect(pos_m_x, int(ALTO * 0.53), btn_m_ancho, btn_m_alto)
btn_salir_rect = pygame.Rect(pos_m_x, int(ALTO * 0.615), btn_m_ancho, btn_m_alto)

btn_modo_control_rect = pygame.Rect(pos_m_x, int(ALTO * 0.38), btn_m_ancho, btn_m_alto)
btn_layout_rect = pygame.Rect(pos_m_x, int(ALTO * 0.48), btn_m_ancho, btn_m_alto)
btn_volver_opciones_rect = pygame.Rect(pos_m_x, int(ALTO * 0.62), btn_m_ancho, btn_m_alto)

btn_p_ancho = int(ANCHO * 0.12)
btn_p_alto = int(ALTO * 0.05)

btn_pausa_rect = pygame.Rect(ANCHO - btn_p_ancho - int(ANCHO * 0.03), int(ALTO * 0.015), btn_p_ancho, btn_p_alto)

btn_r_ancho = int(ANCHO * 0.6)
btn_r_alto = int(ALTO * 0.07)

btn_reanudar_rect = pygame.Rect(ANCHO//2 - btn_r_ancho//2, ALTO//2 - int(ALTO*0.05), btn_r_ancho, btn_r_alto)
btn_menu_pausa_rect = pygame.Rect(ANCHO//2 - btn_r_ancho//2, ALTO//2 + int(ALTO*0.05), btn_r_ancho, btn_r_alto)
btn_reintentar_rect = pygame.Rect(ANCHO//2 - btn_r_ancho//2, ALTO//2, btn_r_ancho, btn_r_alto)
btn_menu_go_rect = pygame.Rect(ANCHO//2 - btn_r_ancho//2, ALTO//2 + int(ALTO*0.09), btn_r_ancho, btn_r_alto)

btn_cerrar_tutorial = pygame.Rect(ANCHO//2 - int(ANCHO*0.25), int(ALTO*0.78), int(ANCHO*0.5), int(ALTO*0.06))


# ------------------------------------------------------------
# BOTONES DE CONTROL
# ------------------------------------------------------------

def crear_botones_control():
    global btn_izq, btn_der, btn_arr, btn_aba

    if tipo_layout == 'CLASICO':
        btn_izq = pygame.Rect(0, ALTO - alto_boton, ANCHO // 2, alto_boton)
        btn_der = pygame.Rect(ANCHO // 2, ALTO - alto_boton, ANCHO // 2, alto_boton)
        btn_arr = pygame.Rect(ANCHO // 2 - int(ANCHO*0.12), ALTO - alto_boton*2 - 8, int(ANCHO*0.24), int(alto_boton*0.7))
        btn_aba = pygame.Rect(ANCHO // 2 - int(ANCHO*0.12), ALTO - alto_boton - 4, int(ANCHO*0.24), int(alto_boton*0.55))

    elif tipo_layout == 'LATERALES':
        btn_izq = pygame.Rect(8, ALTO//2 - int(ALTO*0.08), int(ANCHO*0.18), int(ALTO*0.16))
        btn_der = pygame.Rect(ANCHO - int(ANCHO*0.18) - 8, ALTO//2 - int(ALTO*0.08), int(ANCHO*0.18), int(ALTO*0.16))
        btn_arr = pygame.Rect(ANCHO//2 - int(ANCHO*0.1), ALTO - int(ALTO*0.22), int(ANCHO*0.2), int(ALTO*0.08))
        btn_aba = pygame.Rect(ANCHO//2 - int(ANCHO*0.1), ALTO - int(ALTO*0.12), int(ANCHO*0.2), int(ALTO*0.08))

    else:  # COMPACTO
        base_y = ALTO - int(ALTO * 0.195)
        btn_izq = pygame.Rect(int(ANCHO*0.04), base_y, int(ANCHO*0.28), int(ALTO*0.085))
        btn_der = pygame.Rect(ANCHO - int(ANCHO*0.32), base_y, int(ANCHO*0.28), int(ALTO*0.085))
        btn_arr = pygame.Rect(ANCHO//2 - int(ANCHO*0.11), base_y - int(ALTO*0.09), int(ANCHO*0.22), int(ALTO*0.075))
        btn_aba = pygame.Rect(ANCHO//2 - int(ANCHO*0.11), base_y + int(ALTO*0.01), int(ANCHO*0.22), int(ALTO*0.07))


crear_botones_control()


# ------------------------------------------------------------
# FUENTES
# ------------------------------------------------------------

tam_f_normal = int(ALTO * 0.028)
tam_f_grande = int(ALTO * 0.045)
tam_f_titulo = int(ALTO * 0.058)
tam_f_jefe = int(ALTO * 0.022)
tam_f_peque = int(ALTO * 0.022)

fuente = pygame.font.SysFont(None, tam_f_normal)
fuente_grande = pygame.font.SysFont(None, tam_f_grande)
fuente_titulo = pygame.font.SysFont(None, tam_f_titulo)
fuente_jefe = pygame.font.SysFont(None, tam_f_jefe)
fuente_peque = pygame.font.SysFont(None, tam_f_peque)


# ------------------------------------------------------------
# ESTRELLAS + ANIMACIÓN MENÚ
# ------------------------------------------------------------

estrellas = []
for _ in range(70):
    estrellas.append({
        'x': random.randint(0, ANCHO),
        'y': random.randint(0, ALTO),
        'vel': random.uniform(ALTO * 0.002, ALTO * 0.005),
        'radio': max(1, int(ANCHO * 0.004))
    })

reloj = pygame.time.Clock()
menu_nave_offset = 0
menu_nave_dir = 1


# ------------------------------------------------------------
# FUNCIONES DE DIBUJO
# ------------------------------------------------------------

def dibujar_nave_jugador(pantalla, x, y, tam):
    AZUL_CUERPO = (0, 180, 255)
    AZUL_OSCURO = (0, 100, 180)
    BLANCO_CABINA = (200, 245, 255)
    ROJO_DETALLE = (255, 50, 80)
    FUEGO_MOTOR = (255, 120, 0) if random.randint(0, 1) == 0 else (255, 200, 0)

    p_motor1 = (x + tam * 0.35, y + tam)
    p_motor2 = (x + tam * 0.65, y + tam)
    p_fuego = (x + tam * 0.5, y + tam + random.randint(int(tam * 0.15), int(tam * 0.3)))

    pygame.draw.polygon(pantalla, FUEGO_MOTOR, [p_motor1, p_motor2, p_fuego])

    ala_izq = [(x, y + tam), (x + tam * 0.25, y + tam * 0.4), (x + tam * 0.25, y + tam)]
    ala_der = [(x + tam, y + tam), (x + tam * 0.75, y + tam * 0.4), (x + tam * 0.75, y + tam)]
    pygame.draw.polygon(pantalla, AZUL_OSCURO, ala_izq)
    pygame.draw.polygon(pantalla, AZUL_OSCURO, ala_der)

    punta = (x + tam * 0.5, y)
    esq_izq = (x + tam * 0.2, y + tam * 0.9)
    esq_der = (x + tam * 0.8, y + tam * 0.9)
    pygame.draw.polygon(pantalla, AZUL_CUERPO, [punta, esq_izq, esq_der])

    pygame.draw.circle(pantalla, ROJO_DETALLE, (int(x + tam * 0.1), int(y + tam * 0.85)), max(2, int(tam * 0.06)))
    pygame.draw.circle(pantalla, ROJO_DETALLE, (int(x + tam * 0.9), int(y + tam * 0.85)), max(2, int(tam * 0.06)))

    cabina_p1 = (x + tam * 0.5, y + tam * 0.3)
    cabina_p2 = (x + tam * 0.38, y + tam * 0.6)
    cabina_p3 = (x + tam * 0.62, y + tam * 0.6)
    pygame.draw.polygon(pantalla, BLANCO_CABINA, [cabina_p1, cabina_p2, cabina_p3])


def dibujar_nave_enemiga(pantalla, x, y, tam, color, tipo='COMUN'):
    if tipo == 'COMUN':
        p1 = (x + tam * 0.5, y + tam)
        p2 = (x, y)
        p3 = (x + tam, y)
        pygame.draw.polygon(pantalla, color, [p1, p2, p3])
        pygame.draw.polygon(pantalla, (min(255, color[0]+40), min(255, color[1]+40), min(255, color[2]+40)),
                            [(x + tam*0.5, y + tam*0.7), (x + tam*0.3, y + tam*0.25), (x + tam*0.7, y + tam*0.25)])
    elif tipo == 'ARTILLERO':
        cuerpo = pygame.Rect(x + tam*0.15, y + tam*0.15, tam*0.7, tam*0.7)
        pygame.draw.rect(pantalla, color, cuerpo, border_radius=4)
        pygame.draw.rect(pantalla, (30, 90, 180), (x, y + tam*0.35, tam*0.18, tam*0.3))
        pygame.draw.rect(pantalla, (30, 90, 180), (x + tam*0.82, y + tam*0.35, tam*0.18, tam*0.3))
        pygame.draw.rect(pantalla, (180, 230, 255), (x + tam*0.3, y + tam*0.05, tam*0.4, tam*0.15))
    elif tipo == 'KAMIKAZE':
        puntos = [(x + tam*0.5, y + tam), (x, y + tam*0.3), (x + tam*0.2, y), (x + tam*0.8, y), (x + tam, y + tam*0.3)]
        pygame.draw.polygon(pantalla, color, puntos)
        pygame.draw.circle(pantalla, (255, 220, 100), (int(x + tam*0.35), int(y + tam*0.35)), max(2, int(tam*0.08)))
        pygame.draw.circle(pantalla, (255, 220, 100), (int(x + tam*0.65), int(y + tam*0.35)), max(2, int(tam*0.08)))
    else:
        p1 = (x, y)
        p2 = (x + tam, y)
        p3 = (x + tam // 2, y + tam)
        pygame.draw.polygon(pantalla, color, [p1, p2, p3])


def dibujar_jefe(pantalla, jefe):
    rect = jefe['rect']
    x, y, w, h = rect.x, rect.y, rect.width, rect.height
    color = jefe['color']
    tipo = jefe['tipo']
    fase = jefe.get('fase', 1)

    if tipo == 'MINI_JEFE':
        pygame.draw.rect(pantalla, color, rect, border_radius=6)
        pygame.draw.polygon(pantalla, (140, 30, 220), [(x, y + h*0.3), (x - w*0.28, y + h*0.5), (x, y + h*0.7)])
        pygame.draw.polygon(pantalla, (140, 30, 220), [(x + w, y + h*0.3), (x + w + w*0.28, y + h*0.5), (x + w, y + h*0.7)])
        nucleo_color = (255, 180, 255) if fase == 1 else (255, 80, 180)
        pygame.draw.circle(pantalla, nucleo_color, (rect.centerx, rect.centery), max(6, int(w * 0.18)))
        pygame.draw.rect(pantalla, (100, 20, 160), (x + w*0.2, y - h*0.15, w*0.6, h*0.2), border_radius=3)
    else:
        pygame.draw.rect(pantalla, color, rect, border_radius=8)
        pygame.draw.polygon(pantalla, (0, 180, 70), [(x + w*0.15, y), (x + w*0.5, y - h*0.4), (x + w*0.85, y)])
        pygame.draw.rect(pantalla, (0, 140, 60), (x - w*0.12, y + h*0.25, w*0.15, h*0.5), border_radius=3)
        pygame.draw.rect(pantalla, (0, 140, 60), (x + w*0.97, y + h*0.25, w*0.15, h*0.5), border_radius=3)
        if fase == 1: nucleo = (150, 255, 180)
        elif fase == 2: nucleo = (255, 255, 100)
        else: nucleo = (255, 80, 50)
        pygame.draw.circle(pantalla, nucleo, (rect.centerx, rect.centery), max(8, int(w * 0.16)))
        pygame.draw.circle(pantalla, BLANCO, (rect.centerx, rect.centery), max(3, int(w * 0.07)))


def dibujar_barra_vida(pantalla, rect, vida_actual, vida_max):
    largo = rect.width
    alto = max(4, int(ALTO * 0.008))
    x = rect.x
    y = rect.y - int(ALTO * 0.015)
    porcentaje = max(0, vida_actual / vida_max)
    pygame.draw.rect(pantalla, (100, 0, 0), (x, y, largo, alto))
    pygame.draw.rect(pantalla, (0, 255, 0), (x, y, int(largo * porcentaje), alto))


def dibujar_salud_jugador(pantalla, barras_actuales, barras_maxima):
    ancho_barra = int(ANCHO * 0.02)
    alto_barra = int(ALTO * 0.018)
    espaciado = int(ANCHO * 0.006)
    pos_x_inicio = int(ANCHO * 0.03)
    pos_y = int(ALTO * 0.055)

    for i in range(barras_maxima):
        x = pos_x_inicio + i * (ancho_barra + espaciado)
        rect_b = pygame.Rect(x, pos_y, ancho_barra, alto_barra)
        if i < barras_actuales:
            pygame.draw.rect(pantalla, AZUL_SALUD, rect_b, border_radius=2)
            pygame.draw.rect(pantalla, BLANCO, rect_b, 1, border_radius=2)
        else:
            pygame.draw.rect(pantalla, (40, 40, 60), rect_b, border_radius=2)


def dibujar_boton(pantalla, rect, texto, color_base, color_texto=BLANCO):
    sombra = rect.copy()
    sombra.x += 3
    sombra.y += 3
    pygame.draw.rect(pantalla, (20, 20, 30), sombra, border_radius=12)
    pygame.draw.rect(pantalla, color_base, rect, border_radius=12)
    pygame.draw.rect(pantalla, (255, 255, 255, 40), rect, width=2, border_radius=12)
    txt = fuente.render(texto, True, color_texto)
    pantalla.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))


def dibujar_boton_control(pantalla, rect, texto):
    pygame.draw.rect(pantalla, BOTON_COLOR, rect, border_radius=10)
    pygame.draw.rect(pantalla, (80, 80, 120), rect, width=2, border_radius=10)
    txt = fuente_peque.render(texto, True, BLANCO)
    pantalla.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))


# ============================================================
# BUCLE PRINCIPAL ASYNC (para Pygbag)
# ============================================================

async def main():
    global ejecutando, estado_juego, mostrar_tutorial, tipo_control, tipo_layout
    global en_pausa, game_over, puntos, high_score, nuevo_record_alcanzado
    global jugador_x, jugador_y, salud_barras
    global balas, balas_jefe, balas_artillero, orbes_curacion, enemigos
    global cooldown_disparo, tiempo_nuevo_enemigo, jefe_actual
    global siguiente_umbral_jefe, siguiente_tipo_jefe
    global menu_nave_offset, menu_nave_dir

    ejecutando = True

    while ejecutando:
        reloj.tick(60)

        mover_izq = mover_der = mover_arr = mover_aba = False

        limite_y_arriba = int(ALTO * 0.28)
        limite_y_abajo = ALTO - int(ALTO * 0.22)

        for est in estrellas:
            est['y'] += est['vel']
            if est['y'] >= ALTO:
                est['y'] = 0
                est['x'] = random.randint(0, ANCHO)

        menu_nave_offset += 0.35 * menu_nave_dir
        if menu_nave_offset > 12:
            menu_nave_dir = -1
        elif menu_nave_offset < -12:
            menu_nave_dir = 1

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False

            if evento.type == pygame.MOUSEBUTTONDOWN:
                pos_click = evento.pos

                if estado_juego == 'MENU':
                    if mostrar_tutorial:
                        if btn_cerrar_tutorial.collidepoint(pos_click):
                            mostrar_tutorial = False
                    else:
                        if btn_iniciar_rect.collidepoint(pos_click):
                            reset_game()
                            estado_juego = 'JUGANDO'
                        elif btn_tutorial_rect.collidepoint(pos_click):
                            mostrar_tutorial = True
                        elif btn_opciones_rect.collidepoint(pos_click):
                            estado_juego = 'OPCIONES'
                        elif btn_salir_rect.collidepoint(pos_click):
                            ejecutando = False

                elif estado_juego == 'OPCIONES':
                    if btn_modo_control_rect.collidepoint(pos_click):
                        tipo_control = 'DESLIZAR' if tipo_control == 'BOTONES' else 'BOTONES'
                    elif btn_layout_rect.collidepoint(pos_click):
                        if tipo_layout == 'CLASICO':
                            tipo_layout = 'LATERALES'
                        elif tipo_layout == 'LATERALES':
                            tipo_layout = 'COMPACTO'
                        else:
                            tipo_layout = 'CLASICO'
                        crear_botones_control()
                    elif btn_volver_opciones_rect.collidepoint(pos_click):
                        estado_juego = 'MENU'

                elif estado_juego == 'JUGANDO':
                    if game_over:
                        if btn_reintentar_rect.collidepoint(pos_click):
                            reset_game()
                        elif btn_menu_go_rect.collidepoint(pos_click):
                            estado_juego = 'MENU'
                    elif btn_pausa_rect.collidepoint(pos_click):
                        en_pausa = not en_pausa
                    elif en_pausa:
                        if btn_reanudar_rect.collidepoint(pos_click):
                            en_pausa = False
                        elif btn_menu_pausa_rect.collidepoint(pos_click):
                            estado_juego = 'MENU'

        # ========================================================
        # GAMEPLAY
        # ========================================================

        if estado_juego == 'JUGANDO' and not en_pausa and not game_over:

            if tipo_control == 'BOTONES':
                if pygame.mouse.get_pressed()[0]:
                    pos_touch = pygame.mouse.get_pos()
                    if btn_izq.collidepoint(pos_touch):
                        mover_izq = True
                    if btn_der.collidepoint(pos_touch):
                        mover_der = True
                    if btn_arr.collidepoint(pos_touch):
                        mover_arr = True
                    if btn_aba.collidepoint(pos_touch):
                        mover_aba = True

            elif tipo_control == 'DESLIZAR':
                if pygame.mouse.get_pressed()[0]:
                    pos_touch = pygame.mouse.get_pos()
                    if not btn_pausa_rect.collidepoint(pos_touch):
                        objetivo_x = pos_touch[0] - jugador_tam // 2
                        objetivo_y = pos_touch[1] - jugador_tam // 2
                        jugador_x += (objetivo_x - jugador_x) * 0.22
                        jugador_y += (objetivo_y - jugador_y) * 0.22

            if mover_izq and jugador_x > 0:
                jugador_x -= velocidad_jugador
            if mover_der and jugador_x < ANCHO - jugador_tam:
                jugador_x += velocidad_jugador
            if mover_arr and jugador_y > limite_y_arriba:
                jugador_y -= velocidad_jugador
            if mover_aba and jugador_y < limite_y_abajo:
                jugador_y += velocidad_jugador

            jugador_x = max(0, min(ANCHO - jugador_tam, jugador_x))
            jugador_y = max(limite_y_arriba, min(limite_y_abajo, jugador_y))

            cooldown_disparo += 1
            if cooldown_disparo >= cadencia_disparo:
                bala_x = jugador_x + jugador_tam // 2 - int(ANCHO * 0.006)
                balas.append(pygame.Rect(bala_x, jugador_y, int(ANCHO * 0.012), int(ALTO * 0.02)))
                reproducir_sonido('laser')
                cooldown_disparo = 0

            for bala in balas[:]:
                bala.y -= velocidad_bala
                if bala.y < 0:
                    balas.remove(bala)

            for orb in orbes_curacion[:]:
                orb['rect'].y += int(ALTO * 0.004)
                if orb['rect'].y > ALTO:
                    orbes_curacion.remove(orb)

            if jefe_actual is None and puntos >= siguiente_umbral_jefe:
                if siguiente_tipo_jefe == 'MINI_JEFE':
                    jefe_actual = {
                        'rect': pygame.Rect(ANCHO//2 - int(ANCHO*0.11), int(ALTO*0.06), int(ANCHO*0.22), int(ALTO*0.065)),
                        'vida': 6, 'vida_max': 6, 'tipo': 'MINI_JEFE', 'color': VIOLETA_MINIJEFE,
                        'vel_x': int(ANCHO*0.007), 'fase': 1, 'cooldown_disparo': 0
                    }
                else:
                    jefe_actual = {
                        'rect': pygame.Rect(ANCHO//2 - int(ANCHO*0.14), int(ALTO*0.05), int(ANCHO*0.28), int(ALTO*0.09)),
                        'vida': 14, 'vida_max': 14, 'tipo': 'JEFE_REAL', 'color': VERDE_JEFE,
                        'vel_x': int(ANCHO*0.009), 'fase': 1, 'cooldown_disparo': 0
                    }

            if jefe_actual:
                vida_pct = jefe_actual['vida'] / jefe_actual['vida_max']
                if jefe_actual['tipo'] == 'MINI_JEFE':
                    jefe_actual['fase'] = 1 if vida_pct > 0.5 else 2
                else:
                    if vida_pct > 0.66: jefe_actual['fase'] = 1
                    elif vida_pct > 0.33: jefe_actual['fase'] = 2
                    else: jefe_actual['fase'] = 3

                jefe_actual['rect'].x += jefe_actual['vel_x']
                if jefe_actual['rect'].right >= ANCHO or jefe_actual['rect'].left <= 0:
                    jefe_actual['vel_x'] *= -1

                if jefe_actual['tipo'] == 'MINI_JEFE' and jefe_actual['fase'] == 2:
                    if abs(jefe_actual['vel_x']) < int(ANCHO * 0.011):
                        jefe_actual['vel_x'] = int(ANCHO * 0.011) * (1 if jefe_actual['vel_x'] > 0 else -1)

                if jefe_actual['tipo'] == 'JEFE_REAL' and jefe_actual['fase'] == 3:
                    if random.random() < 0.02:
                        jefe_actual['vel_x'] *= -1

                jefe_actual['cooldown_disparo'] += 1

                if jefe_actual['tipo'] == 'MINI_JEFE':
                    cadencia = 55 if jefe_actual['fase'] == 1 else 32
                    if jefe_actual['cooldown_disparo'] >= cadencia:
                        bx = jefe_actual['rect'].centerx - int(ANCHO * 0.007)
                        balas_jefe.append(pygame.Rect(bx, jefe_actual['rect'].bottom, int(ANCHO*0.014), int(ALTO*0.02)))
                        jefe_actual['cooldown_disparo'] = 0
                else:
                    if jefe_actual['fase'] == 1:
                        if jefe_actual['cooldown_disparo'] >= 45:
                            bx = jefe_actual['rect'].centerx - int(ANCHO*0.008)
                            balas_jefe.append(pygame.Rect(bx, jefe_actual['rect'].bottom, int(ANCHO*0.016), int(ALTO*0.022)))
                            jefe_actual['cooldown_disparo'] = 0
                    elif jefe_actual['fase'] == 2:
                        if jefe_actual['cooldown_disparo'] >= 38:
                            cx = jefe_actual['rect'].centerx
                            by = jefe_actual['rect'].bottom
                            balas_jefe.append(pygame.Rect(cx - int(ANCHO*0.035), by, int(ANCHO*0.014), int(ALTO*0.02)))
                            balas_jefe.append(pygame.Rect(cx + int(ANCHO*0.02), by, int(ANCHO*0.014), int(ALTO*0.02)))
                            jefe_actual['cooldown_disparo'] = 0
                    else:
                        if jefe_actual['cooldown_disparo'] >= 28:
                            cx = jefe_actual['rect'].centerx
                            by = jefe_actual['rect'].bottom
                            balas_jefe.append(pygame.Rect(cx - int(ANCHO*0.045), by, int(ANCHO*0.013), int(ALTO*0.02)))
                            balas_jefe.append(pygame.Rect(cx - int(ANCHO*0.008), by, int(ANCHO*0.013), int(ALTO*0.02)))
                            balas_jefe.append(pygame.Rect(cx + int(ANCHO*0.03), by, int(ANCHO*0.013), int(ALTO*0.02)))
                            jefe_actual['cooldown_disparo'] = 0

            for bj in balas_jefe[:]:
                bj.y += int(ALTO * 0.011)
                if bj.y > ALTO:
                    balas_jefe.remove(bj)

            tiempo_nuevo_enemigo += 1
            tam_e = int(ANCHO * 0.09)

            if tiempo_nuevo_enemigo >= 50 and len(enemigos) < max_enemigos_pantalla:
                if jefe_actual is None or jefe_actual['tipo'] != 'JEFE_REAL':
                    ex = random.randint(0, ANCHO - tam_e)
                    if puntos >= 700 and random.random() < 0.20:
                        enemigos.append({
                            'rect': pygame.Rect(ex, -tam_e, tam_e, tam_e),
                            'vida': 3, 'tipo': 'ARTILLERO', 'color': AZUL_ARTILLERO,
                            'vel_x': random.choice([int(ANCHO*0.003), -int(ANCHO*0.003)]),
                            'cooldown': random.randint(30, 90)
                        })
                    elif (jefe_actual and jefe_actual['tipo'] == 'MINI_JEFE') or (puntos >= 400 and random.random() < 0.25):
                        enemigos.append({
                            'rect': pygame.Rect(ex, -tam_e, tam_e, tam_e),
                            'vida': 2, 'tipo': 'KAMIKAZE', 'color': NARANJA_KAMIKAZE
                        })
                    else:
                        enemigos.append({
                            'rect': pygame.Rect(ex, -tam_e, tam_e, tam_e),
                            'vida': 1, 'tipo': 'COMUN', 'color': ROJO_ENEMIGO
                        })
                    tiempo_nuevo_enemigo = 0

            for e in enemigos:
                if e['tipo'] == 'ARTILLERO':
                    if e['rect'].y < int(ALTO * 0.22):
                        e['rect'].y += int(ALTO * 0.003)
                    e['rect'].x += e['vel_x']
                    if e['rect'].left <= 0:
                        e['rect'].left = 0
                        e['vel_x'] *= -1
                    elif e['rect'].right >= ANCHO:
                        e['rect'].right = ANCHO
                        e['vel_x'] *= -1
                    e['cooldown'] -= 1
                    if e['cooldown'] <= 0:
                        bx = e['rect'].centerx - int(ANCHO * 0.007)
                        balas_artillero.append(pygame.Rect(bx, e['rect'].bottom, int(ANCHO*0.014), int(ALTO*0.022)))
                        e['cooldown'] = random.randint(70, 110)
                elif e['tipo'] == 'KAMIKAZE':
                    e['rect'].y += int(velocidad_enemigo * 1.55)
                    centro_jugador = jugador_x + jugador_tam // 2
                    if e['rect'].centerx < centro_jugador - 4:
                        e['rect'].x += int(ANCHO * 0.0055)
                    elif e['rect'].centerx > centro_jugador + 4:
                        e['rect'].x -= int(ANCHO * 0.0055)
                else:
                    e['rect'].y += velocidad_enemigo
                    if e['rect'].y > ALTO:
                        e['rect'].y = -tam_e
                        e['rect'].x = random.randint(0, ANCHO - tam_e)

            for ba in balas_artillero[:]:
                ba.y += int(ALTO * 0.007)
                if ba.y > ALTO:
                    balas_artillero.remove(ba)

            rect_j = pygame.Rect(jugador_x, jugador_y, jugador_tam, jugador_tam)

            for orb in orbes_curacion[:]:
                if rect_j.colliderect(orb['rect']):
                    salud_barras = min(salud_maxima, salud_barras + 1)
                    reproducir_sonido('curacion')
                    orbes_curacion.remove(orb)

            for e in enemigos[:]:
                if rect_j.colliderect(e['rect']):
                    reproducir_sonido('impacto')
                    if e['tipo'] == 'KAMIKAZE':
                        salud_barras -= 4
                        vibrar(0.22)
                    elif e['tipo'] == 'ARTILLERO':
                        salud_barras -= 3
                        vibrar(0.15)
                    else:
                        salud_barras -= 2
                        vibrar(0.1)
                    enemigos.remove(e)

            for bj in balas_jefe[:]:
                if rect_j.colliderect(bj):
                    salud_barras -= 2
                    reproducir_sonido('impacto')
                    vibrar(0.1)
                    balas_jefe.remove(bj)

            for ba in balas_artillero[:]:
                if rect_j.colliderect(ba):
                    salud_barras -= 1
                    reproducir_sonido('impacto')
                    vibrar(0.08)
                    balas_artillero.remove(ba)

            if jefe_actual and rect_j.colliderect(jefe_actual['rect']):
                salud_barras = 0
                vibrar(0.5)

            if salud_barras <= 0:
                salud_barras = 0
                reproducir_sonido('explosion')
                vibrar(0.4)
                game_over = True
                if puntos > high_score:
                    high_score = puntos
                    guardar_high_score(high_score)
                    nuevo_record_alcanzado = True

            for e in enemigos[:]:
                for bala in balas[:]:
                    if bala.colliderect(e['rect']):
                        balas.remove(bala)
                        e['vida'] -= 1
                        if e['vida'] <= 0:
                            reproducir_sonido('impacto')
                            if e['tipo'] == 'ARTILLERO':
                                puntos += 25
                            elif e['tipo'] == 'KAMIKAZE':
                                radio_orb = int(ANCHO * 0.025)
                                orbes_curacion.append({
                                    'rect': pygame.Rect(e['rect'].centerx - radio_orb, e['rect'].centery - radio_orb, radio_orb*2, radio_orb*2)
                                })
                                puntos += 15
                            else:
                                puntos += 10
                            enemigos.remove(e)
                        break

            if jefe_actual:
                for bala in balas[:]:
                    if bala.colliderect(jefe_actual['rect']):
                        balas.remove(bala)
                        jefe_actual['vida'] -= 1
                        if jefe_actual['vida'] <= 0:
                            reproducir_sonido('explosion')
                            if jefe_actual['tipo'] == 'MINI_JEFE':
                                puntos += 180
                                siguiente_umbral_jefe += 700
                                siguiente_tipo_jefe = 'JEFE_REAL'
                            else:
                                puntos += 550
                                siguiente_umbral_jefe += 500
                                siguiente_tipo_jefe = 'MINI_JEFE'
                            jefe_actual = None
                        break

        # ========================================================
        # RENDER
        # ========================================================

        pantalla.fill(NEGRO)

        for est in estrellas:
            pygame.draw.circle(pantalla, BLANCO, (int(est['x']), int(est['y'])), est['radio'])

        if estado_juego == 'MENU':
            txt_titulo_sombra = fuente_titulo.render("ATAQUES ESPACIALES", True, (0, 60, 100))
            txt_titulo = fuente_titulo.render("ATAQUES ESPACIALES", True, AZUL_NAVE)
            pos_t_x = ANCHO // 2 - txt_titulo.get_width() // 2
            pos_t_y = int(ALTO * 0.11)
            pantalla.blit(txt_titulo_sombra, (pos_t_x + 4, pos_t_y + 4))
            pantalla.blit(txt_titulo, (pos_t_x, pos_t_y))

            hs_rect = pygame.Rect(ANCHO//2 - int(ANCHO*0.32), int(ALTO*0.21), int(ANCHO*0.64), int(ALTO*0.07))
            pygame.draw.rect(pantalla, (25, 25, 45), hs_rect, border_radius=12)
            pygame.draw.rect(pantalla, DORADO, hs_rect, width=2, border_radius=12)
            txt_hs_label = fuente_peque.render("MEJOR PUNTUACIÓN", True, (180, 180, 200))
            txt_hs = fuente_grande.render(str(high_score), True, DORADO)
            pantalla.blit(txt_hs_label, (hs_rect.centerx - txt_hs_label.get_width()//2, hs_rect.y + 6))
            pantalla.blit(txt_hs, (hs_rect.centerx - txt_hs.get_width()//2, hs_rect.y + int(ALTO*0.028)))

            dibujar_boton(pantalla, btn_iniciar_rect, "INICIAR JUEGO", VERDE_REANUDAR)
            dibujar_boton(pantalla, btn_tutorial_rect, "CÓMO JUGAR", AZUL_CONFIG)
            dibujar_boton(pantalla, btn_opciones_rect, "OPCIONES", BOTON_COLOR)
            dibujar_boton(pantalla, btn_salir_rect, "SALIR", ROJO_SALIR)

            nave_menu_x = ANCHO // 2 - jugador_tam // 2
            nave_menu_y = int(ALTO * 0.78) + int(menu_nave_offset)
            dibujar_nave_jugador(pantalla, nave_menu_x, nave_menu_y, jugador_tam)

            if mostrar_tutorial:
                sombra = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
                sombra.fill((0, 0, 0, 210))
                pantalla.blit(sombra, (0, 0))
                panel = pygame.Rect(int(ANCHO*0.08), int(ALTO*0.15), int(ANCHO*0.84), int(ALTO*0.60))
                pygame.draw.rect(pantalla, (25, 28, 50), panel, border_radius=16)
                pygame.draw.rect(pantalla, AZUL_NAVE, panel, width=2, border_radius=16)

                titulo_tut = fuente_grande.render("CÓMO JUGAR", True, AZUL_NAVE)
                pantalla.blit(titulo_tut, (panel.centerx - titulo_tut.get_width()//2, panel.y + 16))

                lineas = [
                    "• Muévete en 4 direcciones",
                    "• Usa botones o desliza el dedo",
                    "",
                    "• Naves NARANJAS = Kamikaze",
                    "• ARTILLEROS disparan desde arriba",
                    "",
                    "• Los JEFES tienen varias fases",
                    "• Recoge orbes azules para curarte",
                    "",
                    "• Cambia el layout de botones",
                    "  en Opciones según tu comodidad"
                ]
                y_texto = panel.y + 65
                for linea in lineas:
                    txt = fuente_peque.render(linea, True, BLANCO)
                    pantalla.blit(txt, (panel.x + 25, y_texto))
                    y_texto += int(ALTO * 0.032)

                dibujar_boton(pantalla, btn_cerrar_tutorial, "ENTENDIDO", VERDE_REANUDAR)

        elif estado_juego == 'OPCIONES':
            txt_sub = fuente_grande.render("OPCIONES", True, AZUL_NAVE)
            pantalla.blit(txt_sub, (ANCHO // 2 - txt_sub.get_width() // 2, int(ALTO * 0.18)))

            texto_ctrl = "CONTROL: BOTONES" if tipo_control == 'BOTONES' else "CONTROL: DESLIZAR"
            dibujar_boton(pantalla, btn_modo_control_rect, texto_ctrl, AZUL_CONFIG)

            texto_lay = f"LAYOUT: {tipo_layout}"
            dibujar_boton(pantalla, btn_layout_rect, texto_lay, (70, 50, 140))

            dibujar_boton(pantalla, btn_volver_opciones_rect, "VOLVER AL MENÚ", ROJO_SALIR)

            txt_prev = fuente_peque.render("Vista previa del layout:", True, (160, 160, 180))
            pantalla.blit(txt_prev, (ANCHO//2 - txt_prev.get_width()//2, int(ALTO*0.72)))

        elif estado_juego == 'JUGANDO':

            for bala in balas:
                pygame.draw.rect(pantalla, AMARILLO_BALA, bala)
            for bj in balas_jefe:
                pygame.draw.rect(pantalla, ROJO_BALA_JEFE, bj)
            for ba in balas_artillero:
                pygame.draw.rect(pantalla, AZUL_BALA_ARTILLERO, ba, border_radius=4)

            for orb in orbes_curacion:
                pygame.draw.circle(pantalla, AZUL_CURACION, orb['rect'].center, orb['rect'].width // 2)
                pygame.draw.circle(pantalla, BLANCO, orb['rect'].center, max(2, orb['rect'].width // 4))

            for e in enemigos:
                dibujar_nave_enemiga(pantalla, e['rect'].x, e['rect'].y, e['rect'].width, e['color'], e['tipo'])

            if jefe_actual:
                dibujar_jefe(pantalla, jefe_actual)
                dibujar_barra_vida(pantalla, jefe_actual['rect'], jefe_actual['vida'], jefe_actual['vida_max'])
                txt_j = fuente_jefe.render(f"{jefe_actual['tipo']} - FASE {jefe_actual['fase']}", True, BLANCO)
                pantalla.blit(txt_j, (jefe_actual['rect'].x, jefe_actual['rect'].y - int(ALTO * 0.03)))

            dibujar_nave_jugador(pantalla, jugador_x, jugador_y, jugador_tam)

            if tipo_control == 'BOTONES':
                dibujar_boton_control(pantalla, btn_izq, "←")
                dibujar_boton_control(pantalla, btn_der, "→")
                dibujar_boton_control(pantalla, btn_arr, "↑")
                dibujar_boton_control(pantalla, btn_aba, "↓")

            txt_pts = fuente.render(f"SCORE: {puntos}", True, BLANCO)
            txt_best = fuente.render(f"BEST: {high_score}", True, AMARILLO_BALA)
            pantalla.blit(txt_pts, (int(ANCHO * 0.03), int(ALTO * 0.015)))
            pantalla.blit(txt_best, (int(ANCHO * 0.03), int(ALTO * 0.038)))
            dibujar_salud_jugador(pantalla, salud_barras, salud_maxima)

            pygame.draw.rect(pantalla, BOTON_COLOR, btn_pausa_rect, border_radius=6)
            b_w = max(3, int(btn_p_ancho * 0.15))
            b_h = int(btn_p_alto * 0.5)
            offset_x = int(btn_p_ancho * 0.28)
            offset_y = int(btn_p_alto * 0.25)
            pygame.draw.rect(pantalla, BLANCO, (btn_pausa_rect.x + offset_x, btn_pausa_rect.y + offset_y, b_w, b_h))
            pygame.draw.rect(pantalla, BLANCO, (btn_pausa_rect.x + btn_p_ancho - offset_x - b_w, btn_pausa_rect.y + offset_y, b_w, b_h))

            if en_pausa:
                sombra = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
                sombra.fill(OVERLAY_SOMBRA)
                pantalla.blit(sombra, (0, 0))
                txt_p = fuente_grande.render("PAUSA", True, BLANCO)
                pantalla.blit(txt_p, (ANCHO//2 - txt_p.get_width()//2, ALTO//2 - int(ALTO*0.15)))
                dibujar_boton(pantalla, btn_reanudar_rect, "REANUDAR", VERDE_REANUDAR)
                dibujar_boton(pantalla, btn_menu_pausa_rect, "MENÚ PRINCIPAL", ROJO_SALIR)

            if game_over:
                sombra = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
                sombra.fill(OVERLAY_SOMBRA)
                pantalla.blit(sombra, (0, 0))
                txt_go = fuente_grande.render("GAME OVER", True, ROJO_ENEMIGO)
                pantalla.blit(txt_go, (ANCHO//2 - txt_go.get_width()//2, ALTO//2 - int(ALTO*0.16)))
                if nuevo_record_alcanzado:
                    txt_rec = fuente.render("¡NUEVO RÉCORD!", True, AMARILLO_BALA)
                    pantalla.blit(txt_rec, (ANCHO//2 - txt_rec.get_width()//2, ALTO//2 - int(ALTO*0.09)))
                txt_score_fin = fuente.render(f"PUNTAJE FINAL: {puntos}", True, BLANCO)
                pantalla.blit(txt_score_fin, (ANCHO//2 - txt_score_fin.get_width()//2, ALTO//2 - int(ALTO*0.05)))
                dibujar_boton(pantalla, btn_reintentar_rect, "REINTENTAR", VERDE_REINTENTAR)
                dibujar_boton(pantalla, btn_menu_go_rect, "MENÚ PRINCIPAL", ROJO_SALIR)

        pygame.display.flip()
        await asyncio.sleep(0)  # Obligatorio para Pygbag / navegador

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    asyncio.run(main())
