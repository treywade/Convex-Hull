# Convex hull


#
# Usage: python main.py [-d] file_of_points
#
# You can press ESC in the window to exit.
#
# You'll need Python 3 and must install these packages:
#
#   PyOpenGL, GLFW


import sys, os, math

try:  # PyOpenGL
    from OpenGL.GL import *
except:
    print('Error: PyOpenGL has not been installed.')
    sys.exit(0)

try:  # GLFW
    import glfw
except:
    print('Error: GLFW has not been installed.')
    sys.exit(0)

# Globals

window = None

windowWidth = 1000  # window dimensions
windowHeight = 1000

minX = None  # range of points
maxX = None
minY = None
maxY = None

r = 0.01  # point radius as fraction of window size

numAngles = 32
thetas = [i / float(numAngles) * 2 * 3.14159 for i in range(numAngles)]  # used for circle drawing

allPoints = []  # list of points

lastKey = None  # last key pressed

discardPoints = False


# Point
#
# A Point stores its coordinates and pointers to the two points beside
# it (CW and CCW) on its hull.  The CW and CCW pointers are None if
# the point is not on any hull.
#
# For debugging, you can set the 'highlight' flag of a point.  This
# will cause the point to be highlighted when it's drawn.

class Point(object):

    def __init__(self, coords):

        self.x = float(coords[0])  # coordinates
        self.y = float(coords[1])

        self.ccwPoint = None  # point CCW of this on hull
        self.cwPoint = None  # point CW of this on hull

        self.highlight = False  # to cause drawing to highlight this point

    def __repr__(self):
        return 'pt(%g,%g)' % (self.x, self.y)

    def drawPoint(self):

        # Highlight with yellow fill

        if self.highlight:
            glColor3f(0.9, 0.9, 0.4)
            glBegin(GL_POLYGON)
            for theta in thetas:
                glVertex2f(self.x + r * math.cos(theta), self.y + r * math.sin(theta))
            glEnd()

        # Outline the point

        glColor3f(0, 0, 0)
        glBegin(GL_LINE_LOOP)
        for theta in thetas:
            glVertex2f(self.x + r * math.cos(theta), self.y + r * math.sin(theta))
        glEnd()

        # Draw edges to next CCW and CW points.

        if self.ccwPoint:
            glColor3f(0, 0, 1)
            drawArrow(self.x, self.y, self.ccwPoint.x, self.ccwPoint.y)

        if self.ccwPoint:
            glColor3f(1, 0, 0)
            drawArrow(self.x, self.y, self.cwPoint.x, self.cwPoint.y)


# Draw an arrow between two points, offset a bit to the right

def drawArrow(x0, y0, x1, y1):
    d = math.sqrt((x1 - x0) * (x1 - x0) + (y1 - y0) * (y1 - y0))

    vx = (x1 - x0) / d  # unit direction (x0,y0) -> (x1,y1)
    vy = (y1 - y0) / d

    vpx = -vy  # unit direction perpendicular to (vx,vy)
    vpy = vx

    xa = x0 + 1.5 * r * vx - 0.4 * r * vpx  # arrow tail
    ya = y0 + 1.5 * r * vy - 0.4 * r * vpy

    xb = x1 - 1.5 * r * vx - 0.4 * r * vpx  # arrow head
    yb = y1 - 1.5 * r * vy - 0.4 * r * vpy

    xc = xb - 2 * r * vx + 0.5 * r * vpx  # arrow outside left
    yc = yb - 2 * r * vy + 0.5 * r * vpy

    xd = xb - 2 * r * vx - 0.5 * r * vpx  # arrow outside right
    yd = yb - 2 * r * vy - 0.5 * r * vpy

    glBegin(GL_LINES)
    glVertex2f(xa, ya)
    glVertex2f(xb, yb)
    glEnd()

    glBegin(GL_POLYGON)
    glVertex2f(xb, yb)
    glVertex2f(xc, yc)
    glVertex2f(xd, yd)
    glEnd()


# Determine whether three points make a left or right turn

LEFT_TURN = 1
RIGHT_TURN = 2
COLLINEAR = 3


def turn(a, b, c):
    det = (a.x - c.x) * (b.y - c.y) - (b.x - c.x) * (a.y - c.y)

    if det > 0:
        return LEFT_TURN
    elif det < 0:
        return RIGHT_TURN
    else:
        return COLLINEAR


# Build a convex hull from a set of point
#
# Use the method described in class


