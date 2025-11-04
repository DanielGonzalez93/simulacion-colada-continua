"""
================================================================================
SCRIPT AUTOMATIZADO FREECAD
SISTEMA DE CALENTAMIENTO POR INDUCCIÓN DE PALANQUILLAS
================================================================================

INSTRUCCIONES DE USO:
1. Abrir FreeCAD
2. Ir a: Macro → Macros... (Alt+F6)
3. Click en "Create"
4. Nombre: "Sistema_Induccion_Palanquillas"
5. Copiar y pegar este código completo
6. Click en "Execute"
7. Esperar a que termine (puede tomar 1-2 minutos)
8. Archivo → Exportar → Seleccionar STEP

BASADO EN: https://preview--induction-billet-blueprint.lovable.app/

================================================================================
"""

import FreeCAD as App
import Part
import Draft
import math
import os
import glob
import shutil
import subprocess

# Permitir especificar ffmpeg explícitamente vía variable de entorno
# y forzar ruta local conocida como fallback
FFMPEG_EXE = os.environ.get('FFMPEG_EXE', r"C:\\Users\\Usuario\\Documents\\Personal\\Palanquillas\\ffmpeg\\bin\\ffmpeg.exe")
if not os.path.isfile(FFMPEG_EXE):
    which = shutil.which('ffmpeg')
    if which:
        FFMPEG_EXE = which

# ============================================================================
# PARÁMETROS DEL SISTEMA (Modificables)
# ============================================================================

# ESCALA GENERAL PARA VERLO MÁS GRANDE EN PANTALLA
SCALE = 3.0  # 1.0 = real; >1 más grande

# MODO DE PROCESO: 'casting_vertical' o 'induction_horizontal'
PROCESS_MODE = 'casting_vertical'

# Palanquilla (se aplicará SCALE)
BILLET_SECTION = 130 * SCALE       # mm (sección cuadrada)
BILLET_LENGTH = 12000 * SCALE      # mm (longitud)
# Parámetros de Colada Continua Vertical
STRAND_SECTION = 150 * SCALE        # mm
STRAND_LENGTH = 12000 * SCALE       # mm (largo modelado del hilo)
MOLD_SIZE = STRAND_SECTION + 60 * SCALE
MOLD_HEIGHT = 800 * SCALE
TUNDISH_W = 1000 * SCALE
TUNDISH_D = 600 * SCALE
TUNDISH_H = 400 * SCALE
SPRAY_ZONE_COUNT = 6
SPRAY_SPACING = 1000 * SCALE
ROLLER_PAIR_COUNT = 16

# Bobinas de Inducción (aplicar SCALE)
COIL_INNER_DIAMETER = 300 * SCALE  # mm (clearance para palanquilla)
COIL_OUTER_DIAMETER = 420 * SCALE  # mm (más robusta)
COIL_HEIGHT = 280 * SCALE          # mm (más alta)
COIL_COUNT = 8                     # Número de bobinas
COIL_SPACING = 1500 * SCALE        # mm (separación entre bobinas)
CONDUCTOR_DIAMETER = 18 * SCALE    # mm (tubo de cobre)

# Rodillos
ROLLER_DIAMETER = 240 * SCALE
ROLLER_WIDTH = 520 * SCALE
ROLLER_COUNT = 18
ROLLER_SPACING = 800 * SCALE

# Estructura
FRAME_HEIGHT = 2000 * SCALE
COLUMN_DIAMETER = 160 * SCALE

# Colores (RGB 0-1)
COLOR_STEEL = (0.6, 0.6, 0.6)
COLOR_COPPER = (0.72, 0.45, 0.20)
COLOR_HOT_STEEL = (1.0, 0.3, 0.0)

# Flags para evitar "puntos/solidos" accesorios
CREATE_SENSORS = False
CREATE_PIPES = False

# Parámetros de animación (unificado)
FRAMES = 240
FPS = 24
TEMP_MIN = 20
TEMP_MAX = 1200
IMG_W, IMG_H = 1920, 1080
MARGIN_X = 2000 * SCALE
# Directorio base: carpeta donde está este script
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except Exception:
    BASE_DIR = os.getcwd()
OUTPUT_DIR = os.path.join(BASE_DIR, "_render_animacion")


# ============================================================================
# FUNCIONES DE CREACIÓN
# ============================================================================

def create_document():
    """Crear nuevo documento FreeCAD"""
    doc = App.newDocument("Sistema_Induccion_Palanquillas")
    print("✓ Documento creado: Sistema_Induccion_Palanquillas")
    return doc


def create_billet(doc):
    """Crear palanquilla de acero 130x130x12000mm ORIENTADA EN X (horizontal)"""
    print("⏳ Creando palanquilla...")
    
    # Crear prisma con longitud sobre X (X=longitud, Y=sección, Z=sección)
    square = Part.makeBox(BILLET_LENGTH, BILLET_SECTION, BILLET_SECTION)
    
    # Centrar respecto al origen (que el centro de la sección quede en 0,0)
    offset_x = -BILLET_LENGTH / 2
    offset_y = -BILLET_SECTION / 2
    offset_z = -BILLET_SECTION / 2
    square.translate(App.Vector(offset_x, offset_y, offset_z))
    
    # Crear objeto en documento
    billet = doc.addObject("Part::Feature", "Palanquilla_130x130x12000")
    billet.Shape = square
    billet.ViewObject.ShapeColor = COLOR_STEEL
    
    print(f"✓ Palanquilla creada: {BILLET_SECTION}×{BILLET_SECTION}×{BILLET_LENGTH}mm")
    return billet


# ===============================
# Colada Continua Vertical - Geometría
# ===============================

