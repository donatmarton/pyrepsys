# Reputation System – Small Python Simulation on ranking/reputation
'''
The players:
- Agent: agents/people that have a rank (0-9)

- Claim: any content by one of the agents that has a trueness and a stake
   - trueness (0-9): the real but unknown quality of the content
   - reviews[]: a list trueness estimate of other agents
   - stake (0-1): the confidence of the claiming agent

- Review: contains a Score for a Claim by one Agent
    - score (0-9): one trueness estimate for a claim
    - stake (0-1): the confidence of the reviewer

The node behaviors:
- Active/Lazy: active nodes publish more claims and rate more claims than lazy nodes
- Honest/Angry: honest nodes publish more true claims and rate more accuarately other claims than angry nodes
    => angry means a preference for more negative ratings and not directly a liar
- TrollSpammer: a node that always does the worst to mess with the system

Question: how can we derive accurate ratings of claims and nodes? 
'''

# imports
import random
from random import randint

# globals
CFG_RANK_INIT=10
CFG_NUM_NODES=20

CFG_RATE_MIN=0
CFG_RATE_MAX=9

CFG_HONEST_RATING=9  # max rating
CFG_ANGRY_RATING=5   # max rating


Score=int
def Rank(x):
    return round(max(min(x, CFG_RATE_MAX), CFG_RATE_MIN),1)

class System:
    def __init__(self):
        # todo: different init functions, e.g with nodeNum and percentages, or list of profiles
        self.nodes = [Node(x) for x in range(0,CFG_NUM_NODES)]
        self.evalAgent = rankAgentMean

        # create Attitudes
        honestAttitude = Attitude("Honest", claimTrue,   rateTrue)
        angryAttitude  = Attitude("Angry",  claimBiased, rateLow)
        softAttitude   = Attitude("Soft",   claimBiased, rateHigh)
        trollAttitude  = Attitude("Troll",  claimFalse,  rateWrong)

        # create nodes
        for node in self.nodes:

            halfnodes = len(self.nodes)//2
            if 0 <= node.myid < halfnodes:
                node.set_attitude(honestAttitude)
            else:
                node.set_attitude(angryAttitude)
            if halfnodes-2 <= node.myid < halfnodes + 2:
                node.set_engagement(ActiveEngagement())
            else:
                node.set_engagement(LazyEngagement())

            if node.myid == CFG_NUM_NODES-1:
                node.set_attitude(trollAttitude)
                node.set_engagement(SpamEngagement())


        self.claims = []

    def addClaim(self, claim):
        """ adds a claim to the globally published claims """
        self.claims.append(claim)

    def evalAll(self):
        self.evalAgent = rankAgentMean
        self.show()
        self.stats()
        self.evalAgent = rankAgentMedian
        self.stats()
        self.evalAgent = rankAgentWeighted
        self.stats()        

    def show(self):
        print("node (attitude)     | true rank revs claims <cTRUE-SCORES>")
        print("--------------------|------------------------------------")
        for node in self.nodes:
            print("{:<20}| {:>4} {:>4} {:>4} {:>2}".format(str(node), node.trueness(), self.evalAgent(node), node.numReviews(), str(node.myclaims)))

    def stats(self):
        trueness_avg = avg([n.trueness() for n in self.nodes])
        honest_rank = avg([self.evalAgent(n) for n in self.nodes if n.myatt.name == "Honest"])
        angry_rank = avg([self.evalAgent(n) for n in self.nodes if n.myatt.name == "Angry"])
        review_err = avg([n.trueness() - self.evalAgent(n) for n in self.nodes])
        print("Stats:")
        print("Avg. Trueness: {}".format(trueness_avg))
        print("Honest rank: {}".format(honest_rank))
        print("Angry  rank: {}".format(angry_rank))
        print("Review Error: {}  (trueness of claims - avg claim score)".format(review_err))



# Rating Functions for True Claim Rank (tcr)
# todo: maybe add previous reviews
# ------------------------------
def rateTrue(tcr): return Score(tcr)
def rateLow(tcr):  return Score(max(tcr-2, CFG_RATE_MIN))
def rateHigh(tcr): return Score(min(tcr+2, CFG_RATE_MAX))
def rateFlat(tcr): return Score(tcr+CFG_RATE_MAX/2)/2
def rateExtreme(tcr): return Score(tcr/2 + int(CFG_RATE_MAX/2<=tcr)*CFG_RATE_MAX/2)
def rateWrong(tcr): return Score(CFG_RATE_MAX - tcr)


