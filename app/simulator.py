import random
import itertools

'''
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
- Una persona va a por lo menos 5 lugares, (trabajo, supermercado, casa(nocuenta), y 3 comercios mas )
- Cada persona va a visitar esos 5 lugares ciclando por el T tiempo en el q transcurre la simulacion

SIMULACION:
- Creo N habitantes con caracteristicas random (con un % contagiado)
- Creo M espacios posiblides para visitar con caracteristicas random
- Creo Reglas pasadas por parametro
- Asigno 5 lugares a cada persona para visitar durante la simulacion
- Cada dia q pasa la persona va a 2/3 de los lugares para visitar, amenos q su mobilidad se vea reducida


'''

LOW_RISK,MID_RISK,HIGH_RISK = 2, 1, 0

FAV_PLACES = 5

LOCKDOWN_RESTRICTION = 7 # days

DAY = 24

HOUR = 60

def shared_time(a, b): # in minutes
    range_a = range(a.timestamp.minute, a.timestamp.minute + a.duration)
    range_b = range(b.timestamp.minute, b.timestamp.minute + b.duration)

    return len(set(range_a) & set(range_b))

class Rule:
    def __init__(self, params):
        for key, value in params:
            setattr(self, key, value)


class Person:
    def __init__(self):
        self.vacinated = random.randint(0,1)
        self.recovered = False

        self.infected = False
        self.locked_down = False
        self.locked_down_counter = 0
        self.fav_places = []
        self.risk = LOW_RISK

    def places_to_visit(self):
        n_places_to_visit = random.randint(0, self.risk)
        n_places = len(self.fav_places)
        places = []
        for _ in range(n_places_to_visit):
            idx = random.randint(1, n_places-1)

            places.append(idx)

        return places


class Place:
    def __init__(self, id):
        self.id = id
        self.openSpace = random.randint(0,1)
        self.n95mandatory = random.randint(0,1)
        self.m2 = random.randint(5, 100)
        self.estimatedVisitDuration = random.randint(5, 60) #min

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

    def _assign_places(self, n_places, population, n_favs=FAV_PLACES):
        for person in population:
            places_idxs = set()
            for _ in range(n_favs):
                idx = random.randint(0, n_places-1)
                places_idxs.add(idx)

            person.fav_places = places_idxs

        
    def _update_person(self, person, day, places, visits_of_day):
        if person.locked_down:
            person.locked_down_counter -= 1
            if person.locked_down_counter == 0:
                person.locked_down = False
            return
        
        visited_places = person.places_to_visit()

        for p in visited_places:
            place = places[p]

            timestamp = Timestamp(day, random.randint(0, DAY), random.randint(0, HOUR)) # TODO: review

            ed = place.estimatedVisitDuration

            duration = random.randint(ed - 5, ed + 5)

            visit = Visit(timestamp,  duration, person, place)

            print(f"CREATE VISIT at {place.id} hour: {timestamp.hour} minute: {timestamp.minute}")

            key = (place.id, timestamp.hour)

            if key not in visits_of_day:
                visits_of_day[key] = []

            visits_of_day[key].append(visit)


        
    def _apply_rules(self, visits, rules):
        for visits_by_hour in visits.values():
            if len(visits_by_hour) > 1:
                for visit_a, visit_b in itertools.combinations(visits_by_hour, 2):
                    st = shared_time(visit_a, visit_b)

                    if not st:
                        continue

                    print(f"OVERLAP ON {visit_a.place.id} at A:[{visit_a.timestamp.minute};{visit_a.timestamp.minute + visit_a.duration}] B:[{visit_b.timestamp.minute};{visit_b.timestamp.minute + visit_b.duration}] SHARED {st}")

                    # apply rules



    def _gather_results(self, population):
        pop_low = 0
        pop_mid = 0
        pop_high = 0
        for person in population:
            if person.risk == LOW_RISK:
                pop_low +=1
            elif person.risk == MID_RISK:
                pop_mid += 1
            else:
                pop_high +=1

        return {
            "high": pop_high,
            "mid": pop_mid,
            "low": pop_low
        }

    def run(self, n_pop=10, n_places=5, t=10, rules_info=[], seed=123): #T is in days
        random.seed(seed)
        print("INIT SIMULATION")
        population = [Person() for p in range(n_pop)]
        print("INIT POPULATION")
        places = [Place(pl) for pl in range(n_places)]
        print("INIT PLACES")
        rules = [Rule(info) for info in rules_info]
        print("INIT RULES")
        self._assign_places(len(places), population)
        print("ASSIGNED PLACES")
        for i in range(t):
            print(f"DAY {i}")
            visits_of_day = {}
            for person in population:
                self._update_person(person, i, places, visits_of_day)

            self._apply_rules(visits_of_day, rules)
                
        return self._gather_results(population)




sim = Simulator()

sim.run(rules_info=[])