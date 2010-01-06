from __future__ import division
import DistanceMeasure
reload(DistanceMeasure)
from DistanceMeasure import sim_pearson as pearson, cosine_measure as cosine, cosine_measure_dense as cosine_dense
from math import sqrt, pow, fabs, floor
import random
from PIL import Image, ImageDraw
import time
import cPickle
import SearchTermDoc as STD
from scipy import sparse
from numpy import delete
import os
import IOmodule as IO

# Main folder
_mainFolder=os.getenv("HOME")+"/"+"The_Hive"
# Phase subfolder
_subFolder = _mainFolder+"/"+"term_doc"
# Term-doc directory
_termDocDir=_subFolder+"/"+"termDoc"
# Term- and PMID-hash directory
_hashTablesDir=_subFolder+"/"+"hashTables"
# Disease label hash
_labelHash="labelHash"

_stemmed=False

if not _stemmed:
    _outlierRemoved='new_diseaseMatrices_outlierRemoved'

else:
    _outlierRemoved='new_diseaseMatrices_outlierRemoved_stemmed'

outlierRemoved=_outlierRemoved

def scaledown(tdm, distance=pearson, rate=0.01, time_log=False):

    tiny_value = 0.999

    n = tdm.shape[0]

    tdm = tdm.todense()

    if time_log:
        t1 = time.time()

    print 'Calculating distance...'

    realdist = [[distance(tdm[i,1:], tdm[j,1:])
                 for j in range(0, n)]
                for i in range(0, n)]

    print
    print 'Distance calculations done.'

    if time_log:
        print 'Time for distance calculations:', time.time() - t1

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
                errorterm = (fakedist[j][k] - realdist[j][k]) / (realdist[j][k] + tiny_value)

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
        'Time for iterating: ', time.time() - t2

    return loc
    