# Claiming Functions
# ------------------------------
def claimTrue():   return randint(CFG_RATE_MAX-2,CFG_RATE_MAX)
def claimBiased(): return randint(CFG_RATE_MAX//2,CFG_RATE_MAX-2)
def claimFalse():  return randint(CFG_RATE_MIN,CFG_RATE_MIN+3)


# Direct Averages of Scoring
# ------------------------------
def avgMean(scores): 
    return sum(scores)/len(scores)

def avgMedian(scores): 
    scores.sort(); mid = len(scores) // 2
    return (scores[mid] + scores[~mid]) / 2


# Ranking Functions for Claims
# ------------------------------
def rankClaimMean(claim): 
    return avgMean([r.rating for r in claim.reviews]) if claim.reviews else CFG_RATE_MAX//2

def rankClaimMedian(claim):
    return avgMedian([r.rating for r in claim.reviews]) if claim.reviews else CFG_RATE_MAX//2


# Ranking Functions for Agents
# ------------------------------
def rankAgentMean(agent):
    return Rank(avgMean([rankClaimMean(c) for c in agent.myclaims]))

def rankAgentMedian(agent):
    return Rank(avgMedian([rankClaimMedian(c) for c in agent.myclaims]))

def rankAgentWeighted(agent):
    cranks = [rankClaimMean(c) for c in agent.myclaims]
    crevs = [len(c.reviews) for c in agent.myclaims]
    return Rank(avg(cranks, crevs))    


# Attitudes
# ------------------------------
class Attitude:
    def __init__(self, name, claimFun, rateFun, rateJit=1.5, claimJit=1.5):
        self.name = name
        self.claimfun = claimFun
        self.ratefun = rateFun
        self.claimJitter = claimJit
        self.rateJitter = rateJit

    def claim_trueness(self):
        return minmax(round(self.claimfun()+jitter(self.claimJitter)))

    def review_trueness(self, claim): 
        return minmax(round(self.ratefun(claim.trueness)+jitter(self.rateJitter)))

    def __str__(self): return self.name


# Engagement
# ------------------------------
class Engagement:
    def publish_num(self): raise NotImplementedError
    def review_num(self): raise NotImplementedError
    def __str__(self): return self.__class__.__name__[:-10]

class ActiveEngagement(Engagement):
    def publish_num(self): return randint(2,5)
    def review_num(self): return randint(5,10)

class LazyEngagement(Engagement):
    def publish_num(self): return randint(1,2)
    def review_num(self): return randint(3,6)

class SpamEngagement(Engagement):
    def publish_num(self): return randint(5,6)
    def review_num(self): return randint(15,20)



class Node:
    count = 0
    def __init__(self, myid=None):
        self.myid = myid if myid else Node.count
        Node.count += 1
        self.myrank = CFG_RATE_MAX//2
        self.mypeers = ()
        self.myclaims = []
        self.myreviews = []
        self.myatt = None
        self.myengagement = None
        self.scoreFun = None

    def set_attitude(self, attitude):
        self.myatt = attitude

    def set_engagement(self, engagement):
        self.myengagement = engagement

    def setScoreFun(self, scoreFun):
        self.scoreFun = scoreFun

    def publish(self):
        """ create a new claim. Its trueness depends on the agents attitude. """
        for idx in [0]*self.myengagement.publish_num():
            trueness = self.myatt.claim_trueness()
            claim = Claim(self.myid, trueness)
            self.myclaims.append(claim)
            g_sys.addClaim(claim)

    def assess(self, claims):
        """ create and add a review to one or more claims.  """
        if not isinstance(claims, list): claims = [claims] 

        # pick a subset of claims to rate
        num_reviews = min(self.myengagement.review_num(), len(claims))
        claims = random.sample(claims, num_reviews)

        for claim in claims:
            rating = self.myatt.review_trueness(claim) # get score from attitude
            review = Review(self.myid, rating)
            self.myreviews.append(review)
            claim.add_review(review)

    def trueness(self):
        """ returns the average of the actual own claims """
        return avg([c.trueness for c in self.myclaims])

    def numReviews(self):
        return len(self.myreviews)

    def __str__(self):
        return "N-{} ({},{})".format(self.myid, str(self.myengagement), str(self.myatt))



class Claim:
    count = 0

    def __init__(self, author, trueness):
        self.myid = Claim.count   # use index as ID
        Claim.count += 1
        self.fromnode = author
        self.trueness = trueness
        self.reviews = []

    def rank(self):
        if not self.reviews: 
            return CFG_RATE_MAX//2
        return avg([r.rating for r in self.reviews])

    def add_review(self, review):
        self.reviews.append(review)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "c{}-{}".format(self.trueness, "".join([str(x) for x in self.reviews]))



class Review:
    def __init__(self, myid, rating):
        self.fromid = myid
        self.rating = rating

    def __str__(self):
        return green(self.rating) if isHonest(self.fromid) else red(self.rating)



# Helper Functions
# -----------------------
def red(string):   return "\033[91m"+str(string)+"\033[0m"
def green(string): return "\033[32m"+str(string)+"\033[0m"
def bold(string):  return "\033[1m"+str(string)+"\033[0m"

def isHonest(nid):
    return g_sys.nodes[nid].myatt.name == "Honest"

def jitter(amplitude):
    return random.uniform(-1.0*amplitude, amplitude)

# weighted average
def avg(lst, weights = None):
    result = -1
    if lst == None or len(lst) == 0: return result
    if weights and sum(weights):
        result = round(sum([x*w for x, w in zip(lst, weights)])/(sum(weights)),2)   # division by zero
    else: 
        result = round(sum(lst)/len(lst),2)
    return result

# saturate rate
def minmax(x): return max(min(x, CFG_RATE_MAX), CFG_RATE_MIN)



# Main
# -----------------------
g_sys = System()

for node in g_sys.nodes:
    node.publish()

for node in g_sys.nodes:
    node.assess(g_sys.claims)

g_sys.evalAll()