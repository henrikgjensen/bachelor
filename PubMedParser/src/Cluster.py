import DistanceMeasure
reload(DistanceMeasure)
from DistanceMeasure import sim_pearson as pearson
from math import sqrt, pow, fabs
import random
from PIL import Image, ImageDraw
import time
from __future__ import division


def scaledown(tdm, distance=pearson, rate=0.01, time_log=False):

    tiny_value = 0.0001

    n = tdm.shape[0]

    # Are we able to save an if check if we just make the range run from range(1,n)
    if time_log:
        t1 = time.time()

    print 'Calculating distance...'

    realdist=[]

    for i in range(0,n):
        # Should be a slight optimazation
        row_i = tdm.getrow(i)[0,1:]
        for j in range(0,n):
            realdist.append(distance(row_i,tdm.getrow(j)[0,1:]))

#    realdist = [[distance(tdm.getrow(i)[0,1:], tdm.getrow(j)[0,1:])
#                 for j in range(0, n)]
#                for i in range(0, n)]

    print
    print 'Distance calculations done.'

    if time_log:
        print 'Time for distance calculations:', t1 - time.time()

    outersum = 0.0

    # We might be subject to getting off by one, due to the fact that
    # our real dist starts from range(1,n), and not from 0 as our
    # fakedist and loc. We might solve this by using range(1,n)
    # instead.
    loc = [[random.random(), random.random()] for i in range(0,n)]

    fakedist=[[0.0 for j in range(0,n)] for i in range(0,n)]

    if time_log:
        t2 = time.time()

    print 'Find projected distances and move around...'

    lasterror = None
    for m in range(0, 1500):
        # Find projected distance
        for i in range(0,n):
            for j in range(0,n):
                fakedist[i][j] = sqrt(sum([pow(loc[i][x] - loc[j][x], 2) for x in range(len(loc[i]))]))

        # Move the points around
        grad=[[0.0, 0.0] for i in range(0,n)]

        totalerror=0
        for k in range(0,n):
            for j in range(0,n):
                if j == k: continue
                # The error is percent difference between the
                # distances, plus a tiny value to avoid division by zero
                errorterm = (fakedist[j][k] - realdist[j][k]) / realdist[j][k] + tiny_value

                # Each point needs to be moved away from or towards the other
                # point in proportion to how much error it has
                grad[k][0]+=((loc[k][0] - loc[j][0]) / fakedist[j][k]) * errorterm
                grad[k][1]+=((loc[k][1] - loc[j][1]) / fakedist[j][k]) * errorterm
                
            # Keep track of the total error
                totalerror+=abs(errorterm)
                
        print totalerror, 
                
        # If the answer got worse by moving the points, we are done
        if lasterror and lasterror < totalerror: break
        lasterror = totalerror

        # Move each of the points by the learning rate times the gradient
        for k in range(n):
            loc[k][0] -= rate * grad[k][0]
            loc[k][1] -= rate * grad[k][1]

    print
    print 'Done finding projected distances and moving points around.'

    if time_log:
        'Time for iterating: ', t2 - time.time()

    return loc
    