def create_strand_vertical(doc):
    """Crear hilo de colada (palanquilla en colada continua) orientado en Z (vertical)."""
    print("⏳ Creando hilo de colada vertical...")
    strand = Part.makeBox(STRAND_SECTION, STRAND_SECTION, STRAND_LENGTH)
    # centrar X,Y y colocar la parte superior por encima del molde (z inicial positiva)
    strand.translate(App.Vector(-STRAND_SECTION/2, -STRAND_SECTION/2, 800 * SCALE))
    strand_obj = doc.addObject("Part::Feature", "Hilo_Colada_Vertical")
    strand_obj.Shape = strand
    strand_obj.ViewObject.ShapeColor = COLOR_STEEL
    return strand_obj


def create_tundish(doc):
    body = Part.makeBox(TUNDISH_W, TUNDISH_D, TUNDISH_H)
    body.translate(App.Vector(-TUNDISH_W/2, -TUNDISH_D/2, MOLD_HEIGHT + 600 * SCALE))
    o = doc.addObject("Part::Feature", "Tundish")
    o.Shape = body
    o.ViewObject.ShapeColor = (0.8, 0.7, 0.5)
    return o


def create_mold(doc):
    mold = Part.makeBox(MOLD_SIZE, MOLD_SIZE, MOLD_HEIGHT)
    mold.translate(App.Vector(-MOLD_SIZE/2, -MOLD_SIZE/2, 0))
    o = doc.addObject("Part::Feature", "Molde_Cobre")
    o.Shape = mold
    o.ViewObject.ShapeColor = (0.9, 0.6, 0.2)  # cobre
    return o


def create_spray_zones(doc):
    """Crear boquillas alrededor del hilo en varias alturas."""
    sprays = []
    radius = (MOLD_SIZE/2) + 120 * SCALE
    for i in range(SPRAY_ZONE_COUNT):
        z = - (i+1) * SPRAY_SPACING
        for a in [0, 90, 180, 270]:
            cyl = Part.makeCylinder(40 * SCALE, 200 * SCALE)
            # orientar el cilindro mirando hacia el centro
            cyl.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
            x = radius * math.cos(math.radians(a))
            y = radius * math.sin(math.radians(a))
            cyl.translate(App.Vector(x - 100* SCALE, y, z))
            o = doc.addObject("Part::Feature", f"Spray_{i+1}_{a}")
            o.Shape = cyl
            o.ViewObject.ShapeColor = (0.2, 0.6, 0.9)
            sprays.append(o)
    print(f"✓ Zonas de spray: {SPRAY_ZONE_COUNT}")
    return sprays


def create_vertical_rollers(doc):
    """Crear pares de rodillos guía a lo largo del descenso."""
    rollers = []
    for i in range(ROLLER_PAIR_COUNT):
        z = - i * (SPRAY_SPACING * 0.6)
        # rodillo X
        r1 = Part.makeCylinder(120 * SCALE, 400 * SCALE)
        r1.rotate(App.Vector(0,0,0), App.Vector(1,0,0), 90)  # eje Y
        r1.translate(App.Vector(-200 * SCALE, 0, z))
        o1 = doc.addObject("Part::Feature", f"RollerX_{i:02d}")
        o1.Shape = r1
        o1.ViewObject.ShapeColor = (0.3,0.3,0.35)
        # rodillo Y
        r2 = Part.makeCylinder(120 * SCALE, 400 * SCALE)
        r2.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)  # eje X
        r2.translate(App.Vector(0, -200 * SCALE, z))
        o2 = doc.addObject("Part::Feature", f"RollerY_{i:02d}")
        o2.Shape = r2
        o2.ViewObject.ShapeColor = (0.3,0.3,0.35)
        rollers += [o1, o2]
    print(f"✓ Rodillos verticales: {ROLLER_PAIR_COUNT*2}")
    return rollers


# ===============================
# Equipos periféricos (vista general)
# ===============================

def add_label(doc, text, x, y, z):
    try:
        t = Draft.makeText([text], point=App.Vector(x, y, z))
        t.ViewObject.TextSize = 40 * SCALE
        t.ViewObject.TextColor = (1.0, 1.0, 0.4)
        return t
    except Exception:
        return None


def create_induction_furnace(doc):
    x = -2500 * SCALE; y = 0; z = MOLD_HEIGHT + 600 * SCALE
    # crisol
    crucible_outer = Part.makeCylinder(500 * SCALE, 700 * SCALE)
    crucible_inner = Part.makeCylinder(420 * SCALE, 700 * SCALE)
    crucible = crucible_outer.cut(crucible_inner)
    crucible.translate(App.Vector(x, y, z))
    c_obj = doc.addObject("Part::Feature", "Horno_Induccion_Crisol")
    c_obj.Shape = crucible
    c_obj.ViewObject.ShapeColor = (0.5, 0.5, 0.55)
    # bobina
    torus = Part.makeTorus(520 * SCALE, 80 * SCALE)
    torus.translate(App.Vector(x, y, z + 350 * SCALE))
    coil = doc.addObject("Part::Feature", "Horno_Bobina")
    coil.Shape = torus
    coil.ViewObject.ShapeColor = (0.95, 0.6, 0.2)
    add_label(doc, "Horno de Induccion\n5 t/h | 3500 kW", x - 400 * SCALE, y + 700 * SCALE, z + 800 * SCALE)
    return [c_obj, coil]


def create_transformer(doc):
    x = -3600 * SCALE; y = -600 * SCALE; z = MOLD_HEIGHT + 200 * SCALE
    body = Part.makeBox(900 * SCALE, 600 * SCALE, 800 * SCALE)
    body.translate(App.Vector(x, y, z))
    o = doc.addObject("Part::Feature", "Transformador_4000kVA")
    o.Shape = body
    o.ViewObject.ShapeColor = (0.3, 0.35, 0.45)
    add_label(doc, "Transformador 4000 kVA", x - 200 * SCALE, y, z + 900 * SCALE)
    return [o]


