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

LOW_RISK,MID_RISK,HIGH_RISK = 0, 1, 2

TOTAL_RISK = 2

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
        self.risk=params['contagionRisk']
        self.durationValue=params['durationValue']
        self.durationCmp=params['durationCmp']
        self.m2Value=params['m2Value']
        self.m2Cmp=params['m2Cmp']
        self.openSpace=params['openSpace']
        #self.n95Mandatory=params['n95Mandatory']
        #self.vaccinated=params['vaccinated']
        #self.vaccineReceived=params['vaccineReceived']
        #self.vaccinatedDaysAgoMin=params['vaccinatedDaysAgoMin']
        #self.illnessRecovered=params['illnessRecovered']
        #self.illnessRecoveredDaysAgoMax=params['illnessRecoveredDaysAgoMax']
        #for key, value in params:
        #    setattr(self, key, value)

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

        if check:
            return self.risk
		


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
        n_places_to_visit = random.randint(0, TOTAL_RISK - self.risk) # inverso al riesgo
        n_places = len(self.fav_places)
        places = []
        for _ in range(n_places_to_visit):
            idx = random.randint(1, n_places-1)

            places.append(idx)

        return places

    def update_risk(self, risk):
        self.risk = risk
        if risk == HIGH_RISK: # reduce mobility
            print("REDUCED MOBILITY")
            self.locked_down = True
            self.locked_down_counter = LOCKDOWN_RESTRICTION


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
            print("CANT MOVE")
            person.locked_down_counter -= 1
            if person.locked_down_counter == 0:
                print("IM FREE")
                person.locked_down = False
                person.risk = LOW_RISK
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
                    shared = shared_time(visit_a, visit_b)

                    if not shared:
                        continue

                    print(f"OVERLAP ON {visit_a.place.id} at A:[{visit_a.timestamp.minute};{visit_a.timestamp.minute + visit_a.duration}] B:[{visit_b.timestamp.minute};{visit_b.timestamp.minute + visit_b.duration}] SHARED {shared}")

                    risk = LOW_RISK
                    for rule in rules:
                        rule_applied = rule.apply(visit_a, visit_b, shared)
                        risk = risk if not rule_applied else max(rule_applied, risk)

                    visit_a.person.update_risk(risk)
                    visit_b.person.update_risk(risk)



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

    def run(self, n_pop=100, n_places=5, t=10, rules_info=[], seed=123): #T is in days
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

rules = [
    {
    "contagionRisk": 2,
    "durationValue": 20,
    "durationCmp": ">",
    "m2Value": None,
    "m2Cmp": None,
    "openSpace": None
    },
    {
    "contagionRisk": 1,
    "m2Value": 20,
    "m2Cmp": "<",
    "durationValue": None,
    "durationCmp": None,
    "openSpace": None
    },
]

print(sim.run(rules_info=rules, t=20, n_pop=200, n_places=100))