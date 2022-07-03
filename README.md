# ct-simulator

Servidor de simulacion. Provee servicios de simulación de las reglas de contagios según la configuración que re provea.

## Usage
### Setup

`pip3 install -r app/requirements.txt`

### Test

TODO

### Run Local

`python3 app/main.py`

## Simulación

### Parametros

Recibe las reglas de contagio a simular y la configuracion de la simulación:

```
Reglas:

- contagionRisk: Riesgo bajo (0), medio (1), alto (2)
- durationValue: Duracion del contacto
- durationCmp: Mayor o menor
- m2Value: Tamaño del establecimiento
- m2Cmp: Mayor o menor
- openSpace: Espacio abierto (true) o cerrado (false)
- vaccinated: Estado de vacunacion, sin vacunas (0), parcialmente (1), totalmente (2)

Configuracion:

- n_pop: Cantidad de personas
- n_places: Cantidad de establecimientos
- t: Cantidad de dias,
- mobility: Mobilidad
    - frequency: Cantidad de veces que sale en un dia
    - variability: Cantidad de establecimientos distintos que visita
- seed: Para la repetibilidad de la simulacion,
- init_infected: Porcentaje de personas que comienzan contagiadas (0-1),
- infected_days: Duracion del virus en dias,
- lockdown_restriction: Duracion de la restriccion por riesgo alto o medio en dias,
- partially_vaccinated: Porcentaje de usuarios parcialmente vacunados (0-1),
- fully_vaccinated: Porcentaje de usuarios totalmente vacunados (0-1),
- incubation_period: Cantidad de dias que tarda en manifestarse el virus.

```

### Consideraciones de la simulación

- En una pandemia el movimiento es reducido pero existe
- Una persona va a por lo menos `variability` lugares, (trabajo, supermercado, farmacia, etc )
- Cada persona va a visitar `frequency` de esos `variability` lugares cada dia ciclando por el `t` tiempo en el que transcurre la simulacion, a menos que `frequency` se vea reducido por alguna restriccion.
- Todas las personas se comportan similar (visitan la misma cantidad de establecimientos la misma cantidad de veces)
- Todas las personas respetan las normas (si su movilidad se ve reducida)
- Los establecimientos son uniformes.
- Todos los establecimientos tienen la misma probabilidad de ser visitados

**NIVELES DE RIESGO:**
- Alto: movilidad reducida a 0, no puede visitar lugares por `lockdown_restriction` dias
- Medio: movilidad reducida a la mitad de `frequency` lugares por `lockdown_restriction` dias
- Bajo: visita la totalidad de `frequency` lugares configurada




