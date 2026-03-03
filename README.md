# Dungeons of Aethoria

Un RPG de texto estilo D&D años 80, construido en Python puro.
Con humor argentino incluido. Sin dependencias externas. Sin excusas.

---

## Requisitos

- **Python 3.11 o superior**
- No se requieren librerías externas (stdlib puro, sin `pip install` de nada)

---

## Cómo jugar

```bash
cd dungeons-of-aethoria
python main.py
```

### Terminal recomendada

| Sistema | Terminal recomendada           |
|---------|--------------------------------|
| Windows | Windows Terminal, PowerShell 7 |
| Mac     | Terminal.app, iTerm2           |
| Linux   | Cualquier terminal moderna     |

> En el CMD clásico de Windows los caracteres de borde pueden verse raros.
> Con Windows Terminal se arregla solo.

---

## Clases disponibles

| Clase     | HP  | MP  | Stat principal | En criollo                                      |
|-----------|-----|-----|----------------|-------------------------------------------------|
| Guerrero  | 120 | 20  | FUE            | Más cicatrices que el auto del tío de un amigo  |
| Mago      | 60  | 120 | INT            | No consiguió laburo en su especialidad          |
| Pícaro    | 80  | 40  | DES            | Opera desde las sombras con mucho dramatismo    |
| Paladín   | 100 | 70  | FUE / CAR      | Un poco intenso en los asados                   |
| Arquero   | 75  | 40  | DES            | Apareció desde atrás de un árbol                |
| Bárbaro   | 140 | 15  | FUE            | Su plan es ir para adelante hasta que algo pare |
| Monje     | 85  | 60  | DES / SAB      | La paz interior son cinco piñas en la cara      |
| Explorador| 78  | 45  | DES            | Lee la mazmorra como si fuera el subte          |
| Hechicero | 65  | 100 | INT / CAR      | El 65% de las veces sale bien                   |
| Brujo     | 70  | 85  | CAR            | El alquiler no se paga solo                     |

---

## Mecánicas principales

- **Combate por turnos** — ataque básico, habilidades especiales (con coste de MP), pociones, huida (estrategia válida).
- **12 efectos de estado** — veneno, quemadura, aturdimiento, maldición, escudo, rabia, drenaje, y más.
- **10 pisos de mazmorra** con dificultad progresiva. Siempre hay más.
- **6 tipos de habitación** — combate, tesoro, descanso, mercader, trampa, misterio, y sala de jefe al final de cada piso.
- **Subida de nivel** — stats crecen automáticamente según la clase, hasta nivel 20.
- **Inventario** — hasta 20 objetos, equipo en arma, armadura y anillo.
- **Guardado automático** después de cada habitación en formato JSON.
- **3 jefes** — Dragón de Aethoria (piso 3), Lich Archmago (piso 6), Archfiend Malachar (piso 9).

---

## Árbol de habilidades

Cada clase tiene 3 habilidades base más 3 desbloqueables por nivel, organizadas en dos tiers:

| Tier     | Nombre                              | Nivel mínimo |
|----------|-------------------------------------|--------------|
| Avanzada | Primera habilidad extra de la clase | 4 — 5        |
| Avanzada | Segunda habilidad extra             | 6 — 8        |
| Élite    | Habilidad definitiva de la clase    | 11 — 16      |

Las habilidades de tier Élite requieren haber desbloqueado las anteriores primero.
El campamento muestra `[NUEVO!]` cuando hay habilidades disponibles para desbloquear.

---

## Misiones secundarias

16 misiones con condiciones variadas y recompensas en oro, XP y objetos:

| Tipo              | Ejemplos                                             |
|-------------------|------------------------------------------------------|
| Matar enemigos    | 5 goblins, 10 no-muertos, 3 jefes, 20 o 50 en total  |
| Tipos específicos | 3 orcos, 2 demonios                                  |
| Progreso          | Completar 3 o 7 pisos, llegar a nivel 5 o 10         |
| Recursos          | Acumular 500 o 2000 monedas de oro                   |
| Especiales        | Esquivar 3 trampas, huir exitosamente de 3 combates  |

El progreso se guarda automáticamente y se muestra con barra visual en el campamento.

---

## Tienda permanente

Disponible en el campamento entre pisos. El stock:

- Se renueva cada 2 pisos con items de mayor calidad
- Escala con el piso actual (comunes al principio, raros y legendarios más adelante)
- Persiste guardado en el archivo de partida
- Siempre tiene pociones, armas, armaduras y chance de item especial desde el piso 5

---

## Mapa ASCII del piso

Antes de cada habitación se muestra el mapa completo del piso actual:

```
  [ 1*]- [ . ]- [ . ]- [ . ]- [ . ]
    |      |      |      |      |
  [ . ]- [ . ]- [ . ]- [ . ]- [!!!]
```

| Símbolo | Significado       |
|---------|-------------------|
| `[N*]`  | Habitación actual |
| `[ C ]` | Combate           |
| `[ T ]` | Tesoro            |
| `[ R ]` | Descanso          |
| `[ $ ]` | Mercader          |
| `[ X ]` | Trampa            |
| `[ ? ]` | Misterio          |
| `[!!!]` | Jefe              |
| `[ . ]` | Sin explorar      |

---

## Nombres procedurales

Cada partida genera nombres únicos para pisos y habitaciones combinando prefijos,
raíces y sufijos al azar. El mismo piso 1 puede llamarse distinto en cada run:

```
Partida 1 → "The Frozen Abyss of Kharolgur"  —  "The Haunted Passage"
Partida 2 → "The Crumbling Crypt of Malendra" —  "The Forsaken Alcove"
Partida 3 → "The Wretched Lair of Vorazoth"  —  "The Bleeding Hall"
```

---

## Enemigos por dificultad

| Tier           | Enemigos                                       | Pisos aproximados          |
|----------------|------------------------------------------------|----------------------------|
| 1 — Flojitos   | Goblin, Goblin Chamán, Rata Gigante, Esqueleto | 1 — 3                      |
| 2 — Moderados  | Orco, Elfo Oscuro, Caballero Zombie, Bruja     | 3 — 6                      |
| 3 — Peligrosos | Señor Vampiro, Gólem de Piedra, Demonio Menor  | 6 — 9                      |
| 4 — Jefes      | Dragón, Lich, Archfiend Malachar               | Último cuarto de cada piso |

---

*"No todos los que vagan por mazmorras están perdidos."*
*"La mayoría sí. Completamente."*

---

## Licencia

MIT License — hacé lo que quieras con el código, solo dejá el crédito.
