from simulator import Simulator

sim = Simulator()

rules = [
    {
        "contagionRisk": 2,
        "durationValue": 20,
        "durationCmp": ">",
        "m2Value": None,
        "m2Cmp": None,
        "openSpace": None,
    },
    {
        "contagionRisk": 1,
        "m2Value": 20,
        "m2Cmp": "<",
        "durationValue": None,
        "durationCmp": None,
        "openSpace": None,
    },
]

restricted_rules = [
    {
        "contagionRisk": 2,
        "durationValue": 1,
        "durationCmp": ">",
        "m2Value": None,
        "m2Cmp": None,
        "openSpace": None,
    },
]

free_rules = [
    {
        "contagionRisk": 0,
        "durationValue": 1000,
        "durationCmp": ">",
        "m2Value": None,
        "m2Cmp": None,
        "openSpace": None,
    },
]

print(sim.run(rules_info=restricted_rules, t=5, n_pop=200, n_places=400))
