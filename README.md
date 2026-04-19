# 🏭 Sistema de Control de Calidad de Neumáticos
### Arquitecturas de software distribuidas

**Autores:** Asier Sanchez · Unai Pinilla

---

## Descripción

Sistema distribuido de control de calidad para una línea de fabricación de neumáticos. Está formado por dos subsistemas independientes con bajo acoplamiento que se comunican mediante una API REST: la **Planta de Fabricación** (Subsistema A) genera neumáticos de forma simulada y los envía al sistema de **Control de Calidad** (Subsistema B), que los evalúa y devuelve una decisión de aceptación o rechazo.

---

## Arquitectura

```
┌─────────────────────────────────────┐          HTTP POST
│       SUBSISTEMA A — Planta         │  ──────────────────────►  ┌──────────────────────────────────────┐
│                                     │   /api/inspeccionar        │     SUBSISTEMA B — Calidad            │
│  FabricaNeumaticoAleatorio          │                            │                                      │
│  [Patrón Factory Method]            │  ◄──────────────────────  │  InspectorCalidad                    │
│                                     │   200 OK / 406 Rejected    │  [Patrón Strategy]                   │
│  · Si hay red  → POST al servidor   │                            │  · ReglaRadio  [15.8 – 16.2 pulg.]  │
│  · Sin red     → JSON local         │                            │  · ReglaPeso   [9.0 – 10.0 kg]      │
└─────────────────────────────────────┘                            │  · ReglaHuella [>= 1.6 mm]           │
                                                                   └──────────────────────────────────────┘
```

---

## Reglas de calidad

| Atributo | Rango válido | Resultado si falla |
|---|---|---|
| `radio_pulgadas` | 15.8 — 16.2 | HTTP 406 RECHAZADO |
| `peso_kg` | 9.0 — 10.0 | HTTP 406 RECHAZADO |
| `profundidad_huella_mm` | >= 1.6 mm | HTTP 406 RECHAZADO |
| Todos correctos | — | HTTP 200 ACEPTADO |

---

## Estructura del proyecto

```
.
├── subsistema_a_planta/
│   ├── modelos/            # Entidad Neumatico
│   ├── fabrica/            # Patrón Factory Method
│   ├── cliente/            # Cliente REST + fallback local
│   ├── tests/              # Pruebas unitarias y de componente
│   ├── main_a.py           # Punto de entrada
│   └── requirements.txt
│
├── subsistema_b_calidad/
│   ├── modelos/            # Entidad Neumatico (recepción)
│   ├── estrategias/        # Patrón Strategy (ReglaRadio, ReglaPeso, ReglaHuella)
│   ├── servicio/           # InspectorCalidad — contexto del Strategy
│   ├── api/                # Endpoints Flask REST
│   ├── tests/              # Pruebas unitarias y de componente
│   ├── main_b.py           # Punto de entrada del servidor
│   └── requirements.txt
│
├── tests_sistema/          # Pruebas de integración E2E
├── .github/workflows/      # Pipeline CI/CD (GitHub Actions)
├── conftest.py             # Configuración global de pytest
└── sonar-project.properties
```

---

## Instalación

Cada subsistema tiene sus propias dependencias. Instálalas desde la raíz del proyecto:

```bash
pip install -r subsistema_a_planta/requirements.txt
pip install -r subsistema_b_calidad/requirements.txt
```

> Se recomienda usar un entorno virtual (`python -m venv venv`).

---

## Demo — Cómo ejecutar el sistema

### 1. Arrancar el Subsistema B (servidor) — Terminal 1

```bash
cd subsistema_b_calidad
python main_b.py
```

Deberías ver:

```
═══════════════════════════════════════════════════════
  SUBSISTEMA B — SERVIDOR DE CALIDAD ACTIVO
  URL: http://localhost:5000/api/inspeccionar
  Stats: http://localhost:5000/api/estadisticas
═══════════════════════════════════════════════════════
```

### 2. Ejecutar el Subsistema A (planta) — Terminal 2

```bash
cd subsistema_a_planta
python main_a.py          # fabrica 5 neumáticos (por defecto)
python main_a.py --n 10   # fabrica 10 neumáticos
```

Salida esperada:

```
09:31:00 [INFO] SubsistemaA — ════════════════════════════════════════════════════
09:31:00 [INFO] SubsistemaA —   SUBSISTEMA A — INICIO DE PRODUCCIÓN (5 neumáticos)
09:31:00 [INFO] SubsistemaA — ════════════════════════════════════════════════════
09:31:00 [INFO] SubsistemaA — [1/5] Fabricado → Neumatico(id='...', radio=16.05, peso=9.71, huella=4.2)
09:31:00 [INFO] SubsistemaA —        Enviado [RED] → HTTP 200 → ACEPTADO
09:31:00 [INFO] SubsistemaA — [2/5] Fabricado → Neumatico(id='...', radio=14.31, peso=9.5, huella=3.0)
09:31:00 [INFO] SubsistemaA —        Enviado [RED] → HTTP 406 → RECHAZADO
...
09:31:00 [INFO] SubsistemaA —   RESUMEN: Aceptados=3 | Rechazados=2 | Local=0
```