def draw2d(data, labels, jpeg = 'mds_2d.jpeg', colors={}):

    # Initialize a empty picture with white background.
    img = Image.new('RGB', (2000, 2000), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    for i in range(len(data)):
        x = (data[i][0] + 0.5) * 1000
        y = (data[i][1] + 0.5) * 1000
        if colors == {}:
            draw.text((x, y), str(labels[i]), (0, 0, 0))
        else:
            draw.text((x, y), str(labels[i]), colors[str(labels[i])])
        #  ^ It could be really interesting to see colors on this plot
        #  accoring to how many diseases a pmid is on.
        
    img.save(jpeg, 'JPEG')

def drawdendrogram(clust, jpeg = 'disease_cluster_dendro.jpg', col={}, label={}, width = 1200, heightmodifier=20):

    """
    Recieves a cluster, filename, optional color dictionary, width of
    picture and a heightmodifier.

    Color dictionary contains: {'PMID_1' : (R, G, B) }
    Which is standard RGB color in a tuple.
    """

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
    drawnode(draw, clust, 10, (h / 2), scaling, col, label)
    img.save(jpeg,'JPEG')

# The labels needs to be the pmids
def drawnode(draw, clust, x, y, scaling, col={}, label={}):

    """
    Figures out where to put the nodes of the clusters.
    """

    if clust.id < 0:
        h1 = getheight(clust.left) * 20
        h2 = getheight(clust.right) * 20
        top = y - (h1 + h2) / 2
        bottom = y + (h1 + h2) / 2

        # Line length
        ll = fabs(clust.distance) * scaling
        #    ^ Necessary to because we might get a negative ll, which
        #      results in labels being placed wrong. This is a product
        #      of Pearson's correlation coeffiecient which ranges from
        #      -1.0 to 1.0, one could consider making "negative" lines
        #      another color to make sure of that fact.

        # Vertical line from this cluster to children
        draw.line((x, top + h1 / 2, x, bottom - h2 / 2), fill = (255, 0, 0))
        
        # Horizontal line to left item
        draw.line((x, top + h1 / 2, x + ll, top + h1 / 2), fill = (255, 0, 0))
        
        # ... right item
        draw.line((x, bottom - h2 / 2, x + ll, bottom - h2 / 2),
                  fill = (255, 0, 0))

        # Call the function to draw the left and right node
        drawnode(draw, clust.left, x + ll, top + h1 / 2, scaling, col, label)
        drawnode(draw, clust.right, x + ll, bottom - h2 / 2, scaling, col, label)
        
    else:
        # If it is an end point, draw the item label
        if col == {}:
            draw.text((x + 5, y - 7), label[clust.id], (0, 0, 0))
        else:
            draw.text((x + 5, y - 7), label[clust.id], col[str(clust.id)])
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
def hcluster(tdm, distance=pearson, output=False, time_log=False, time_total=False, print_remain=False):

    """
    Recieves an already cut matrix, that does not contain term
    hashes. Optionally a distance measuere, the default one being
    pearson's correlation coefficient, time_log for see what takes the
    time, print_remain to see how many clusters are left to merge.
    """

    distances = {}
    currentclustid = -1

    n = tdm.shape[0]

#    tdm = tdm.todense()

    print 'Start building clusters (clusters=' + str(n) + ')'

    # Time for clustering building
    if time_log or time_total:
        t1 = time.time()

    # We might consider using the real pmid for both label and id for
    # the cluster, when doing clustering on the sub term matrices. And
    # use the disease name when doing global.

    # Clusters are initially just the rows of the tdm / len(tdm.shape[0])
    clust=[bicluster(tdm.getrow(i)[0,1:], id = tdm.getrow(i)[0,0]) for i in range(0, n)]
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
        closest=distance(clust[0].vec, clust[1].vec, output=output, time_log=time_log)
        
        # Loop through every pair looking for the smallest distance
        for i in range(len(clust)):
            print 'Processing row', i
            if output:
                print 'Processing row', i
            for j in range(i + 1, len(clust)):
                # distances is the cache of distance calculations
                if (clust[i].id, clust[j].id) not in distances:
                    distances[(clust[i].id, clust[j].id)] = distance(clust[i].vec, clust[j].vec, output=output, time_log=time_log)

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

def cutMatrix(tdm, time_log=False):

    """
    Recieves a term document matrix, and returns a cut version of it,
    only having the dimensions required by the number of pmids and
    numbers of terms.

    Use time_total=True to record how much time is used on cutting the
    tdm into the right dimensions.
    """

    if time_log:
        t1 = time.time()
    
    # Figure out where to cut by looking for non zero entries.
    rowcut = max(tdm.nonzero()[0]) + 1
    colcut = max(tdm.nonzero()[1]) + 1

    # We do not want the term hash row, but we do want the pmid row.
    tdm = tdm[1:rowcut, 0:colcut]

    if time_log:
        print 'Time cutting matrix:', t1-time.time()

    return tdm

def getLabels(tdm):

    """
    Recieves a term docement matrix, and return a list with the hashed
    pmids, which can be used to reverse look up the real pmids later.
    """

    rows = max(tdm.nonzero()[0]) + 1

    labels = [int(e[0]) for e in tdm[:rows, 0].data.tolist()]

    return labels

def makeColorDictionary(pmidDuplicateList):

    '''
    Recieves a dictionary with pmid\'s and their count, then assigns
    colors to each of the pmids.
    '''

    colors = {}
    counter = 0

    for label in pmidDuplicateList:
        counter+=1
        if counter % 50000 == 0:
            print "Done with", counter
        if pmidDuplicateList[label] <= 10:
            colors[label] = (124,252,0)
        elif pmidDuplicateList[label] <= 50:
            colors[label] = (0,255,0)
        elif pmidDuplicateList[label] <= 100:
            colors[label] = (0,0,156)
        elif pmidDuplicateList[label] <= 200:
            colors[label] = (255,255,0)        
        elif pmidDuplicateList[label] <= 350:
            colors[label] = (255,127,0)
        elif pmidDuplicateList[label] <= 500:
            colors[label] = (255,0,0)

    return colors

def loadColors(filename=''):

    """
    For reading in a color dictionary
    """
    
    if filename == '':
        colors = cPickle.load('colorHash.col')
    else:
        colors = cPickle.load(filename)

    return colors

def runOutlierDetector(dir, distance=cosine_dense, removePercent=0.05, output=False, time_log=False):

    files = IO.getSortedFilelist(dir+'/')

    if output:
        counter = 0

    for f in files:
        diseaseName = f[0:f.find('.mtx')]
        subTermDoc = IO.readInTDM(dir, diseaseName)
        if output:
            counter += 1
            print 'Count:', counter

        # If sub term document matrix is empty, just skip it.
        if subTermDoc.shape[0]==1 or subTermDoc.shape[1]==1:
            continue

        if time_log:
            t1 = time.time()
        subTermDoc = outlierDetector(subTermDoc, distance, removePercent, output, time_log)
        if time_log:
            print 'Time for outlier detection on', diseaseName, ':', str(time.time() -t1)[:4]

        if output:
            print 'Writing',

        subTermDoc = sparse.coo_matrix(subTermDoc)

        IO.writeOutTDM(_subFolder+'/'+outlierRemoved+str(int(removePercent*100)), diseaseName, subTermDoc)

def outlierDetector(stdm, distance=cosine_dense, removePercent=0.05, output=False, time_log=False):

    """
    Recieves a coo matrix and calculates cosine similarity between all
    rows.

    distance=pearson will not work as it is not yet able to work on
    dense matrices
    """
    
    n = stdm.shape[0] - 1
    stdmdense = stdm.todense()
    stdmdense = stdmdense[1:,1:]

    distance_matrix = sparse.lil_matrix((n,n))

    if time_log:
        t1 = time.time()

    for i in range(0,n):
        for j in range(0,n):
            # As it is symmetric only calculate what is needed.
            if distance_matrix[i,j] == 0:
#                distance_matrix[i,j] = distance_matrix[j,i] = distance(stdm_csr.getrow(i), stdm_csr.getrow(j))
                distance_matrix[i,j] = distance_matrix[j,i] = distance(stdmdense[i,:], stdmdense[j,:])

    if time_log:
        print '\tTime for distance calculations', str(time.time() - t1)

    # We need to do the outlier detection down here, but we need some
    # clever way of doing it. Perhaps getting the average correlation
    # for each vector with the others, and then using a threshold to
    # remove those below.

    stdm = stdm.todense()

    distance_matrix = distance_matrix.todense()

    numberToRemove = int(floor(removePercent * n))

    if output:
        print '\tNumber of rows to remove', numberToRemove, 'out of', n

    if time_log:
        t2 = time.time()
    toBeDeleted=[]
    listOfThings=[]
    for i in range(0,n):
        listOfThings.append(((distance_matrix[i,:].sum() / n), i))

    listOfThings.sort()

    # As we have worked on a matrix missing first row and first
    # column, we need to add one to the row index to convert it back
    # to the original matrix.
    toBeDeleted = [int(item[1])+1 for item in listOfThings[:numberToRemove]]

    if output:
        print '\tList of row indices to be removed as outliers:', toBeDeleted

        
    stdm = delete(stdm, toBeDeleted, 0)

    if time_log:
        print '\tTime for finding and deleting outliers:', str(time.time() - t2)[:4]

    stdm = sparse.lil_matrix(stdm)
            
    return stdm

class bicluster:

    """
    A class represents the cluster.
    """
    
    def __init__(self, vec, left=None, right=None, distance=0.0, id=None):
        self.left = left
        self.right = right
        self.vec = vec
        self.id = int(id)
        self.distance = distance