def draw2d(data, labels, jpeg = 'mds_2d.jpeg'):

    # Initialize a empty picture with white background.
    img = Image.new('RGB', (2000, 2000), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    for i in range(len(data)):
        x = (data[i][0] + 0.5) * 1000
        y = (data[i][1] + 0.5) * 1000
        draw.text((x, y), str(labels[i]), (0, 0, 0))
        #  ^ It could be really interesting to see colors on this plot
        #  accoring to how many diseases a pmid is on.
        
    img.save(jpeg, 'JPEG')

def drawdendrogram(clust, jpeg = 'disease_cluster_dendro.jpg', width = 1200, heightmodifier=20):

    # height and width
    h = getheight(clust) * heightmodifier
    w = width
    #   ^ Consider making the drawing wider, we might have awefully much data.
    depth = getdepth(clust)

    # width is fixed so scale distances accordingly
    scaling = float(w - 500) / depth

    # Create a new image with a white background
    img = Image.new('RGB', (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    draw.line((0, h / 2, 10, h / 2), fill = (255, 0, 0))

    # Draw the first node
    drawnode(draw, clust, 10, (h / 2), scaling)
    img.save(jpeg,'JPEG')

# The labels needs to be the pmids
def drawnode(draw, clust, x, y, scaling):

    if clust.id < 0:
        h1 = getheight(clust.left) * 20
        h2 = getheight(clust.right) * 20
        top = y - (h1 + h2) / 2
        bottom = y + (h1 + h2) / 2

        # Line length
        ll = fabs(clust.distance) * scaling
        #    ^ Necessary to because we might get a negative ll, which
        #      results in labels being placed wrong.

        # Vertical line from this cluster to children
        draw.line((x, top + h1 / 2, x, bottom - h2 / 2), fill = (255, 0, 0))
        
        # Horizontal line to left item
        draw.line((x, top + h1 / 2, x + ll, top + h1 / 2), fill = (255, 0, 0))
        
        # ... right item
        draw.line((x, bottom - h2 / 2, x + ll, bottom - h2 / 2),
                  fill = (255, 0, 0))

        # Call the function to draw the left and right node
        drawnode(draw, clust.left, x + ll, top + h1 / 2, scaling)
        drawnode(draw, clust.right, x + ll, bottom - h2 / 2, scaling)
        
    else:
        # If it is an end point, draw the item label
        draw.text((x + 5, y - 7), str(clust.id), (0, 0, 0))
        #                          ^ Here!!!
        # We might want to get the real pmid label here, by a reverse
        # lookup or something like that, could be cool with a color
        # coding according to how many diseases the pmid occurs
        # in. Might help the visualization.

def getheight(clust):
    # Is this an end point
    if clust.left == None and clust.right == None: return 1

    # Otherwise the height is the same of the hieght of each branch
    return getheight(clust.left) + getheight(clust.right)

def getdepth(clust):
    # The distance of an end point is 0.0
    if clust.left == None and clust.right == None: return 0

    # The distance of a branch is the greater of its two sides plus
    # its own distance
    return max(getdepth(clust.left), getdepth(clust.right)) + clust.distance

# Need to send the tdm with, and extract all the rows. We don't use rows right now
def hcluster(tdm, distance=pearson, time_log=False, time_total=False, print_remain=False):
    distances = {}
    currentclustid = -1

    n = tdm.shape[0]

    print 'Start building clusters (clusters=' + str(n) + ')' 

    # Time for clustering building
    if time_log or time_total:
        t1 = time.time()

    # We might consider using the real pmid for both label and id for
    # the cluster, when doing clustering on the sub term matrices. And
    # use the disease name when doing global.

    # Clusters are initially just the rows of the tdm / len(tdm.shape[0])
    clust=[bicluster(tdm.getrow(i)[0,1:], id = int(tdm.getrow(i)[0,0])) for i in range(1, n)]
    #                               We had a tdm.getrow(i)[1:]
    #                               ^ This might take quite a while
    #                                 Consider alternative solution.

    print 'Done building', len(clust)+1, 'clusters.',
    
    if time_log:
        print 'Build time:', time.time() - t1,
        
    print
    print 'Starting distance calculations and merging of clusters...'
    
    if time_log:
        t2 = time.time()

    while len(clust)>1:
        if print_remain:
            print len(clust)-1,
        if time_log:
            t3 = time.time()

        lowestpair = (0, 1)
        closest=distance(clust[0].vec, clust[1].vec)
        
        # Loop through every pair looking for the smallest distance
        for i in range(len(clust)):
            for j in range(i + 1, len(clust)):
                # distances is the cache of distance calculations
                if (clust[i].id, clust[j].id) not in distances:
                    distances[(clust[i].id, clust[j].id)] = distance(clust[i].vec, clust[j].vec)

                d = distances[(clust[i].id, clust[j].id)]

                if d < closest:
                    closest = d
                    lowestpair = (i, j)

        # Calculate the average of the two clusters
        mergevec = (clust[lowestpair[0]].vec + clust[lowestpair[1]].vec) / 2.0

        # Create the new cluster
        newcluster = bicluster(mergevec, left = clust[lowestpair[0]],
                             right = clust[lowestpair[1]],
                             distance = closest, id = currentclustid)

        # cluster ids that was not in the original set is negative
        currentclustid -= 1
        del clust[lowestpair[1]]
        del clust[lowestpair[0]]
        clust.append(newcluster)

        if time_log:
            print 'Time taken:', time.time() - t3,
            print
    
    print 'Done calculating distance and merging clusters.'

    if time_log:
        t_e = time.time()
        print 'Time for clustering:', t_e - t2
        print 'Total time taken:', t_e - t1

    if time_total:
        t_e = time.time()
        print 'Total time taken:', t_e - t1

    return clust[0]

def cutMatrix(tdm, time_total=False):

    """
    cutMatrix(tdm, time_total=False)

    Recieves a term document matrix, and returns a cut version of it,
    only having the dimensions required by the number of pmids and
    numbers of terms.

    Use time_total=True to record how much time is used on cutting the
    tdm into the right dimensions.
    """

    if time_total:
        t1 = time.time()
    
    # Figure out where to cut by looking for non zero entries.
    rowcut = max(tdm.nonzero()[0]) + 1
    colcut = max(tdm.nonzero()[1]) + 1

    # We do not want the term hash row, but we do want the pmid row.
    tdm = tdm[1:rowcut, 0:colcut]

    if time_total:
        print 'Time cutting matrix:', t1-time.time()

    return tdm

def getLabels(tdm):

    rows = max(tdm.nonzero()[0]) + 1

    labels = [int(e[0]) for e in tdm[:rows, 0].data.tolist()]

    return labels

class bicluster:
    def __init__(self, vec, left=None, right=None, distance=0.0, id=None):
        self.left = left
        self.right = right
        self.vec = vec
        self.id = int(id)
        self.distance = distance