### 3. Consultar estadísticas en tiempo real

```bash
curl http://localhost:5000/api/estadisticas
```

```json
{
  "inspeccionados": 5,
  "aceptados": 3,
  "rechazados": 2
}
```

### 4. Probar un neumático manualmente

**Neumático válido (esperado: HTTP 200):**

```bash
curl -X POST http://localhost:5000/api/inspeccionar \
  -H "Content-Type: application/json" \
  -d '{
    "id_neumatico": "prueba-manual-001",
    "radio_pulgadas": 16.0,
    "peso_kg": 9.5,
    "profundidad_huella_mm": 3.2
  }'
```

**Neumático con huella desgastada (esperado: HTTP 406):**

```bash
curl -X POST http://localhost:5000/api/inspeccionar \
  -H "Content-Type: application/json" \
  -d '{
    "id_neumatico": "prueba-manual-002",
    "radio_pulgadas": 16.0,
    "peso_kg": 9.5,
    "profundidad_huella_mm": 0.8
  }'
```

### 5. Modo sin red (fallback local)

Si el Subsistema B no está disponible cuando se ejecuta el A, los neumáticos se guardan automáticamente en `subsistema_a_planta/data/pendientes.json` en lugar de perderse.

---

## Pruebas

Ejecutar toda la suite desde la raíz del proyecto:

```bash
# Unitarias y de componente — Subsistema A
cd subsistema_a_planta
python -m pytest tests/ -v

# Unitarias y de componente — Subsistema B
cd subsistema_b_calidad
python -m pytest tests/ -v

# Integración E2E (requiere ambos subsistemas instalados)
cd ..
python -m pytest tests_sistema/ -v
```

O todas de golpe desde la raíz:

```bash
python -m pytest subsistema_a_planta/tests/ subsistema_b_calidad/tests/ tests_sistema/ -v
```

---

## Pipeline CI/CD

El fichero `.github/workflows/python-ci-cd.yml` define un pipeline de 4 etapas que se ejecuta automáticamente en cada push y Pull Request:

```
BUILD  ──►  TEST Unitarios/Componente  ──►  TEST Sistema E2E  ──►  SonarCloud
```

| Etapa | Qué hace |
|---|---|
| **BUILD** | Instala dependencias y verifica que los imports funcionan |
| **TEST** | Ejecuta las pruebas unitarias y de componente de ambos subsistemas con reporte de cobertura |
| **TEST E2E** | Levanta el servidor B en un hilo y ejecuta el flujo completo real |
| **SONARCLOUD** | Análisis estático de calidad y cobertura (solo en `main` y PRs) |

---

## API Reference

### `POST /api/inspeccionar`

Evalúa un neumático contra las tres reglas de calidad.

**Body:**
```json
{
  "id_neumatico": "string",
  "radio_pulgadas": 16.0,
  "peso_kg": 9.5,
  "profundidad_huella_mm": 3.2
}
```

**Respuesta 200 — ACEPTADO:**
```json
{
  "id_neumatico": "...",
  "decision": "ACEPTADO",
  "resultados": [
    {"regla": "ReglaRadio",  "aprobado": true,  "detalle": "OK: radio=16.0 dentro de [15.8, 16.2]"},
    {"regla": "ReglaPeso",   "aprobado": true,  "detalle": "OK: peso=9.5 dentro de [9.0, 10.0]"},
    {"regla": "ReglaHuella", "aprobado": true,  "detalle": "OK: huella=3.2 mm >= mínimo 1.6 mm"}
  ],
  "estadisticas": {"inspeccionados": 1, "aceptados": 1, "rechazados": 0}
}
```

**Respuesta 406 — RECHAZADO** (misma estructura, `"decision": "RECHAZADO"` y `"aprobado": false` en la regla que falla).

### `GET /api/estadisticas`

Devuelve los contadores acumulados de la sesión actual.

### `GET /api/health`

Health-check del servidor. Devuelve `{"status": "ok"}`.

---

## Patrones de diseño

### Factory Method — Subsistema A

Implementado en `subsistema_a_planta/fabrica/fabrica_neumatico.py`. Permite generar neumáticos sin que el código cliente conozca los detalles de construcción.

| Rol | Clase |
|---|---|
| Creador abstracto | `FabricaNeumaticoBase` |
| Creador concreto | `FabricaNeumaticoValido` — siempre dentro de tolerancias |
| Creador concreto | `FabricaNeumaticoDefecto` — siempre con al menos un defecto |
| Creador concreto | `FabricaNeumaticoAleatorio` — 70% válidos / 30% defectuosos |

### Strategy — Subsistema B

Implementado en `subsistema_b_calidad/estrategias/`. Permite añadir o modificar reglas de calidad sin tocar el Inspector.

| Rol | Clase |
|---|---|
| Contexto | `InspectorCalidad` |
| Interfaz (Strategy) | `ReglaCalidad` |
| Estrategia concreta | `ReglaRadio` |
| Estrategia concreta | `ReglaPeso` |
| Estrategia concreta | `ReglaHuella` |
