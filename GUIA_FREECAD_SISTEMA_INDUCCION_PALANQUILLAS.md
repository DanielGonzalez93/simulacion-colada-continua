# 🔥 GUÍA COMPLETA FREECAD
## SISTEMA DE CALENTAMIENTO POR INDUCCIÓN DE PALANQUILLAS
### Basado en: [Induction Billet Blueprint](https://preview--induction-billet-blueprint.lovable.app/)

---

## 📋 ÍNDICE

1. [Preparación de FreeCAD](#preparación)
2. [Modelado de Palanquilla](#palanquilla)
3. [Sistema de Bobinas de Inducción](#bobinas)
4. [Estructura de Soporte](#estructura)
5. [Sistema de Transporte](#transporte)
6. [Ensamble Completo](#ensamble)
7. [Exportación a STEP](#exportacion)
8. [Importación en Inventor](#importacion)

---

## 🔧 1. PREPARACIÓN DE FREECAD {#preparación}

### Instalación
1. Descargar FreeCAD desde: https://www.freecad.org/
2. Instalar versión 0.21 o superior
3. Abrir FreeCAD

### Configuración Inicial
```
Edit → Preferences → General → Units
- Unit System: Metric
- Number of decimals: 2

Edit → Preferences → Display → 3D View
- Background: Simple color (negro o gris oscuro)
- Anti-aliasing: ON
```

### Crear Nuevo Documento
```
File → New (Ctrl+N)
File → Save As... → "Sistema_Induccion_Palanquillas.FCStd"
```

---

## 🔩 2. MODELADO DE PALANQUILLA {#palanquilla}

### 2.1 Crear Nueva Pieza

```
Workbench: Part Design (cambiar en menú superior)
Create Body (ícono de cubo azul)
Create Sketch (ícono lápiz)
→ Seleccionar: XY_Plane
```

### 2.2 Dibujar Sección Cuadrada

**Paso 1: Rectángulo**
```
Sketch → Geometries → Rectangle
- Click en origen (0, 0)
- Dimensiones: 130 × 130 mm (sección de palanquilla)
```

**Paso 2: Restricciones**
```
Seleccionar rectángulo
Sketch → Constraints → Symmetric (respecto a ejes)
Close Sketch (ícono ✓ verde)
```

### 2.3 Extruir Palanquilla

```
Part Design → Additive → Pad
- Length: 12000 mm (12 metros - longitud típica)
- Symmetric to plane: No
- Click OK
```

### 2.4 Chaflanes (Opcional)

```
Part Design → Dress-up → Chamfer
- Seleccionar aristas superiores
- Size: 5 mm
- Click OK
```

### 2.5 Propiedades del Material

```
Click derecho en "Body" → Appearance
- Material: Steel (Acero)
- Color: RGB (150, 150, 150) - Gris metálico

Guardar pieza:
File → Export... → "Palanquilla_130x130x12000.stp"
```

---

## ⚡ 3. SISTEMA DE BOBINAS DE INDUCCIÓN {#bobinas}

### 3.1 Crear Nueva Pieza (Bobina Individual)

```
File → New
Workbench: Part Design
Create Body
Create Sketch → XY_Plane
```

### 3.2 Dibujar Perfil de Bobina

**Paso 1: Sección del Conductor**
```
Sketch → Rectangle
- Centro: (300, 0) mm
- Dimensiones: 40 × 80 mm (sección rectangular del conductor de cobre)
```

**Paso 2: Círculo Interno**
```
Sketch → Circle
- Centro: (0, 0)
- Radio: 280 mm (diámetro interno para palanquilla + clearance)
```

**Paso 3: Círculo Externo**
```
Sketch → Circle
- Centro: (0, 0)
- Radio: 340 mm (diámetro externo de bobina)
```

**Close Sketch**

### 3.3 Crear Anillo (Revolución)

```
Part Design → Additive → Revolution
- Axis: Vertical_Sketch_Axis
- Angle: 360°
- Click OK
```

### 3.4 Agregar Espiras (Patrón Helicoidal)

**Opción A: Simplificado (Anillo Sólido)**
```
Part Design → Pad
- Thickness: 200 mm (altura de bobina)
```

**Opción B: Detallado (Espiras Visibles)**
```
Sketch → Helix/Spiral
- Pitch: 20 mm (separación entre espiras)
- Height: 200 mm
- Turns: 10 vueltas

Part Design → Additive → Pipe
- Profile: Círculo Ø15mm (sección del tubo de cobre)
- Path: Helix
```

### 3.5 Propiedades Bobina

```
Appearance:
- Material: Copper
- Color: RGB (184, 115, 51) - Naranja cobre
- Metallic: Yes

Guardar:
File → Export... → "Bobina_Induccion.stp"
```

---

## 🏗️ 4. ESTRUCTURA DE SOPORTE {#estructura}

### 4.1 Marco Rectangular

```
Workbench: Part Design
Create Body → Create Sketch → XZ_Plane

Sketch → Rectangle
- Dimensiones: 800 × 500 mm
- Centro en origen

Part Design → Additive → Pad
- Length: 100 mm (perfil estructural)
- Mode: Symmetric
```

### 4.2 Columnas Verticales (4 unidades)

```
Create Sketch → XY_Plane
Sketch → Circle
- Radio: 50 mm
- Posición: (350, 200, 0)

Pad → Length: 1500 mm (altura)

Tools → Pattern → Rectangular Pattern
- Occurrences X: 2, Spacing: 700mm
- Occurrences Y: 2, Spacing: 400mm
```

### 4.3 Propiedades Estructura

```
Appearance:
- Material: Steel
- Color: RGB (100, 100, 120) - Gris azulado
```

---

## 🚂 5. SISTEMA DE TRANSPORTE {#transporte}

### 5.1 Rodillos de Transporte

**Paso 1: Crear Rodillo**
```
Create Body → Create Sketch → XY_Plane
Sketch → Circle
- Centro: (0, 0)
- Radio: 80 mm

Part Design → Revolution
- Axis: Horizontal
- Angle: 360°
- Length: 400 mm
```

**Paso 2: Patrón de Rodillos**
```
Tools → Pattern → Linear Pattern
- Direction: Eje X (longitudinal)
- Occurrences: 20
- Length: 12000 mm (cada 600mm)
```

### 5.2 Propiedades Rodillos

```
Appearance:
- Material: Steel
- Color: RGB (80, 80, 80) - Gris oscuro
```

---

## 📦 6. ENSAMBLE COMPLETO {#ensamble}

### 6.1 Crear Ensamble

```
File → New
Workbench: Assembly (o A2plus)

Assembly → Import Part
- Seleccionar: Palanquilla_130x130x12000.stp
- Click OK
```

### 6.2 Añadir Bobinas (Serie en Línea)

```
Assembly → Import Part
- Seleccionar: Bobina_Induccion.stp

Assembly → Constraint → Concentric
- Eje bobina con eje palanquilla

Assembly → Pattern → Linear Pattern
- Direction: Eje longitudinal
- Occurrences: 8 bobinas
- Spacing: 1500 mm entre bobinas
```

### 6.3 Añadir Estructura

```
Assembly → Import Part
- Seleccionar: Marco_Soporte.stp

Assembly → Constraint → Fixed
- Posición: Base (plano suelo)
```

### 6.4 Disposición Final

**Configuración Sistema Completo:**

```
VISTA LATERAL (CORTE):

         [Bobina 1] [Bobina 2] [Bobina 3] ... [Bobina 8]
              |          |          |              |
         ═════╬══════════╬══════════╬══════════════╬═════
         [======== PALANQUILLA 130×130mm =========]
         ═════╬══════════╬══════════╬══════════════╬═════
              |          |          |              |
           Rodillo    Rodillo    Rodillo        Rodillo
              |          |          |              |
         [=============== ESTRUCTURA ================]


DIMENSIONES:
- Longitud total sistema: 12,000 mm
- Número de bobinas: 8 unidades
- Separación entre bobinas: 1,500 mm
- Diámetro interno bobina: 280 mm
- Diámetro externo bobina: 340 mm
- Altura bobina: 200 mm
- Palanquilla: 130 × 130 × 12,000 mm
- Clearance (holgura): 75 mm por lado
```

---

## 💾 7. EXPORTACIÓN A STEP {#exportacion}

### 7.1 Preparar Ensamble

```
View → 3D View → Reset View (F)
View → Standard Views → Isometric
```

### 7.2 Verificación Pre-Exportación

```
Tools → Check Geometry
- Verificar que no haya errores
- Todas las piezas deben estar "Valid"

Assembly → Update
- Actualizar todas las restricciones
```

### 7.3 Exportar como STEP

```
File → Export...

Configuración:
- Files of type: STEP with colors (*.step *.stp)
- Nombre: "Sistema_Induccion_Palanquillas_Completo.stp"
- Location: Carpeta del proyecto

Opciones STEP:
☑ Export Legacy (para máxima compatibilidad)
☑ Geometric Curve Accuracy: 0.01 mm
☑ Write surface curves: Yes
☑ Export colors: Yes (para mantener materiales)

Click "Save"
```

### 7.4 Exportaciones Individuales (Recomendado)

Para mejor control en Inventor, exporta cada componente:

```
1. Palanquilla_130x130x12000.stp
2. Bobina_Induccion_01.stp ... Bobina_Induccion_08.stp
3. Marco_Estructura.stp
4. Rodillo_Transporte.stp
5. Sistema_Completo.stp (ensamble)
```

---

## 📥 8. IMPORTACIÓN EN INVENTOR {#importacion}

### 8.1 Abrir Inventor

```
Autodesk Inventor → New → Assembly (.iam)
File → Open

Files of type: STEP Files (*.stp; *.step)
Seleccionar: Sistema_Induccion_Palanquillas_Completo.stp

Opciones de Importación:
☑ Import as: Multiple solid bodies
☑ Create parametric: Yes
☑ Stitch surfaces: Yes
☑ Tolerance: 0.01 mm

Click "Open"
```

### 8.2 Verificación en Inventor

```
Tools → Inspect → Surface Analysis
- Verificar continuidad de superficies

View → Object Visibility → Origins
- Verificar que el origen esté correcto

Tools → Analyze → Interference
- Verificar que no haya interferencias
```

### 8.3 Convertir a Piezas Nativas (.ipt)

```
Para cada componente importado:
1. Click derecho → "Break Link"
2. Click derecho → "Save As" → Cambiar a .ipt
3. Editar y ajustar según necesidad
```

### 8.4 Crear Ensamble Nativo (.iam)

```
Assembly → Create Component
- Añadir cada pieza .ipt
- Aplicar restricciones:
  * Mate (contacto entre superficies)
  * Flush (alineación de caras)
  * Insert (ejes colineales)
```

---

## 🎨 9. DETALLES TÉCNICOS DEL SISTEMA

### Especificaciones de Palanquilla

```
PALANQUILLA DE ACERO:
- Sección: 130 × 130 mm
- Longitud: 12,000 mm (12 metros)
- Material: Acero al carbono
- Peso: ~1,590 kg
- Temperatura inicial: 20°C
- Temperatura objetivo: 1,200°C
```

### Especificaciones de Bobinas

```
BOBINA DE INDUCCIÓN:
- Diámetro interno: 280 mm
- Diámetro externo: 340 mm
- Altura: 200 mm
- Espiras: 10 vueltas
- Conductor: Tubo de cobre Ø15mm
- Refrigeración: Agua interna
- Potencia: 150 kW por bobina
- Frecuencia: 1-10 kHz
```

### Configuración del Sistema

```
DISPOSICIÓN:
- 8 bobinas en serie
- Separación: 1,500 mm
- Longitud total: 12,000 mm
- Clearance radial: 75 mm
- Velocidad avance: 0.5-2 m/min

POTENCIA TOTAL:
- 8 bobinas × 150 kW = 1,200 kW
- Eficiencia: 85-90%
- Tiempo calentamiento: 6-10 minutos
```

---

## 🔥 10. SIMULACIÓN DE CALENTAMIENTO

### Parámetros para Análisis Térmico

```
CONDICIONES INICIALES:
- Temperatura ambiente: 20°C
- Temperatura objetivo: 1,200°C
- Material: Acero AISI 1045

PROPIEDADES TÉRMICAS DEL ACERO:
- Conductividad térmica: 51.9 W/(m·K)
- Calor específico: 486 J/(kg·K)
- Densidad: 7,850 kg/m³
- Emisividad: 0.8

ZONAS DE CALENTAMIENTO:
Bobina 1: 20°C → 300°C
Bobina 2: 300°C → 500°C
Bobina 3: 500°C → 700°C
Bobina 4: 700°C → 850°C
Bobina 5: 850°C → 950°C
Bobina 6: 950°C → 1,050°C
Bobina 7: 1,050°C → 1,150°C
Bobina 8: 1,150°C → 1,200°C
```

### Gradiente Térmico

```
DISTRIBUCIÓN DE TEMPERATURA (Longitudinal):

1200°C ┤                               ╱━━━━━
1000°C ┤                         ╱━━━━━╯
 800°C ┤                   ╱━━━━━╯
 600°C ┤             ╱━━━━━╯
 400°C ┤       ╱━━━━━╯
 200°C ┤ ╱━━━━━╯
   0°C ┼━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━→
       0   2   4   6   8  10  12  14m
      [Entrada]  [Bobinas 1-8]  [Salida]
```

---

## ⚙️ 11. COMPONENTES ADICIONALES (Opcional)

### 11.1 Sistema de Enfriamiento

```
TUBERÍAS DE AGUA:
- Diámetro: 20 mm
- Material: Cobre
- Conexiones: 16 (2 por bobina)

FreeCAD:
Sketch → Circle Ø20mm
Part Design → Pipe
Path → Conectar bobinas en serie
```

### 11.2 Sensores de Temperatura

```
PIRÓMETROS:
- Cantidad: 8 (1 por bobina)
- Posición: Lateral, 500mm de bobina
- Tipo: Infrarrojo sin contacto

FreeCAD:
Part → Primitive → Cylinder
- Diámetro: 50mm
- Longitud: 150mm
```

### 11.3 Panel de Control

```
GABINETE ELÉCTRICO:
- Dimensiones: 800 × 600 × 300 mm
- Posición: Lateral del sistema

FreeCAD:
Sketch → Rectangle 800×600
Pad → 300mm
```

---

## 📊 12. LISTA DE MATERIALES (BOM)

```
ITEM | CANT | DESCRIPCIÓN                    | MATERIAL     | PESO
-----|------|--------------------------------|--------------|--------
001  |  1   | Palanquilla 130×130×12000mm   | Acero        | 1,590kg
002  |  8   | Bobina inducción Ø340×200mm   | Cobre        | 45kg c/u
003  |  20  | Rodillo transporte Ø160×400mm | Acero        | 25kg c/u
004  |  1   | Bastidor principal 12m         | Acero A36    | 850kg
005  |  4   | Columna soporte 1500mm         | Acero        | 60kg c/u
006  |  8   | Pirómetro infrarrojo           | Electrónico  | 2kg c/u
007  | 100m | Tubería cobre Ø20mm            | Cobre        | 150kg
008  |  1   | Panel control                  | Varios       | 120kg
-----|------|--------------------------------|--------------|--------
                                        PESO TOTAL:  ~3,500kg
```

---

## 🎯 13. CONSEJOS Y TRUCOS

### Optimización del Modelo

```
1. SIMPLIFICACIÓN:
   - No modelar roscas (usar líneas)
   - Chaflanes pequeños: omitir o simplificar
   - Tuberías: usar cilindros simples

2. PERFORMANCE:
   - Dividir ensamble grande en subensambles
   - Usar "Level of Detail" en Inventor
   - Exportar componentes críticos por separado

3. COMPATIBILIDAD:
   - Siempre exportar STEP AP214
   - Verificar unidades antes de exportar
   - Guardar versiones intermedias
```

### Solución de Problemas

```
PROBLEMA: "Archivo STEP no se abre en Inventor"
SOLUCIÓN:
- Exportar como STEP 214 (no 242)
- Reducir tolerancia a 0.001mm
- Exportar componentes individuales

PROBLEMA: "Geometría se ve mal en Inventor"
SOLUCIÓN:
- Aumentar precisión de curvas
- Verificar normales de superficies en FreeCAD
- Usar "Refine shape" antes de exportar

PROBLEMA: "Colores no se importan"
SOLUCIÓN:
- Usar "STEP with colors" en exportación
- En Inventor: View → Object Visibility → Show Colors
```

---

## 📄 14. ARCHIVOS GENERADOS

Al finalizar, deberías tener:

```
📁 Sistema_Induccion_Palanquillas/
├── 📄 Sistema_Induccion_Palanquillas.FCStd (proyecto FreeCAD)
├── 📄 Palanquilla_130x130x12000.stp
├── 📄 Bobina_Induccion_01.stp
├── 📄 Bobina_Induccion_02.stp
├── 📄 ... (hasta 08)
├── 📄 Marco_Estructura.stp
├── 📄 Rodillo_Transporte.stp
├── 📄 Sistema_Completo.stp
└── 📄 GUIA_FREECAD_SISTEMA_INDUCCION_PALANQUILLAS.md
```

---

## ✅ 15. CHECKLIST FINAL

Antes de exportar, verificar:

- [ ] Todas las piezas tienen dimensiones correctas
- [ ] No hay interferencias entre componentes
- [ ] Materiales asignados correctamente
- [ ] Origen del sistema en (0,0,0)
- [ ] Unidades en milímetros
- [ ] Geometría cerrada (sin huecos)
- [ ] Normales de superficies correctas
- [ ] Modelo simplificado (sin detalles innecesarios)
- [ ] Archivo guardado en formato FreeCAD nativo
- [ ] Exportación STEP AP214 exitosa

---

## 📚 16. RECURSOS ADICIONALES

### Tutoriales FreeCAD
- FreeCAD Documentation: https://wiki.freecad.org/
- YouTube: "FreeCAD Tutorial" - Multiple channels
- Forum: https://forum.freecad.org/

### Referencia Técnica
- STEP Format: ISO 10303
- Induction Heating: ASM Handbook Vol. 4C
- Blueprint Original: https://preview--induction-billet-blueprint.lovable.app/

---

## 🎓 CONCLUSIÓN

Has creado un modelo 3D completo de un sistema de calentamiento por inducción para palanquillas que:

✅ **Es paramétrico** - Fácil de modificar  
✅ **Compatible con Inventor** - Formato STEP universal  
✅ **Técnicamente preciso** - Basado en especificaciones reales  
✅ **Listo para simulación** - Con propiedades térmicas  
✅ **Profesional** - Incluye todos los componentes  

**¡Éxito con tu proyecto!** 🚀

---

**Versión:** 1.0  
**Fecha:** 2025-11-04  
**Software:** FreeCAD 0.21+ → Autodesk Inventor 2020+  
**Basado en:** [Induction Billet Blueprint](https://preview--induction-billet-blueprint.lovable.app/)