def create_cooling_tower(doc):
    x = 2800 * SCALE; y = -1500 * SCALE; z = -400 * SCALE
    tank = Part.makeCylinder(700 * SCALE, 1200 * SCALE)
    tank.translate(App.Vector(x, y, z))
    o = doc.addObject("Part::Feature", "Torre_Enfriamiento_500m3h")
    o.Shape = tank
    o.ViewObject.ShapeColor = (0.6, 0.8, 0.9)
    add_label(doc, "Torre 500 m3/h", x - 300 * SCALE, y, z + 1300 * SCALE)
    return [o]


def create_bridge_crane(doc):
    x1 = -3200 * SCALE; x2 = 3200 * SCALE; z = MOLD_HEIGHT + 2600 * SCALE
    beam = Part.makeBox((x2 - x1), 200 * SCALE, 200 * SCALE)
    beam.translate(App.Vector(x1, 1200 * SCALE, z))
    b = doc.addObject("Part::Feature", "Grua_Puente_Beam")
    b.Shape = beam
    b.ViewObject.ShapeColor = (0.95, 0.85, 0.2)
    # gancho
    hook = Part.makeCylinder(60 * SCALE, 800 * SCALE)
    hook.translate(App.Vector(0, 1200 * SCALE, z - 800 * SCALE))
    h = doc.addObject("Part::Feature", "Grua_Hook")
    h.Shape = hook
    h.ViewObject.ShapeColor = (0.9, 0.6, 0.1)
    add_label(doc, "Grua 15 t", -200 * SCALE, 1300 * SCALE, z + 200 * SCALE)
    return [b, h]


def create_fume_filter(doc):
    x = 2600 * SCALE; y = 800 * SCALE; z = 200 * SCALE
    box = Part.makeBox(1000 * SCALE, 700 * SCALE, 1000 * SCALE)
    box.translate(App.Vector(x, y, z))
    o = doc.addObject("Part::Feature", "Filtro_Humos")
    o.Shape = box
    o.ViewObject.ShapeColor = (0.5, 0.6, 0.65)
    add_label(doc, "Filtracion de humos\nCaptacion y filtrado", x - 400 * SCALE, y, z + 1100 * SCALE)
    return [o]


def create_scrap_loader(doc):
    x = -3000 * SCALE; y = -1200 * SCALE; z = MOLD_HEIGHT + 200 * SCALE
    bucket = Part.makeBox(800 * SCALE, 600 * SCALE, 600 * SCALE)
    bucket.translate(App.Vector(x, y, z))
    o = doc.addObject("Part::Feature", "Cargador_Chatarra")
    o.Shape = bucket
    o.ViewObject.ShapeColor = (0.6, 0.45, 0.3)
    add_label(doc, "Cargador de Chatarra\nSistema automatizado", x - 400 * SCALE, y, z + 700 * SCALE)
    return [o]


def create_plc_scada(doc):
    x = 2000 * SCALE; y = 1600 * SCALE; z = 0
    cab = Part.makeBox(600 * SCALE, 300 * SCALE, 1200 * SCALE)
    cab.translate(App.Vector(x, y, z))
    o = doc.addObject("Part::Feature", "PLC_SCADA")
    o.Shape = cab
    o.ViewObject.ShapeColor = (0.8, 0.8, 0.85)
    add_label(doc, "PLC + SCADA\nControl automatizado", x - 250 * SCALE, y, z + 1250 * SCALE)
    return [o]


def create_ball_molder(doc):
    x = 1800 * SCALE; y = -2200 * SCALE; z = -600 * SCALE
    body = Part.makeBox(1200 * SCALE, 800 * SCALE, 900 * SCALE)
    body.translate(App.Vector(x, y, z))
    o = doc.addObject("Part::Feature", "Moldeadora_Bolas")
    o.Shape = body
    o.ViewObject.ShapeColor = (0.7, 0.5, 0.4)
    add_label(doc, "Moldeadora de Bolas\nSistema de moldeado", x - 450 * SCALE, y, z + 1000 * SCALE)
    return [o]


def create_sensors_and_safety(doc):
    objs = []
    # Sensores (pirómetros) en varias alturas
    for i in range(4):
        z = - (i+1) * (SPRAY_SPACING * 0.8)
        s = Part.makeCylinder(40 * SCALE, 160 * SCALE)
        s.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
        s.translate(App.Vector(500 * SCALE, 0, z))
        o = doc.addObject("Part::Feature", f"Sensor_{i+1}")
        o.Shape = s
        o.ViewObject.ShapeColor = (0.95, 0.9, 0.2)
        objs.append(o)
    add_label(doc, "Sensores y Medicion\nTemperatura | nivel | flujo", 700 * SCALE, 0, 200 * SCALE)
    # Postes de seguridad
    for x in [-900 * SCALE, 900 * SCALE]:
        p = Part.makeCylinder(40 * SCALE, 1200 * SCALE)
        p.translate(App.Vector(x, -900 * SCALE, 0))
        po = doc.addObject("Part::Feature", f"Poste_{int(x)}")
        po.Shape = p
        po.ViewObject.ShapeColor = (0.9, 0.2, 0.2)
        objs.append(po)
    add_label(doc, "Sistema de Seguridad\nAlarmas y paradas", -1000 * SCALE, -900 * SCALE, 1300 * SCALE)
    return objs


