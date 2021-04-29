import random

import config as CFG

class Agent:
    count = 0
    def __init__(self):
        self.ID = Agent.count
        Agent.count += 1
        self.global_reputation = 5 # TODO: add default reputation
        self.claims = []
        self.rating_function = rating_function_1
        self.distort_function = distortion_fun_1

    def make_new_claim(self):
        ground_truth = random.randint(CFG.MIN_RATING, CFG.MAX_RATING)
        distorted_claim = self.__distort_ground_truth(ground_truth)
        claim = Claim(self.ID, ground_truth, distorted_claim)
        self.claims.append(claim)

    def rate_claim(self, claim):
        rating_value = self.rating_function(claim)
        rating = Rating(self.ID, rating_value)
        claim.add_rating(rating)

    def __distort_ground_truth(self, true_value):
        return self.distort_function(true_value)

    def print_claims_ratings(self):
        print("Agent #" + str(self.ID), end = ": ")
        if not self.claims:
            print("-")
        else:
            for claim in self.claims:
                print(claim)
    
        #return "c{}-{}".format(self.value, "".join([str(x) for x in self.ratings]))
        #"N-{} ({},{})".format(self.myid, str(self.myengagement), str(self.myatt))


def rating_function_1(claim):
    return min(claim.value + 1, CFG.MAX_RATING)

def distortion_fun_1(claim_value):
    return min(claim_value + 1, CFG.MAX_RATING)

class Claim:
    count = 0
    def __init__(self, author_ID, ground_truth, claim_value, stake=0):
        self.ID = Claim.count
        Claim.count += 1
        self.author_ID = author_ID
        self.ground_truth = ground_truth # TODO should be private or limited access something
        self.value = claim_value
        self.stake = stake
        self.ratings = []

    def add_rating(self,rating):
        self.ratings.append(rating)

    def __str__(self):
        return "c{}-{}".format(self.value, "".join([str(x) for x in self.ratings]))

class Rating:
    def __init__(self, author_ID, rating_value):
        self.author_ID = author_ID
        self.value = rating_value

    def __str__(self):
        return "{}".format(self.value)