def buildHull(points):
    if len(points) == 2:  # If function was only called with two points

        points[1].ccwPoint = points[0]
        points[1].cwPoint = points[0]
        points[0].ccwPoint = points[1]
        points[0].cwPoint = points[1]


    elif len(points) == 3:  # If function was only called with three points

        if turn(points[0], points[1], points[2]) == 1: # if turn of three points in order results in left turn
            points[2].ccwPoint = points[0]
            points[2].cwPoint = points[1]

            points[0].cwPoint = points[2]
            points[0].ccwPoint = points[1]

            points[1].cwPoint = points[0]
            points[1].ccwPoint = points[2]



        elif turn(points[0], points[1], points[2]) == 2: #if turn of three points in order results in right turn

            points[2].cwPoint = points[0]
            points[2].ccwPoint = points[1]

            points[0].cwPoint = points[1]
            points[0].ccwPoint = points[2]

            points[1].ccwPoint = points[0]
            points[1].cwPoint = points[2]



        else: # if neither, three points are colinear

            points[0].cwPoint = points[1]
            points[0].ccwPoint = points[1]

            points[1].cwPoint = points[2]
            points[1].ccwPoint = points[0]

            points[2].ccwPoint = points[1]
            points[2].cwPoint = points[1]
    else:
        l1 = None  # These will store index references to the top and bottom most points of both hulls for merging them together
        r1 = None
        l2 = None
        r2 = None

        Arr1 = points[:(int(len(points) / 2))]  # Place left section of list passed into BuildHull into Arr1
        buildHull(Arr1)  # Call buildhull with new smaller list
        Arr2 = points[int(len(points) / 2):]
        buildHull(Arr2)
        Arr3 = []  # Here we will store all the points we want to delete during walk up and walk down
        r = Arr2[0]  # since lists are sorted, first point of right list is leftmost point
        l = Arr1[-1]  # since lists are sort, last point of left list is rightmost point

        if ((len(Arr1) + len(Arr2)) > 3):
            Arr3.append(l)
            Arr3.append(r)

        while (turn(l.ccwPoint, l, r) == 1 or turn(l, r, r.cwPoint) == 1):  # walking up both lists

            if (turn(l.ccwPoint, l, r) == 1):# if left's ccw, left and right points make a left turn, walkup the left list
                l = l.ccwPoint
                if ((len(Arr1) + len(
                        Arr2)) > 3):  # only add points for deletion if the length of both lists is larger than 3
                    Arr3.append(l)
            else:  #this is an else instead of elif to address the case of a colinear return from turn
                r = r.cwPoint
                if ((len(Arr1) + len(Arr2)) > 3):
                    Arr3.append(r)

        if l in Arr3: # remove the edge cases
            Arr3.remove(l)
        if r in Arr3:
            Arr3.remove(r)

        for x in range(0, len(Arr2)):# find what index of the right list matches with the highest right point
            if (r.x == Arr2[x].x and r.y == Arr2[x].y):
                r1 = x

        for i in range(0, len(Arr1)):#Find what index of the left list matches with the highest left point
            if (l.x == Arr1[i].x and l.y == Arr1[i].y):
                l1 = i

        r = Arr2[0] #Set R and L markers to the center of both lists before walkdown procedure
        l = Arr1[-1]
        while ((turn(l.cwPoint, l, r) != 1) or (turn(r.ccwPoint, r, l) != 2)): #same as walkup,
            if turn(l.cwPoint, l, r) == 2: # if clockwise of left , left and right make a right turn, walk down left side
                l = l.cwPoint
                if ((len(Arr1) + len(Arr2)) > 3):# append values as we walkup to list to be later deleted
                    Arr3.append(l)
            else:
                r = r.ccwPoint
                if ((len(Arr1) + len(Arr2)) > 3):
                    Arr3.append(r)

        if l in Arr3:#remove edge cases
            Arr3.remove(l)
        if r in Arr3:
            Arr3.remove(r)

        for x in range(0, len(Arr2)):
            if (r.x == Arr2[x].x and r.y == Arr2[x].y):
                r2 = x
        for i in range(0, len(Arr1)):
            if (l.x == Arr1[i].x and l.y == Arr1[i].y):
                l2 = i

        Arr2[r2].cwPoint = Arr1[l2]# join up lists using indecies found in for loops, in this case start by pointing clockwise of bottom right list to bottom or left list
        Arr1[l1].cwPoint = Arr2[r1]
        Arr1[l2].ccwPoint = Arr2[r2]
        Arr2[r1].ccwPoint = Arr1[l1]
        for x in range(0, len(Arr3)): #this is the deletion, iterate through the list that was appended to, and set all pointers to None
            Arr3[x].cwPoint = None
            Arr3[x].ccwPoint = None

    for p in points:
        p.highlight = True
        # display(wait=True)

    display()


