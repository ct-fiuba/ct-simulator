import random
import itertools

"""
RULE:

id={rule.id}
contagionRisk={rule.contagionRisk}
durationValue={rule.durationValue}
durationCmp={rule.durationCmp}
m2Value={rule.m2Value}
m2Cmp={rule.m2Cmp}
openSpace={rule.openSpace}
n95Mandatory={rule.n95Mandatory}
vaccinated={rule.vaccinated}
vaccineReceived={rule.vaccineReceived}
vaccinatedDaysAgoMin={rule.vaccinatedDaysAgoMin}
illnessRecovered={rule.illnessRecovered}
illnessRecoveredDaysAgoMax={rule.illnessRecoveredDaysAgoMax}
index={rule.index}

NIVELES DE RIESGO:
Alto: movilidad reducida a 0, no puede visitar lugares
Medio: movilidad reducida a solo visitar 1 lugar por dia
Bajo: visita 2/3 lugares por dia


ASUMO:

- En una pandemia el movimiento es reducido pero existe
- Una persona va a por lo menos 5 lugares, (trabajo, supermercado, casa(nocuenta), farmacia y 2 comercios mas )
- Cada persona va a visitar esos 5 lugares ciclando por el T tiempo en el q transcurre la simulacion

SIMULACION:
- Creo N habitantes con caracteristicas random (con un % contagiado)
- Creo M espacios posiblides para visitar con caracteristicas random
- Creo Reglas pasadas por parametro
- Asigno 5 lugares a cada persona para visitar durante la simulacion
- Cada dia q pasa la persona va a 2/3 de los lugares para visitar, amenos q su mobilidad se vea reducida
- Defino probabilidades de contagio segun los riesgos de la regla
- Defino un tiempo de contagio que tiene un contagiado (por cuantos dias es contagioso)

"""

LOW_RISK, MID_RISK, HIGH_RISK = 0, 1, 2

TOTAL_RISK = 2

FAV_PLACES = 5

LOCKDOWN_RESTRICTION = 7  # days

INFECTED_WINDOW = 5  # days

DAY = 24

HOUR = 60

INFECTED_PROBABILITIES = {LOW_RISK: 0.01, MID_RISK: 0.1, HIGH_RISK: 0.5}


def shared_time(a, b):  # in minutes
    range_a = range(a.timestamp.minute, a.timestamp.minute + a.duration)
    range_b = range(b.timestamp.minute, b.timestamp.minute + b.duration)

    return len(set(range_a) & set(range_b))


class Rule:
    def __init__(self, params):
        self._parse_field("contagionRisk", params)
        self._parse_field("durationValue", params)
        self._parse_field("durationCmp", params)
        self._parse_field("m2Value", params)
        self._parse_field("m2Cmp", params)
        self._parse_field("openSpace", params)
        self._parse_field("vaccinated", params)
        self._parse_field("illnessRecovered", params)
        self._parse_field("illnessRecoveredDaysAgoMax", params)

        # self.n95Mandatory=params['n95Mandatory']
        # self.vaccinated=params['vaccinated']
        # self.vaccineReceived=params['vaccineReceived']
        # self.vaccinatedDaysAgoMin=params['vaccinatedDaysAgoMin']
        # self.illnessRecovered=params['illnessRecovered']
        # self.illnessRecoveredDaysAgoMax=params['illnessRecoveredDaysAgoMax']
        # for key, value in params.items():
        #    setattr(self, key, value)

    def _parse_field(self, field, info):
        setattr(self, field, info[field] if field in info else None)
        if field in info:
            print(info[field])

    def apply(self, visit_a, visit_b, shared):
        infected = visit_a.person.infected or visit_b.person.infected

        if not infected:
            return

        check = True
        if self.durationValue != None:
            if self.durationCmp == "<":
                check &= shared <= self.durationValue
            else:
                check &= shared >= self.durationValue

        if self.m2Value != None:
            if self.m2Cmp == "<":
                check &= visit_a.place.m2 <= self.m2Value
            else:
                check &= visit_a.place.m2 >= self.m2Value

        if self.openSpace != None:
            check &= visit_a.place.openSpace == self.openSpace

        if check:
            return self.contagionRisk


class Person:
    def __init__(self):
        self.vacinated = random.randint(0, 1)
        self.recovered = False

        self.infected = False
        self.infected_counter = 0
        self.locked_down = False
        self.locked_down_counter = 0
        self.fav_places = []
        self.risk = LOW_RISK

    def places_to_visit(self):
        n_places_to_visit = random.randint(
            0, TOTAL_RISK - self.risk
        )  # inverso al riesgo
        n_places = len(self.fav_places)
        places = []
        for _ in range(n_places_to_visit):
            idx = random.randint(1, n_places - 1)

            places.append(idx)

        return places

    def update_risk(self, risk):
        self.risk = risk
        if risk == HIGH_RISK:  # reduce mobility
            # print("REDUCED MOBILITY")
            self.locked_down = True
            self.locked_down_counter = LOCKDOWN_RESTRICTION

        proba_infected = random.random()

        if proba_infected < INFECTED_PROBABILITIES[self.risk]:
            self.infected = True
            self.infected_counter = INFECTED_WINDOW


