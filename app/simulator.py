import random
import itertools
import math
import numpy as np

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
Medio: movilidad reducida a la mitad de la frecuenca
Bajo: visita la totalidad de la frecuencia configurada


ASUMO:

- En una pandemia el movimiento es reducido pero existe
- Una persona va a por lo menos F lugares, (trabajo, supermercado, casa(nocuenta), farmacia, etc )
- Cada persona va a visitar esos F lugares ciclando por el T tiempo en el q transcurre la simulacion

SIMULACION:
- Creo N habitantes con caracteristicas random (con un % contagiado)
- Creo M espacios posiblides para visitar con caracteristicas random
- Creo Reglas pasadas por parametro
- Asigno F lugares a cada persona para visitar durante la simulacion
- Cada dia q pasa la persona va a los configurados lugares para visitar, amenos q su mobilidad se vea reducida
- Defino probabilidades de contagio segun los riesgos de la regla
- Config un tiempo de contagio que tiene un contagiado (por cuantos dias es contagioso)
- Config tiempo de incubacion
- Config por cuanto tiempo se encierra el riesgo alto

"""

LOW_RISK, MID_RISK, HIGH_RISK = 0, 1, 2

TOTAL_RISK = 2

FAV_PLACES = 5

LOCKDOWN_RESTRICTION = 7  # days

INFECTED_WINDOW = 5  # days

DAY = 24

HOUR = 60

RISKS_TO_NUMBER = {"low": 0, "mid": 1, "high": 2}
NUMBER_TO_RISK = ["low", "mid", "high"]

INFECTED_PROBABILITIES = {"low": 0.001, "mid": 0.05, "high": 0.5}

PARTIAL_VACCINATED, FULL_VACCINATED = 1, 2

MOBILITY = {"fequency": 5, "variability": 5}

INCUBATION_PERIOD = 3

DEFAULT_PROBABILITY = 0.5 # tose a coin


def shared_time(a, b):  # in minutes
    range_a = range(a.timestamp.minute, a.timestamp.minute + a.duration)
    range_b = range(b.timestamp.minute, b.timestamp.minute + b.duration)

    return len(set(range_a) & set(range_b))

def random_boolean():
    return random.choice([True, False])


class Rule:
    def __init__(self, params):
        self._parse_field("contagionRisk", params)
        self._parse_field("durationValue", params, parse=True)
        self._parse_field("durationCmp", params)
        self._parse_field("m2Value", params, parse=True)
        self._parse_field("m2Cmp", params)
        self._parse_field("openSpace", params)
        self._parse_field("vaccinated", params, parse=True)

    def _parse_field(self, field, info, parse=False):
        value = info[field] if field in info else None
        setattr(self, field, int(value) if parse and value else value)

    def apply(self, visit_a, visit_b, shared):
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

        if self.vaccinated != None:
            if visit_a.person.infected:
                check &= visit_b.person.vaccinated == self.vaccinated

            if visit_b.person.infected:
                check &= visit_a.person.vaccinated == self.vaccinated

        return check, self.contagionRisk


class Person:
    def __init__(self, id, lockdown_restriction, probabilites, visits_frequency, infected_days, incubation_period):
        self.id = id
        self.recovered = False

        self.infected = False
        self.infected_counter = 0
        self.locked_down = False
        self.locked_down_counter = 0
        self.fav_places = []
        self.lockdown_restriction = lockdown_restriction
        self.probabilities = probabilites
        self.visits_frequency = visits_frequency
        self.infected_days = infected_days
        self.vaccinated = 0
        self.risk = LOW_RISK
        self.incubation_period = incubation_period
        self.incubating = False
        self.incubating_counter = 0
        self.restricted = False

    def __str__(self):
        return f"Person {self.id} | infected {self.infected} | incubating {self.incubating} | risk {self.risk} | vaccinated {self.vaccinated}"

    def places_to_visit(self):

        n_places = len(self.fav_places)

        n_places_to_visit = random.randint(
            0, math.floor(self.visits_frequency * (TOTAL_RISK - self.risk) / TOTAL_RISK)
        )  # inverso al riesgo

        places = []
        for _ in range(n_places_to_visit):
            idx = random.randint(0, n_places - 1)

            places.append(idx)

        return places

    def get_infected(self, now=False):
        if now:
            self.incubating = False
            self.incubating_counter = 0
            self.infected = True
            self.infected_counter = self.infected_days
        else:
            self.incubating = True
            self.incubating_counter = self.incubation_period

    def get_cured(self):
        self.infected = False
        self.infected_counter = 0

    def update_risk(self, risk):
        
        if risk == HIGH_RISK and self.risk != risk:  # reduce mobility
            self.locked_down = True
            self.locked_down_counter = self.lockdown_restriction

        elif risk == MID_RISK and self.risk != risk:
            self.restricted = True
            self.locked_down_counter = self.lockdown_restriction

        self.risk = risk

        #self.expose_to_virus()#p=self.probabilities[NUMBER_TO_RISK[self.risk]])

    def expose_to_virus(self, p=DEFAULT_PROBABILITY):
        proba_infected = random.random()

        if (
            not self.incubating
            and not self.infected
            and proba_infected < p
        ):
            self.get_infected()


class Place:
    def __init__(self, id):
        self.id = id
        self.openSpace = random_boolean()
        self.n95mandatory = random_boolean()
        self.m2 = random.randint(5, 100)
        self.estimatedVisitDuration = random.randint(5, 60)  # min

    def __str__(self):
        return f"Place {self.id} | openSpace {self.openSpace} | m2 {self.m2} | estimatedVisitDuration {self.estimatedVisitDuration}"


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

    def __str__(self) -> str:
        return f"{str(self.place)} || {str(self.person)} || {self.duration}"

class Simulator:
    def __init__(self):
        pass

    def _assign_places(self, n_places, population):
        for person in population:
            places_idxs = set()
            while len(places_idxs) < self.variability:
                idx = random.randint(0, n_places - 1)
                places_idxs.add(idx)

            person.fav_places = places_idxs

    def _update_person(self, person, day, places, visits_of_day):
        if person.incubating:
            person.incubating_counter -= 1
            if person.incubating_counter < 0:
                person.get_infected(now=True)
        elif person.infected:
            person.infected_counter -= 1
            if person.infected_counter <= 0:
                person.get_cured()

        if person.locked_down:
            person.locked_down_counter -= 1
            if person.locked_down_counter == 0:
                person.locked_down = False
                person.restricted = False
                person.risk = LOW_RISK
            return

        elif person.restricted:
            person.locked_down_counter -= 1
            if person.locked_down_counter == 0:
                person.restricted = False
                person.risk = LOW_RISK

        visited_places = person.places_to_visit()

        for p in visited_places:
            place = places[p]

            timestamp = Timestamp(
                day, random.randint(0, DAY), random.randint(0, HOUR)
            )  # TODO: review

            ed = place.estimatedVisitDuration

            duration = random.randint(ed - 5, ed + 5)

            visit = Visit(timestamp, duration, person, place)

            key = (place.id, timestamp.hour)

            if key not in visits_of_day:
                visits_of_day[key] = []

            visits_of_day[key].append(visit)


    def spread_virus(self, place, shared, person_a, person_b):
        p = 0.001 # small chance 
        if place.openSpace == False:
            p += 0.1

        p += 0.1 - (0.1/100) * place.m2

        p += (0.1/HOUR) * shared

        if person_a.vaccinated < 2:
            p += 0.025 if person_a.vaccinated == 1 else 0.05
        else: # being full vaccinated decreases chances
            p -= 0.025

        if person_b.vaccinated < 2:
            p += 0.025 if person_b.vaccinated == 1 else 0.05
        else: # being full vaccinated decreases chances
            p -= 0.025

        person_a.expose_to_virus(p=p)
        person_b.expose_to_virus(p=p)

        


    def _apply_rules(self, visits, rules):
        for key, visits_by_hour in visits.items():
            if len(visits_by_hour) > 1:
                for visit_a, visit_b in itertools.combinations(visits_by_hour, 2):
                    shared = shared_time(visit_a, visit_b)

                    if not shared:
                        continue

                    infected = visit_a.person.infected or visit_b.person.infected

                    if not infected:
                        continue

                    #print(f"OVERLAP ON {visit_a.place.id} at A:[{visit_a.timestamp.minute};{visit_a.timestamp.minute + visit_a.duration}] B:[{visit_b.timestamp.minute};{visit_b.timestamp.minute + visit_b.duration}] SHARED {shared}")

                    risk = LOW_RISK
                    should_update = False
                    for rule in rules:
                        rule_applied, new_risk = rule.apply(visit_a, visit_b, shared)
                        should_update |= rule_applied

                        risk = risk if not rule_applied else max(new_risk, risk)
                        if rule_applied:
                            break

                    if should_update:
                        #print(f"HUBO CONTAGIO EN {visit_a.place.id} {visit_b.place.id}")
                        visit_a.person.update_risk(risk)
                        visit_b.person.update_risk(risk)
                    #else:
                    #    print(visit_a)
                    #    print(visit_b)
                    #    print(shared)
                    #visit_a.person.expose_to_virus()
                    #visit_b.person.expose_to_virus()

                    self.spread_virus(visit_a.place, shared, visit_a.person, visit_b.person)


    def _infect_population(self, population, init_infected):
        for person in population:
            proba = random.random()

            if proba < init_infected:
                person.get_infected(now=True)

    def _vaccinate_population(self, population, vaccine, p_vaccine):
        for person in population:
            proba = random.random()

            if proba < p_vaccine:
                person.vaccinated = vaccine

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

    def _places_statistics(self, places):
        stats = {
            "m2": [],
            "openSpace": [],
            "estimatedVisitDuration": []
        }
        for place in places:
            for char in stats.keys():
                stats[char].append(getattr(place, char))

        for char, values in stats.items():
            unique_elements, counts_elements = np.unique(values, return_counts=True)


    def run(
        self,
        n_pop=100,
        n_places=5,
        t=10, #days
        rules_info=[],
        mobility=MOBILITY,
        seed=None,
        init_infected=0.05,
        infected_days=INFECTED_WINDOW,
        lockdown_restriction=LOCKDOWN_RESTRICTION,
        probabilities=INFECTED_PROBABILITIES,
        partially_vaccinated=0,
        fully_vaccinated=0,
        incubation_period=INCUBATION_PERIOD
    ):
        if seed:
            random.seed(seed)

        visits_frequency = mobility["frequency"]
        population = [
            Person(p, lockdown_restriction, probabilities, visits_frequency, infected_days, incubation_period)
            for p in range(n_pop)
        ]
        places = [Place(pl) for pl in range(n_places)]
        rules = [Rule(info) for info in rules_info]

        self.variability = mobility["variability"]
        self._assign_places(len(places), population)

        self._infect_population(population, init_infected)
        self._vaccinate_population(population, FULL_VACCINATED, fully_vaccinated)
        self._vaccinate_population(population, PARTIAL_VACCINATED, partially_vaccinated)

        report = []
        for i in range(t):
            #print(f"DAY {i}")
            visits_of_day = {}
            for p, person in enumerate(population):
                # print("person day", p, i)
                self._update_person(person, i, places, visits_of_day)

            self._apply_rules(visits_of_day, rules)
            self._daily_report(population, report, i)

        #self._population_statistics()
        #self._places_statistics(places)

        return report


"""
Visualizar:
----------

Pre simulacion:
Distribuciones de los establecimientos
Distribuciones de las personas


agregar distribucion de establecimientos

Posibles mejoras a la simulacion:
---------------------------------

- no todos los lugares tienen igual chance de ser visitados (hay lugares mas concurridos)
- proba de contagio variable segun el dia de la enfermedad
- usar https://scikit-mobility.github.io/scikit-mobility/reference/models.html#module-skmob.models.markov_diary_generator


"""