def create_coil(doc, position, index):
    """Crear bobina de inducción individual"""
    
    # Radio medio para el conductor
    r_inner = COIL_INNER_DIAMETER / 2
    r_outer = COIL_OUTER_DIAMETER / 2
    r_mid = (r_inner + r_outer) / 2
    
    # Crear anillo (torus simplificado)
    conductor_radius = (r_outer - r_inner) / 2
    
    # Crear torus
    torus = Part.makeTorus(r_mid, conductor_radius)
    
    # Extender verticalmente para simular espiras apiladas
    extrusion_vector = App.Vector(0, 0, COIL_HEIGHT - conductor_radius * 2)
    cylinder = Part.makeCylinder(conductor_radius, COIL_HEIGHT - conductor_radius * 2)
    
    # Crear múltiples anillos para simular espiras
    coil_shape = torus
    
    # Agregar grosor vertical
    ring_outer = Part.makeCylinder(r_outer, COIL_HEIGHT)
    ring_inner = Part.makeCylinder(r_inner, COIL_HEIGHT)
    coil_shape = ring_outer.cut(ring_inner)
    
    # Rotar 90° alrededor de Y para que el eje de la bobina sea X (horizontal)
    coil_shape.rotate(App.Vector(0, 0, 0), App.Vector(0, 1, 0), 90)
    
    # Posicionar bobina a lo largo de X
    coil_shape.translate(App.Vector(position, 0, 0))
    
    # Crear objeto
    coil = doc.addObject("Part::Feature", f"Bobina_Induccion_{index:02d}")
    coil.Shape = coil_shape
    coil.ViewObject.ShapeColor = COLOR_COPPER
    
    return coil


def create_all_coils(doc):
    """Crear todas las bobinas en serie"""
    print(f"⏳ Creando {COIL_COUNT} bobinas de inducción...")
    
    coils = []
    for i in range(COIL_COUNT):
        # Calcular posición X de cada bobina
        x_position = i * COIL_SPACING + 500  # Empezar a 500mm
        coil = create_coil(doc, x_position, i + 1)
        coils.append(coil)
    
    print(f"✓ {COIL_COUNT} bobinas creadas")
    return coils


def create_roller(doc, x_position, index):
    """Crear rodillo de transporte (eje Y) bajo la palanquilla horizontal"""
    
    # Cilindro con eje Y (por defecto eje Z, lo giramos 90° sobre X)
    roller = Part.makeCylinder(ROLLER_DIAMETER / 2, ROLLER_WIDTH)
    roller.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), 90)
    
    # Posicionar: bajo la palanquilla, centrado en Z=0
    y_position = -(BILLET_SECTION / 2 + ROLLER_DIAMETER / 2 + 50)
    z_position = 0
    roller.translate(App.Vector(x_position - ROLLER_WIDTH / 2, y_position, z_position))
    
    # Crear objeto
    roller_obj = doc.addObject("Part::Feature", f"Rodillo_{index:02d}")
    roller_obj.Shape = roller
    roller_obj.ViewObject.ShapeColor = (0.3, 0.3, 0.3)
    
    return roller_obj


def create_all_rollers(doc):
    """Crear todos los rodillos"""
    print(f"⏳ Creando {ROLLER_COUNT} rodillos de transporte...")
    
    rollers = []
    for i in range(ROLLER_COUNT):
        x_position = i * ROLLER_SPACING
        roller = create_roller(doc, x_position, i + 1)
        rollers.append(roller)
    
    print(f"✓ {ROLLER_COUNT} rodillos creados")
    return rollers


def create_support_column(doc, x, y, index):
    """Crear columna de soporte"""
    
    column = Part.makeCylinder(COLUMN_DIAMETER / 2, FRAME_HEIGHT)
    column.translate(App.Vector(x, y, 0))
    
    col_obj = doc.addObject("Part::Feature", f"Columna_{index}")
    col_obj.Shape = column
    col_obj.ViewObject.ShapeColor = (0.4, 0.4, 0.5)
    
    return col_obj


def create_frame(doc):
    """Crear estructura de soporte (4 columnas)"""
    print("⏳ Creando estructura de soporte...")
    
    # Posiciones de las 4 columnas
    offset_x = 400
    offset_y = 300
    
    positions = [
        (offset_x, offset_y, 1),
        (-offset_x, offset_y, 2),
        (offset_x, -offset_y, 3),
        (-offset_x, -offset_y, 4)
    ]
    
    columns = []
    for x, y, idx in positions:
        col = create_support_column(doc, x, y, idx)
        columns.append(col)
    
    print("✓ Estructura creada (4 columnas)")
    return columns


def create_temperature_sensors(doc):
    """Crear sensores de temperatura (pirómetros)"""
    print("⏳ Creando sensores de temperatura...")
    
    sensors = []
    for i in range(COIL_COUNT):
        # Posición: al lado de cada bobina
        z_pos = i * COIL_SPACING + 500 + COIL_HEIGHT / 2
        x_pos = 300  # Lateral
        y_pos = 0
        
        # Cilindro pequeño para representar sensor
        sensor = Part.makeCylinder(25, 150)
        sensor.rotate(App.Vector(x_pos, y_pos, z_pos), App.Vector(0, 1, 0), 90)
        sensor.translate(App.Vector(x_pos, y_pos, z_pos))
        
        sensor_obj = doc.addObject("Part::Feature", f"Sensor_Temp_{i+1:02d}")
        sensor_obj.Shape = sensor
        sensor_obj.ViewObject.ShapeColor = (0.9, 0.9, 0.1)  # Amarillo
        sensors.append(sensor_obj)
    
    print(f"✓ {COIL_COUNT} sensores creados")
    return sensors