class Place:
    def __init__(self, id):
        self.id = id
        self.openSpace = random.randint(0, 1)
        self.n95mandatory = random.randint(0, 1)
        self.m2 = random.randint(5, 100)
        self.estimatedVisitDuration = random.randint(5, 60)  # min


class Timestamp:
    def __init__(self, day, hour, minute):
        self.day = day
        self.hour = hour
        self.minute = minute


class Visit:
    def __init__(self, timestamp, duration, person, place):
        self.timestamp = timestamp
        self.duration = duration
        self.person = person
        self.place = place


class Simulator:
    def __init__(self):
        pass

    def _assign_places(self, n_places, population, mobility):
        for person in population:
            places_idxs = set()
            for _ in range(mobility):
                idx = random.randint(0, n_places - 1)
                places_idxs.add(idx)

            person.fav_places = places_idxs

    def _update_person(self, person, day, places, visits_of_day):
        if person.locked_down:
            # print("CANT MOVE")
            person.locked_down_counter -= 1
            if person.locked_down_counter == 0:
                # print("IM FREE")
                person.locked_down = False
                person.risk = LOW_RISK

        if person.infected:
            person.infected_counter -= 1
            if person.infected_counter == 0:
                person.infected = False
            return

        visited_places = person.places_to_visit()

        for p in visited_places:
            place = places[p]

            timestamp = Timestamp(
                day, random.randint(0, DAY), random.randint(0, HOUR)
            )  # TODO: review

            ed = place.estimatedVisitDuration

            duration = random.randint(ed - 5, ed + 5)

            visit = Visit(timestamp, duration, person, place)

            # print(f"CREATE VISIT at {place.id} hour: {timestamp.hour} minute: {timestamp.minute}")

            key = (place.id, timestamp.hour)

            if key not in visits_of_day:
                visits_of_day[key] = []

            visits_of_day[key].append(visit)

    def _apply_rules(self, visits, rules):
        for visits_by_hour in visits.values():
            if len(visits_by_hour) > 1:
                for visit_a, visit_b in itertools.combinations(visits_by_hour, 2):
                    shared = shared_time(visit_a, visit_b)

                    if not shared:
                        continue

                    # print(f"OVERLAP ON {visit_a.place.id} at A:[{visit_a.timestamp.minute};{visit_a.timestamp.minute + visit_a.duration}] B:[{visit_b.timestamp.minute};{visit_b.timestamp.minute + visit_b.duration}] SHARED {shared}")

                    risk = LOW_RISK
                    for rule in rules:
                        rule_applied = rule.apply(visit_a, visit_b, shared)

                        risk = risk if not rule_applied else max(rule_applied, risk)
                        if rule_applied:
                            break

                    visit_a.person.update_risk(risk)
                    visit_b.person.update_risk(risk)

    def _infect_population(self, population, init_infected):
        for person in population:
            proba = random.random()

            if proba < init_infected:
                person.infected = True

    def _daily_report(self, population, report, day):
        pop_low = 0
        pop_mid = 0
        pop_high = 0

        pop_infected = 0
        for person in population:
            if person.infected:
                pop_infected += 1
            if person.risk == LOW_RISK:
                pop_low += 1
            elif person.risk == MID_RISK:
                pop_mid += 1
            else:
                pop_high += 1

        return report.append(
            {
                "day": day,
                "high": pop_high,
                "mid": pop_mid,
                "low": pop_low,
                "infected": pop_infected,
            }
        )

    def run(
        self,
        n_pop=100,
        n_places=5,
        t=10,
        rules_info=[],
        mobility=FAV_PLACES,
        seed=None,
        init_infected=0.05,
    ):  # T is in days
        if seed:
            random.seed(seed)
        population = [Person() for p in range(n_pop)]
        places = [Place(pl) for pl in range(n_places)]
        rules = [Rule(info) for info in rules_info]
        self._assign_places(len(places), population, mobility)

        self._infect_population(population, init_infected)

        report = []
        for i in range(t):
            # print(f"DAY {i}")
            visits_of_day = {}
            for person in population:
                self._update_person(person, i, places, visits_of_day)

            self._apply_rules(visits_of_day, rules)
            self._daily_report(population, report, i)

        return report


"""
Visualizar:
----------

Pre simulacion:
Distribuciones de los establecimientos
Distribuciones de las personas

Post simulacion:
Avance de contagios en el tiempo
Avance de riesgos en el tiempo

nth:
poner a los establecimientos en un lugar
simular los puntitos moviendose y cambiando de colores



Posibles mejoras a la simulacion:
---------------------------------

- no todos tienen 5 lugares fav
- no todos los lugares tienen igual chance de ser visitados (hay lugares mas concurridos)
- proba de contagio variable segun el dia de la enfermedad
- usar https://scikit-mobility.github.io/scikit-mobility/reference/models.html#module-skmob.models.markov_diary_generator
"""
