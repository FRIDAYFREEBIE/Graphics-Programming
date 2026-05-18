import pygame

# draw line
def DrawLine(surface, x1, y1, x2, y2, color):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    stepX = 1 if x1 < x2 else -1
    stepY = 1 if y1 < y2 else -1

    error = dx - dy

    x = x1
    y = y1

    while True:
        surface.set_at((x, y), color)

        if x == x2 and y == y2:
            break

        e2 = 2 * error

        if e2 > -dy:
            error -= dy
            x += stepX

        if e2 < dx:
            error += dx
            y += stepY

# draw triangle outline
def DrawTriangle(surface, vertices, color):
    x1, y1 = vertices[0]
    x2, y2 = vertices[1]
    x3, y3 = vertices[2]

    DrawLine(surface, x1, y1, x2, y2, color)
    DrawLine(surface, x2, y2, x3, y3, color)
    DrawLine(surface, x3, y3, x1, y1, color)

# draw rectangle outline
def DrawRectangle(surface, vertices, color):
    x1, y1 = vertices[0]
    x2, y2 = vertices[1]
    x3, y3 = vertices[2]
    x4, y4 = vertices[3]

    DrawLine(surface, x1, y1, x2, y2, color)
    DrawLine(surface, x2, y2, x3, y3, color)
    DrawLine(surface, x3, y3, x4, y4, color)
    DrawLine(surface, x4, y4, x1, y1, color)

# fill triangle
def FillTriangle(surface, vertices, color):
    # sort vertices by y
    vertices.sort(key=lambda vertex: vertex[1])

    x1 = vertices[0][0]
    y1 = vertices[0][1]
    x2 = vertices[1][0]
    y2 = vertices[1][1]
    x3 = vertices[2][0]
    y3 = vertices[2][1]

    # interpolate x values between two points
    def Interpolate(yStart, xStart, yEnd, xEnd):

        if yStart == yEnd:
            return []

        xValues = []

        deltaX = (xEnd - xStart) / (yEnd - yStart)

        currentX = xStart

        y = yStart

        while y < yEnd:
            xValues.append(currentX)

            currentX += deltaX

            y += 1

        return xValues

    # create edge lists
    xShort = Interpolate(y1, x1, y2, x2)
    xShort += Interpolate(y2, x2, y3, x3)

    xLong = Interpolate(y1, x1, y3, x3)

    # get minimum length
    length = len(xShort)

    if len(xLong) < length:
        length = len(xLong)

    # fill triangle
    i = 0

    while i < length:

        y = y1 + i

        xa = int(xShort[i])
        xb = int(xLong[i])

        if xa > xb:
            temp = xa
            xa = xb
            xb = temp

        # draw horizontal line
        DrawLine(surface, xa, y, xb, y, color)

        # delay to visualization
        pygame.display.update()
        pygame.time.delay(15)

        i += 1

# fill rectangle using 2 triangles!
def FillRectangle(surface, vertices, color):
    # 0 = top left
    # 1 = top right
    # 2 = bottom right
    # 3 = bottom left

    triangle1 = [
        vertices[0],
        vertices[1],
        vertices[2]
    ]

    triangle2 = [
        vertices[0],
        vertices[2],
        vertices[3]
    ]

    FillTriangle(surface, triangle1, color)
    FillTriangle(surface, triangle2, color)

# pygame init
pygame.init()

screen = pygame.display.set_mode((800, 800))
pygame.display.set_caption("DRAW")

screen.fill((255, 255, 255))

# triangle vertex
triangle = [
    (50, 50),
    (300, 300),
    (50, 300)
]

# draw triangle outline
DrawTriangle(screen, triangle, (0, 0, 0))

# fill triangle inside
FillTriangle(screen, triangle, (0, 0, 255))

# rectangle vertex
rectangle = [
    (400, 400),
    (700, 400),
    (700, 600),
    (400, 600)
]

#draw rectangle outline
DrawRectangle(screen, rectangle, (0, 0, 0))

# fill rectangle inside
FillRectangle(screen, rectangle, (255, 0, 0))

pygame.display.flip()


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

# pygame quit
pygame.quit()