def add_cooling_pipes(doc):
    """Crear sistema de tuberías de refrigeración"""
    print("⏳ Creando tuberías de refrigeración...")
    
    pipes = []
    pipe_diameter = 20
    
    for i in range(COIL_COUNT):
        # Dos tuberías por bobina (entrada y salida)
        z_pos = i * COIL_SPACING + 500
        
        # Tubería de entrada
        pipe_in = Part.makeCylinder(pipe_diameter / 2, 500)
        pipe_in.rotate(App.Vector(0, 0, 0), App.Vector(0, 1, 0), 90)
        pipe_in.translate(App.Vector(-250, COIL_OUTER_DIAMETER / 2 + 50, z_pos + 50))
        
        pipe_in_obj = doc.addObject("Part::Feature", f"Tuberia_Entrada_{i+1:02d}")
        pipe_in_obj.Shape = pipe_in
        pipe_in_obj.ViewObject.ShapeColor = (0.2, 0.5, 0.8)  # Azul agua
        pipes.append(pipe_in_obj)
        
        # Tubería de salida
        pipe_out = Part.makeCylinder(pipe_diameter / 2, 500)
        pipe_out.rotate(App.Vector(0, 0, 0), App.Vector(0, 1, 0), 90)
        pipe_out.translate(App.Vector(-250, COIL_OUTER_DIAMETER / 2 + 50, z_pos + 150))
        
        pipe_out_obj = doc.addObject("Part::Feature", f"Tuberia_Salida_{i+1:02d}")
        pipe_out_obj.Shape = pipe_out
        pipe_out_obj.ViewObject.ShapeColor = (0.8, 0.2, 0.2)  # Rojo agua caliente
        pipes.append(pipe_out_obj)
    
    print(f"✓ {len(pipes)} tuberías creadas")
    return pipes


def create_control_panel(doc):
    """Crear gabinete de control eléctrico"""
    print("⏳ Creando panel de control...")
    
    # Caja rectangular
    panel = Part.makeBox(800, 300, 600)
    panel.translate(App.Vector(-900, -150, 0))
    
    panel_obj = doc.addObject("Part::Feature", "Panel_Control")
    panel_obj.Shape = panel
    panel_obj.ViewObject.ShapeColor = (0.9, 0.6, 0.1)  # Naranja
    
    print("✓ Panel de control creado")
    return panel_obj


def add_system_info(doc):
    """Agregar información del sistema como propiedades"""
    print("⏳ Agregando propiedades del sistema...")
    
    # Calcular peso estimado
    steel_density = 7850  # kg/m³
    billet_volume = (BILLET_SECTION / 1000) ** 2 * (BILLET_LENGTH / 1000)  # m³
    billet_weight = billet_volume * steel_density
    
    total_weight = billet_weight + (COIL_COUNT * 45) + (ROLLER_COUNT * 25) + 850
    
    # Agregar como comentarios al documento
    doc.Comment = f"""SISTEMA DE CALENTAMIENTO POR INDUCCIÓN
    
Palanquilla: {BILLET_SECTION}×{BILLET_SECTION}×{BILLET_LENGTH}mm
Peso palanquilla: {billet_weight:.0f} kg

Bobinas: {COIL_COUNT} unidades
Potencia total: {COIL_COUNT * 150} kW
Diámetro bobinas: {COIL_INNER_DIAMETER}-{COIL_OUTER_DIAMETER}mm

Rodillos: {ROLLER_COUNT} unidades
Longitud sistema: {BILLET_LENGTH}mm

Peso total estimado: {total_weight:.0f} kg

Temperatura objetivo: 1200°C
Tiempo de proceso: 6-10 minutos

Basado en: https://preview--induction-billet-blueprint.lovable.app/
"""
    
    print("✓ Propiedades agregadas")


def organize_in_groups(doc, billet, coils, rollers, columns, sensors, pipes, panel):
    """Organizar componentes en grupos"""
    print("⏳ Organizando en grupos...")
    
    # Crear grupos
    group_heating = doc.addObject("App::DocumentObjectGroup", "01_Sistema_Calentamiento")
    group_transport = doc.addObject("App::DocumentObjectGroup", "02_Sistema_Transporte")
    group_structure = doc.addObject("App::DocumentObjectGroup", "03_Estructura")
    group_cooling = doc.addObject("App::DocumentObjectGroup", "04_Refrigeracion")
    group_control = doc.addObject("App::DocumentObjectGroup", "05_Control")
    
    # Agregar objetos a grupos
    group_heating.addObject(billet)
    for coil in coils:
        group_heating.addObject(coil)
    
    for roller in rollers:
        group_transport.addObject(roller)
    
    for col in columns:
        group_structure.addObject(col)
    
    for sensor in sensors:
        group_control.addObject(sensor)
    
    for pipe in pipes:
        group_cooling.addObject(pipe)
    
    group_control.addObject(panel)
    
    print("✓ Componentes organizados en 5 grupos")


def set_view(doc):
    """Configurar vista isométrica"""
    print("⏳ Configurando vista...")
    
    try:
        import FreeCADGui as Gui
        Gui.activeDocument().activeView().viewIsometric()
        Gui.SendMsgToActiveView("ViewFit")
        print("✓ Vista configurada")
    except:
        print("⚠ No se pudo configurar la vista (modo sin GUI)")


def export_instructions():
    """Mostrar instrucciones de exportación"""
    instructions = """
================================================================================
✓ SISTEMA CREADO EXITOSAMENTE
================================================================================

COMPONENTES CREADOS:
• 1 Palanquilla 130×130×12000mm
• 8 Bobinas de inducción
• 20 Rodillos de transporte
• 4 Columnas de soporte
• 8 Sensores de temperatura
• 16 Tuberías de refrigeración
• 1 Panel de control

PRÓXIMOS PASOS:

1. REVISAR EL MODELO:
   - Rotar vista con botón central del mouse
   - Zoom con scroll
   - Ver árbol de objetos en panel izquierdo

2. EXPORTAR A STEP:
   File → Export...
   - Tipo: STEP with colors (*.step *.stp)
   - Nombre: Sistema_Induccion_Palanquillas_Completo.stp
   - ☑ Export Legacy
   - ☑ Export colors

3. IMPORTAR EN INVENTOR:
   - Abrir Autodesk Inventor
   - File → Open → Seleccionar archivo .stp
   - Opciones:
     ☑ Import as: Multiple solid bodies
     ☑ Stitch surfaces: Yes

4. MODIFICAR PARÁMETROS:
   - Editar valores al inicio de este script
   - Volver a ejecutar el macro

================================================================================
Basado en: https://preview--induction-billet-blueprint.lovable.app/
================================================================================
"""
    print(instructions)
    return instructions


