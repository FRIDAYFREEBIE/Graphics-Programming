import pygame
import time
import numpy as np
import math
from pygame.locals import *

WIDTH, HEIGHT = 800, 600
BG_COLOR = (220, 220, 220)

CAM_POS = np.array([150, 200, 300])
TARGET_POS = np.array([0, 0, 0])
UP = np.array([0, 1, 0])
FOV = 60


# Create camera view transformation matrix
def GetViewMatrix(CamPos, TargetPos, Up):
    ViewZ = TargetPos - CamPos
    ViewZ = ViewZ / np.linalg.norm(ViewZ)

    ViewX = np.cross(Up, ViewZ)
    ViewX = ViewX / np.linalg.norm(ViewX)

    ViewY = np.cross(ViewZ, ViewX)

    CamInv = np.array([
        [ViewX[0], ViewX[1], ViewX[2], -np.dot(ViewX, CamPos)],
        [ViewY[0], ViewY[1], ViewY[2], -np.dot(ViewY, CamPos)],
        [ViewZ[0], ViewZ[1], ViewZ[2], -np.dot(ViewZ, CamPos)],
        [0, 0, 0, 1]
    ])

    FlipY = np.array([
        [-1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, -1, 0],
        [0, 0, 0, 1]
    ])

    return np.matmul(FlipY, CamInv)


# Create perspective projection matrix
def GetProjectionMatrix(FovDeg, Width, Height, Near=0.1, Far=1000):
    Fov = math.radians(FovDeg)
    Aspect = Width / Height
    Distance = 1 / math.tan(Fov / 2)

    return np.array([
        [Distance / Aspect, 0, 0, 0],
        [0, Distance, 0, 0],
        [0, 0, (Near + Far) / (Near - Far), (2 * Near * Far) / (Near - Far)],
        [0, 0, -1, 0]
    ])


# Convert normalized device coordinates to screen coordinates
def GetViewportMatrix(Width, Height):
    return np.array([
        [Width / 2, 0, 0, Width / 2],
        [0, -Height / 2, 0, Height / 2],
        [0, 0, 0.5, 0.5],
        [0, 0, 0, 1]
    ])


# Determine whether a triangle is facing the camera
def IsFrontFace(V0, V1, V2):
    Edge1 = V1[:3] - V0[:3]
    Edge2 = V2[:3] - V0[:3]

    Normal = np.cross(Edge1, Edge2)

    Center = (V0[:3] + V1[:3] + V2[:3]) / 3

    # Camera is placed at the origin in view space
    ViewDirection = -Center

    # Visible when the face normal points toward the camera
    return np.dot(Normal, ViewDirection) > 0


# Transform and render a cube using backface culling
def DrawCube(Size, Position, Color, Screen, ViewMatrix, ProjectionMatrix, ViewportMatrix):
    Half = Size / 2

    Vertices = np.array([
        [-Half, -Half,  Half, 1],
        [ Half, -Half,  Half, 1],
        [ Half,  Half,  Half, 1],
        [-Half,  Half,  Half, 1],
        [-Half, -Half, -Half, 1],
        [ Half, -Half, -Half, 1],
        [ Half,  Half, -Half, 1],
        [-Half,  Half, -Half, 1]
    ])

    Faces = [
        [0, 1, 2], [2, 3, 0],
        [7, 6, 5], [5, 4, 7],
        [4, 5, 1], [1, 0, 4],
        [3, 2, 6], [6, 7, 3],
        [4, 0, 3], [3, 7, 4],
        [1, 5, 6], [6, 2, 1]
    ]

    Translate = np.array([
        [1, 0, 0, Position[0]],
        [0, 1, 0, Position[1]],
        [0, 0, 1, Position[2]],
        [0, 0, 0, 1]
    ])

    ViewVertices = []
    ProjectedVertices = []

    for Vertex in Vertices:
        # Local space -> World space
        WorldVertex = np.matmul(Translate, Vertex)

        # World space -> View space
        ViewVertex = np.matmul(ViewMatrix, WorldVertex)
        ViewVertices.append(ViewVertex)

        # View space -> Clip space
        ClipVertex = np.matmul(ProjectionMatrix, ViewVertex)

        # Perspective divide
        if ClipVertex[3] != 0:
            NdcVertex = ClipVertex / ClipVertex[3]
        else:
            NdcVertex = ClipVertex

        # NDC -> Screen space
        ScreenVertex = np.matmul(ViewportMatrix, NdcVertex)
        ProjectedVertices.append((int(ScreenVertex[0]), int(ScreenVertex[1]), ScreenVertex[2]))

    FaceDepths = []

    for Face in Faces:
        V0 = ViewVertices[Face[0]]
        V1 = ViewVertices[Face[1]]
        V2 = ViewVertices[Face[2]]

        # Skip triangles facing away from the camera
        if not IsFrontFace(V0, V1, V2):
            continue

        AvgDepth = sum(ProjectedVertices[Index][2] for Index in Face) / 3
        FaceDepths.append((AvgDepth, Face))

        FaceDepths.sort(key=lambda Item: Item[0], reverse=True)

        for _, Face in FaceDepths:
            Points = [
                (ProjectedVertices[Index][0],
                ProjectedVertices[Index][1])
                for Index in Face
            ]

            pygame.draw.polygon(Screen, Color, Points)
            pygame.draw.polygon(Screen, (0, 0, 0), Points, 2)

            # Update screen immediately
            pygame.display.flip()

            # Delay for recording
            time.sleep(0.15)


# Initialize Pygame
pygame.init()

Screen = pygame.display.set_mode((WIDTH, HEIGHT))
Clock = pygame.time.Clock()

# Build transformation matrices
ViewMatrix = GetViewMatrix(CAM_POS, TARGET_POS, UP)
ProjectionMatrix = GetProjectionMatrix(FOV, WIDTH, HEIGHT)
ViewportMatrix = GetViewportMatrix(WIDTH, HEIGHT)

# Main rendering loop
Running = True
while Running:
    for Event in pygame.event.get():
        if Event.type == QUIT:
            Running = False

    Screen.fill(BG_COLOR)

    DrawCube(100, (10, 10, 10), (0, 0, 255), Screen, ViewMatrix, ProjectionMatrix, ViewportMatrix)
    DrawCube(50, (-150, 150, -10), (0, 255, 0), Screen, ViewMatrix, ProjectionMatrix, ViewportMatrix)

    pygame.display.flip()
    Clock.tick(60)

pygame.quit()