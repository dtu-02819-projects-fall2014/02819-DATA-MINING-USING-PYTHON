# -*- coding: utf-8 -*-

"""
 The code containing the recomendations algorithm. This code is copied from
 'Programming Collective Intelligence first edition' by Toby Segaran Chapter 2.

"""

from math import sqrt
import pprint
# Returns the Pearson correlation coefficient for p1 and p2


# Returns a distance-based similarity score for person1 and person2
def sim_distance(prefs,person1,person2):
    # Get the list of shared_items
    si={}
    for item in prefs[person1]:
        if item in prefs[person2]: si[item]=1
        # if they have no ratings in common, return 0
        if len(si)==0: return 0
        # Add up the squares of all the differences
        sum_of_squares=sum([pow(prefs[person1][item]-prefs[person2][item],2)
                            for item in prefs[person1] if item in prefs[person2]])
        return 1/(1+sum_of_squares)

def sim_pearson(prefs, p1, p2):

    # Get the list of mutually rated items
    si = {}
    for item in prefs[p1]:
        if item in prefs[p2]:
            si[item] = 1

    # if they are no ratings in common, return 0
    if len(si) == 0:
        return 0

    # Sum calculations
    n = len(si)

    # Sums of all the preferences
    sum1 = sum([prefs[p1][it] for it in si])
    sum2 = sum([prefs[p2][it] for it in si])
    
    # Sums of the squares
    sum1Sq = sum([pow(prefs[p1][it], 2) for it in si])
    sum2Sq = sum([pow(prefs[p2][it], 2) for it in si])

    # Sum of the products
    pSum = sum([prefs[p1][it]*prefs[p2][it] for it in si])
    # Calculate r (Pearson score)
    num = pSum-(sum1*sum2/n)
    den = sqrt((sum1Sq-pow(sum1, 2)/n)*(sum2Sq-pow(sum2, 2)/n))

    if den == 0:
        return 0
    
    r = num/den


    return r

# Gets recommendations for a person by using a weighted average
# of every other user's rankings


def getRecommendations(prefs, person, similarity=sim_pearson):

    totals = {}
    simSums = {}
    for other in prefs:

        if other == person:
            continue

        sim = similarity(prefs, person, other)
        if sim <= 0:
            continue

        for item in prefs[other]:

                # only score movies I haven't seen yet
            if item not in prefs[person] or prefs[person][item] == 0:
                # Similarity * Score
                totals.setdefault(item, 0)
                totals[item] += prefs[other][item]*sim
                # Sum of similarities
                simSums.setdefault(item, 0)
                simSums[item] += sim

    # Create the normalized list
    rankings = [(total/simSums[item], item) for item, total in totals.items()]

    # Return the sorted list
    rankings.sort()
    rankings.reverse()

    return rankings