# ============================================================================
# ANIMACIÓN UNIFICADA (horizontal en eje X)
# ============================================================================

def ensure_output_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)


def temp_to_color(temp):
    t = max(0.0, min(1.0, (temp - TEMP_MIN) / float(TEMP_MAX - TEMP_MIN)))
    # gris → rojo → naranja → amarillo → casi blanco (más brillante)
    if t < 0.25:
        k = t / 0.25
        r = 0.55 + 0.35 * k
        g = 0.55 * (1 - k)
        b = 0.55 * (1 - k)
    elif t < 0.6:
        k = (t - 0.25) / 0.35
        r = 0.90 + 0.05 * k
        g = 0.10 * (1 - k)
        b = 0.03 * (1 - k)
    elif t < 0.9:
        k = (t - 0.6) / 0.3
        r = 0.95
        g = 0.15 + 0.70 * k
        b = 0.03
    else:
        # tramo final muy caliente: amarillo → casi blanco
        k = min(1.0, (t - 0.9) / 0.1)
        r = 0.98
        g = 0.85 + 0.14 * k
        b = 0.10 + 0.85 * k * 0.3  # un leve blanqueo
    return (r, g, b)


def compute_coil_centers():
    centers = []
    start_x = 500 * SCALE
    for i in range(COIL_COUNT):
        centers.append(start_x + i * COIL_SPACING + COIL_HEIGHT / 2.0)
    return centers


def coil_activation_intensity(center_x, billet_front_x, billet_back_x):
    if billet_back_x > center_x:
        dist = 0.0
    elif billet_front_x < center_x:
        dist = center_x - billet_front_x
    else:
        dist = 0.0
    return max(0.0, 1.0 - dist / (800.0 * SCALE))


