# -*- coding: utf-8 -*-

"""
 The code containing the recomendations algorithm. This code is copied from
 'Programming Collective Intelligence first edition' by Toby Segaran Chapter 2.

"""
from __future__ import division
from math import sqrt
import pprint
# Returns the Pearson correlation coefficient for p1 and p2


def sim_pearson(prefs, p1, p2):

    print '--'
    # Get the list of mutually rated items
    si = {}
    for item in prefs[p1]:
        if item in prefs[p2]:
            print 'ok'
            si[item] = 1

    # if they are no ratings in common, return 0
    if len(si) == 0:
        print 'sheat'
        return 0
    print len(si)
    # Sum calculations
    n = len(si)

    # Sums of all the preferences
    sum1 = sum([prefs[p1][it] for it in si])
    sum2 = sum([prefs[p2][it] for it in si])
    print 'sum1',sum1
    print 'sum2',sum2
    
    # Sums of the squares
    sum1Sq = sum([pow(prefs[p1][it], 2) for it in si])
    sum2Sq = sum([pow(prefs[p2][it], 2) for it in si])
    print 'sum1Sq',sum1Sq
    print 'sum2Sq',sum2Sq
    # Sum of the products
    pSum = sum([prefs[p1][it]*prefs[p2][it] for it in si])
    print 'pSum',pSum
    # Calculate r (Pearson score)
    num = pSum-(sum1*sum2/n)
    den = sqrt((sum1Sq-pow(sum1, 2)/n)*(sum2Sq-pow(sum2, 2)/n))
    print num
    print den 
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
        print sim
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
    log = open('log', 'w')
    pprint.pprint(prefs,log)
    return rankings