windowLeft = None
windowRight = None
windowTop = None
windowBottom = None


# Set up the display and draw the current image

def display(wait=False):
    global lastKey, windowLeft, windowRight, windowBottom, windowTop

    # Handle any events that have occurred

    glfw.poll_events()

    # Set up window

    glClearColor(1, 1, 1, 0)
    glClear(GL_COLOR_BUFFER_BIT)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if maxX - minX > maxY - minY:  # wider point spread in x direction
        windowLeft = -0.1 * (maxX - minX) + minX
        windowRight = 1.1 * (maxX - minX) + minX
        windowBottom = windowLeft
        windowTop = windowRight
    else:  # wider point spread in y direction
        windowTop = -0.1 * (maxY - minY) + minY
        windowBottom = 1.1 * (maxY - minY) + minY
        windowLeft = windowBottom
        windowRight = windowTop

    glOrtho(windowLeft, windowRight, windowBottom, windowTop, 0, 1)

    # Draw points and hull

    for p in allPoints:
        p.drawPoint()

    # Show window

    glfw.swap_buffers(window)

    # Maybe wait until the user presses 'p' to proceed

    if wait:

        sys.stderr.write('Press "p" to proceed ')
        sys.stderr.flush()

        lastKey = None
        while lastKey != 80:  # wait for 'p'
            glfw.wait_events()
            display()

        sys.stderr.write('\r                     \r')
        sys.stderr.flush()


# Handle keyboard input

def keyCallback(window, key, scancode, action, mods):
    global lastKey

    if action == glfw.PRESS:

        if key == glfw.KEY_ESCAPE:  # quit upon ESC
            sys.exit(0)
        else:
            lastKey = key


# Handle window reshape


def windowReshapeCallback(window, newWidth, newHeight):
    global windowWidth, windowHeight

    windowWidth = newWidth
    windowHeight = newHeight


# Handle mouse click/release

def mouseButtonCallback(window, btn, action, keyModifiers):
    if action == glfw.PRESS:

        # Find point under mouse

        x, y = glfw.get_cursor_pos(window)  # mouse position

        wx = (x - 0) / float(windowWidth) * (windowRight - windowLeft) + windowLeft
        wy = (windowHeight - y) / float(windowHeight) * (windowTop - windowBottom) + windowBottom

        minDist = windowRight - windowLeft
        minPoint = None
        for p in allPoints:
            dist = math.sqrt((p.x - wx) * (p.x - wx) + (p.y - wy) * (p.y - wy))
            if dist < r and dist < minDist:
                minDist = dist
                minPoint = p

        # print point and toggle its highlight

        if minPoint:
            minPoint.highlight = not minPoint.highlight
            print(minPoint)


# Initialize GLFW and run the main event loop

def main():
    global window, allPoints, minX, maxX, minY, maxY, r, discardPoints

    # Check command-line args

    if len(sys.argv) < 2:
        print('Usage: %s points1.txt' % sys.argv[0])
        sys.exit(1)

    args = sys.argv[1:]
    while len(args) > 1:
        print(args)
        if args[0] == '-d':
            discardPoints = not discardPoints
        args = args[1:]

    # Set up window

    if not glfw.init():
        print('Error: GLFW failed to initialize')
        sys.exit(1)

    window = glfw.create_window(windowWidth, windowHeight, "Assignment 1", None, None)

    if not window:
        glfw.terminate()
        print('Error: GLFW failed to create a window')
        sys.exit(1)

    glfw.make_context_current(window)
    glfw.swap_interval(1)
    glfw.set_key_callback(window, keyCallback)
    glfw.set_window_size_callback(window, windowReshapeCallback)
    glfw.set_mouse_button_callback(window, mouseButtonCallback)

    # Read the points

    with open(args[0], 'rb') as f:
        allPoints = [Point(line.split(b' ')) for line in f.readlines()]

    # Get bounding box of points

    minX = min(p.x for p in allPoints)
    maxX = max(p.x for p in allPoints)
    minY = min(p.y for p in allPoints)
    maxY = max(p.y for p in allPoints)

    # Adjust point radius in proportion to bounding box

    if maxX - minX > maxY - minY:
        r *= maxX - minX
    else:
        r *= maxY - minY

    # Sort by increasing x.  For equal x, sort by increasing y.

    allPoints.sort(key=lambda p: (p.x, p.y))

    # Run the code

    buildHull(allPoints)

    # Wait to exit

    while not glfw.window_should_close(window):
        glfw.wait_events()

    glfw.destroy_window(window)
    glfw.terminate()


if __name__ == '__main__':
    main()