def animate_and_export(doc, billet):
    import FreeCADGui as Gui
    ensure_output_dir()
    view = Gui.activeDocument().activeView()
    view.viewAxonometric()
    Gui.SendMsgToActiveView("ViewFit")

    centers = compute_coil_centers()
    billet_len = BILLET_LENGTH
    start_x = centers[0] - MARGIN_X - billet_len
    end_x = centers[-1] + MARGIN_X

    for f in range(FRAMES):
        t = f / float(max(1, FRAMES - 1))
        xpos = start_x + (end_x - start_x) * t

        pl = billet.Placement
        pl.Base.x = xpos
        billet.Placement = pl

        base_temp = TEMP_MIN + (TEMP_MAX - TEMP_MIN) * t
        boost = 0.0
        billet_front = xpos + billet_len
        billet_back = xpos
        flash_factor = 0.0
        for c in centers:
            inten = coil_activation_intensity(c, billet_front, billet_back)
            boost += 220.0 * inten
            # pico de calentamiento en el instante de entrada a la bobina (Gauss estrecho)
            dx = (c - billet_front) / (120.0 * SCALE)
            flash = math.exp(-dx * dx)
            if flash > flash_factor:
                flash_factor = flash
        temp = min(TEMP_MAX, base_temp + boost + flash_factor * 200.0)
        billet.ViewObject.ShapeColor = temp_to_color(temp)

        if f < 3:
            Gui.SendMsgToActiveView("ViewFit")
        doc.recompute()

        img_path = os.path.join(OUTPUT_DIR, f"frame_{f:04d}.png")
        view.saveImage(img_path, IMG_W, IMG_H, 'Current')
        print(f"Frame {f+1}/{FRAMES}: x={xpos:.1f} temp={temp:.1f}°C → {img_path}")

    print(f"Usando ffmpeg: {FFMPEG_EXE}")
    # MP4 con ffmpeg (ejecución robusta)
    try:
        mp4_path = os.path.join(OUTPUT_DIR, "animacion_induccion.mp4")
        cmd = [FFMPEG_EXE, "-y", "-framerate", str(FPS), "-i", "frame_%04d.png", "-pix_fmt", "yuv420p", mp4_path]
        result = subprocess.run(cmd, cwd=OUTPUT_DIR, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Video generado: {mp4_path}")
        else:
            print("⚠ ffmpeg fallo al crear MP4:")
            print(result.stderr[:4000])
    except Exception as e:
        print(f"⚠ Error creando MP4: {e}")

    # GIF con paleta para buena calidad (si hay ffmpeg)
    try:
        palette_path = os.path.join(OUTPUT_DIR, "palette.png")
        gif_path = os.path.join(OUTPUT_DIR, "animacion_induccion.gif")
        cmd_palette = [FFMPEG_EXE, "-y", "-i", "frame_%04d.png", "-vf", f"fps={FPS},scale={IMG_W}:{IMG_H}:flags=lanczos,palettegen", palette_path]
        cmd_gif = [FFMPEG_EXE, "-y", "-framerate", str(FPS), "-i", "frame_%04d.png", "-i", palette_path, "-lavfi", f"fps={FPS},scale={IMG_W}:{IMG_H}:flags=lanczos,paletteuse=dither=sierra2_4a", gif_path]
        r1 = subprocess.run(cmd_palette, cwd=OUTPUT_DIR, capture_output=True, text=True)
        r2 = subprocess.run(cmd_gif, cwd=OUTPUT_DIR, capture_output=True, text=True) if r1.returncode == 0 else None
        if r1.returncode == 0 and r2 and r2.returncode == 0:
            print(f"✓ GIF generado: {gif_path}")
        else:
            print("⚠ ffmpeg fallo al crear GIF:")
            if r1.returncode != 0:
                print(r1.stderr[:4000])
            elif r2:
                print(r2.stderr[:4000])
    except Exception as e:
        print(f"⚠ Error creando GIF: {e}")

    # Fallback puro Python: imageio (si está disponible en el Python de FreeCAD)
    try:
        gif_path = os.path.join(OUTPUT_DIR, "animacion_induccion.gif")
        if not os.path.exists(gif_path):
            import imageio.v2 as imageio
            frame_paths = sorted(glob.glob(os.path.join(OUTPUT_DIR, "frame_*.png")))
            if frame_paths:
                images = [imageio.imread(p) for p in frame_paths]
                imageio.mimsave(gif_path, images, fps=FPS, loop=0)
                print(f"✓ GIF generado con imageio: {gif_path}")
            else:
                print("⚠ No se encontraron frames PNG para crear el GIF.")
    except Exception as e:
        print(f"⚠ Fallback imageio no disponible: {e}")


# ===============================
# Animación de Colada Continua Vertical
# ===============================

def compute_spray_centers_z():
    return [ - (i+1) * SPRAY_SPACING for i in range(SPRAY_ZONE_COUNT) ]


def animate_casting_vertical(doc, strand):
    import FreeCADGui as Gui
    ensure_output_dir()
    view = Gui.activeDocument().activeView()
    view.viewAxonometric()
    Gui.SendMsgToActiveView("ViewFit")

    sprays_z = compute_spray_centers_z()
    start_z = 1200 * SCALE
    end_z = - (SPRAY_SPACING * SPRAY_ZONE_COUNT + STRAND_LENGTH + 1200 * SCALE)

    for f in range(FRAMES):
        t = f / float(max(1, FRAMES - 1))
        zpos = start_z + (end_z - start_z) * t

        pl = strand.Placement
        pl.Base.z = zpos
        strand.Placement = pl

        # Perfil térmico: arranca a 1200°C en molde y baja hasta ~300°C
        base_temp = TEMP_MAX - (TEMP_MAX - 300) * t
        cooling = 0.0
        # Frente inferior del hilo
        strand_bottom = zpos
        for zc in sprays_z:
            dz = (strand_bottom - zc) / (180.0 * SCALE)
            inten = math.exp(-dz * dz)
            cooling += 250.0 * inten
        temp = max(80, min(TEMP_MAX, base_temp - cooling))
        strand.ViewObject.ShapeColor = temp_to_color(temp)

        if f < 3:
            Gui.SendMsgToActiveView("ViewFit")
        doc.recompute()

        img_path = os.path.join(OUTPUT_DIR, f"frame_{f:04d}.png")
        view.saveImage(img_path, IMG_W, IMG_H, 'Current')
        print(f"Frame {f+1}/{FRAMES}: z={zpos:.1f} temp={temp:.1f}°C → {img_path}")

    print(f"Usando ffmpeg: {FFMPEG_EXE}")
    # MP4
    try:
        mp4_path = os.path.join(OUTPUT_DIR, "animacion_colada_vertical.mp4")
        cmd = [FFMPEG_EXE, "-y", "-framerate", str(FPS), "-i", "frame_%04d.png", "-pix_fmt", "yuv420p", mp4_path]
        result = subprocess.run(cmd, cwd=OUTPUT_DIR, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Video generado: {mp4_path}")
            try:
                labeled_mp4 = os.path.join(OUTPUT_DIR, "animacion_colada_vertical_labeled.mp4")
                font = r"C:\\Windows\\Fonts\\arial.ttf"
                if not os.path.isfile(font):
                    font = r"C:\\Windows\\Fonts\\segoeui.ttf"
                # Construir overlay (caja + textos)
                x0 = "w-520"; y0 = "40"
                box = f"drawbox=x={x0}:y={y0}:w=500:h=h-80:color=black@0.6:t=fill"
                def dt(text, dy):
                    # escapar ':' y ','
                    safe = text.replace(':', '\\:').replace(',', '\\,')
                    return f",drawtext=fontfile='{font}':text='{safe}':x=w-500+20:y={dy}:fontsize=26:fontcolor=white"
                lines = [
                    "Horno de Induccion\\nCapacidad 5 ton/h \\| Potencia 3500 kW",
                    "Sistema de Fundicion\\nIncluye crisol refractario",
                    "Sistema de Colada Continua\\nPara palanquillas y bolas 150x150mm",
                    "Moldeadora de Bolas\\nSistema de moldeado para bolas de acero",
                    "Transformador Electrico\\nPotencia 4000 kVA",
                    "Sistema de Enfriamiento\\nTorre 500 m3/h",
                    "Grua Puente\\nCapacidad 15 t",
                    "Filtracion de Humos\\nCaptacion y filtrado",
                    "Cargador de Chatarra\\nSistema automatizado",
                    "PLC y Sistema SCADA\\nControl automatizado completo",
                    "Sensores y Medicion\\nTemperatura \\| nivel \\| flujo",
                    "Sistema de Seguridad\\nAlarmas y paradas de emergencia",
                ]
                filter_str = box
                y = 60
                for line in lines:
                    filter_str += dt(line, y)
                    y += 60
                cmd_label = [
                    FFMPEG_EXE, "-y", "-i", mp4_path,
                    "-vf", filter_str,
                    "-pix_fmt", "yuv420p", labeled_mp4
                ]
                rlab = subprocess.run(cmd_label, capture_output=True, text=True)
                if rlab.returncode == 0:
                    print(f"✓ Video con panel generado: {labeled_mp4}")
                    # GIF desde el MP4 etiquetado
                    palette = os.path.join(OUTPUT_DIR, "palette_lbl.png")
                    gif_out = os.path.join(OUTPUT_DIR, "animacion_colada_vertical_labeled.gif")
                    rp1 = subprocess.run([FFMPEG_EXE, "-y", "-i", labeled_mp4, "-vf",
                                           f"fps={FPS},scale={IMG_W}:{IMG_H}:flags=lanczos,palettegen", palette],
                                          capture_output=True, text=True)
                    rp2 = subprocess.run([FFMPEG_EXE, "-y", "-i", labeled_mp4, "-i", palette, "-lavfi",
                                           f"fps={FPS},scale={IMG_W}:{IMG_H}:flags=lanczos,paletteuse=dither=sierra2_4a",
                                           gif_out], capture_output=True, text=True)
                    if rp1.returncode == 0 and rp2.returncode == 0:
                        print(f"✓ GIF con panel generado: {gif_out}")
                else:
                    print("⚠ Error creando video con panel:")
                    print(rlab.stderr[:4000])
            except Exception as e:
                print(f"⚠ No se pudo etiquetar el video: {e}")
        else:
            print("⚠ ffmpeg fallo al crear MP4:")
            print(result.stderr[:4000])
    except Exception as e:
        print(f"⚠ Error creando MP4: {e}")
    # GIF
    try:
        palette_path = os.path.join(OUTPUT_DIR, "palette.png")
        gif_path = os.path.join(OUTPUT_DIR, "animacion_colada_vertical.gif")
        cmd_palette = [FFMPEG_EXE, "-y", "-i", "frame_%04d.png", "-vf", f"fps={FPS},scale={IMG_W}:{IMG_H}:flags=lanczos,palettegen", palette_path]
        cmd_gif = [FFMPEG_EXE, "-y", "-framerate", str(FPS), "-i", "frame_%04d.png", "-i", palette_path, "-lavfi", f"fps={FPS},scale={IMG_W}:{IMG_H}:flags=lanczos,paletteuse=dither=sierra2_4a", gif_path]
        r1 = subprocess.run(cmd_palette, cwd=OUTPUT_DIR, capture_output=True, text=True)
        r2 = subprocess.run(cmd_gif, cwd=OUTPUT_DIR, capture_output=True, text=True) if r1.returncode == 0 else None
        if r1.returncode == 0 and r2 and r2.returncode == 0:
            print(f"✓ GIF generado: {gif_path}")
        else:
            print("⚠ ffmpeg fallo al crear GIF:")
            if r1.returncode != 0:
                print(r1.stderr[:4000])
            elif r2:
                print(r2.stderr[:4000])
    except Exception as e:
        print(f"⚠ Error creando GIF: {e}")
    # Fallback imageio
    try:
        gif_path = os.path.join(OUTPUT_DIR, "animacion_colada_vertical.gif")
        if not os.path.exists(gif_path):
            import imageio.v2 as imageio
            frame_paths = sorted(glob.glob(os.path.join(OUTPUT_DIR, "frame_*.png")))
            if frame_paths:
                images = [imageio.imread(p) for p in frame_paths]
                imageio.mimsave(gif_path, images, fps=FPS, loop=0)
                print(f"✓ GIF generado con imageio: {gif_path}")
    except Exception:
        pass


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    """Función principal de ejecución"""
    
    print("\n" + "="*80)
    print("GENERADOR AUTOMÁTICO: SISTEMA DE INDUCCIÓN DE PALANQUILLAS")
    print("="*80 + "\n")
    
    # Crear documento
    doc = create_document()
    
    if PROCESS_MODE == 'casting_vertical':
        # Colada continua vertical
        strand = create_strand_vertical(doc)
        tundish = create_tundish(doc)
        mold = create_mold(doc)
        vr = create_vertical_rollers(doc)
        sprays = create_spray_zones(doc)
        # Equipos periféricos
        equip = []
        equip += create_induction_furnace(doc)
        equip += create_transformer(doc)
        equip += create_cooling_tower(doc)
        equip += create_bridge_crane(doc)
        equip += create_fume_filter(doc)
        equip += create_scrap_loader(doc)
        equip += create_plc_scada(doc)
        equip += create_ball_molder(doc)
        equip += create_sensors_and_safety(doc)
    else:
        # Inducción horizontal (modo anterior)
        billet = create_billet(doc)
        coils = create_all_coils(doc)
        rollers = create_all_rollers(doc)
        columns = create_frame(doc)
    
    # Crear componentes secundarios (opcional)
    sensors = []
    pipes = []
    if PROCESS_MODE != 'casting_vertical':
        if CREATE_SENSORS:
            sensors = create_temperature_sensors(doc)
        if CREATE_PIPES:
            pipes = add_cooling_pipes(doc)
    panel = create_control_panel(doc)
    
    # Agregar información
    add_system_info(doc)
    
    # Organizar (solo para modo horizontal)
    if PROCESS_MODE != 'casting_vertical':
        organize_in_groups(doc, billet, coils, rollers, columns, sensors, pipes, panel)
    
    # Configurar vista
    set_view(doc)
    
    # Actualizar documento
    doc.recompute()
    
    # Guardar y exportar STEP automáticamente
    try:
        fcstd_path = os.path.join(BASE_DIR, "Sistema_Induccion_Palanquillas.FCStd")
        step_path = os.path.join(BASE_DIR, "Sistema_Induccion_Palanquillas_Completo.stp")
        
        # Guardar documento nativo de FreeCAD
        doc.saveAs(fcstd_path)
        print(f"✓ Guardado: {fcstd_path}")
        
        # Exportar como STEP (AP214)
        try:
            import Import
        except Exception:
            # Compatibilidad con versiones antiguas
            import ImportGui as Import
        
        exportables = [obj for obj in doc.Objects if hasattr(obj, 'Shape')]
        Import.export(exportables, step_path)
        print(f"✓ Exportado STEP: {step_path}")
    except Exception as e:
        print(f"⚠ Error al guardar/exportar: {e}")

    # Animación y exportación de fotogramas/MP4
    try:
        if PROCESS_MODE == 'casting_vertical':
            animate_casting_vertical(doc, strand)
        else:
            animate_and_export(doc, billet)
    except Exception as e:
        print(f"⚠ Animación omitida: {e}")

    # Mostrar instrucciones
    export_instructions()
    
    print("\n✓ PROCESO COMPLETADO")
    print("="*80 + "\n")
    
    return doc


# ============================================================================
# EJECUTAR
# ============================================================================

if __name__ == "__main__":
    main()

