import pygame
import numpy as np
import math
from pygame.locals import *

WIDTH, HEIGHT = 800, 600
BG_COLOR = (220, 220, 220)

CAM_POS = np.array([150, 200, 300])
TARGET_POS = np.array([0, 0, 0])
UP = np.array([0, 1, 0])
FOV = 60


def get_view_matrix(cam_pos, target_pos, up):
    view_z = target_pos - cam_pos
    view_z = view_z / np.linalg.norm(view_z)

    view_x = np.cross(up, view_z)
    view_x = view_x / np.linalg.norm(view_x)

    view_y = np.cross(view_z, view_x)

    cam_inv = np.array([
        [view_x[0], view_x[1], view_x[2], -np.dot(view_x, cam_pos)],
        [view_y[0], view_y[1], view_y[2], -np.dot(view_y, cam_pos)],
        [view_z[0], view_z[1], view_z[2], -np.dot(view_z, cam_pos)],
        [0, 0, 0, 1]
    ])

    flip_y = np.array([
        [-1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, -1, 0],
        [0, 0, 0, 1]
    ])

    return np.matmul(flip_y, cam_inv)


def get_projection_matrix(fov_deg, width, height, n=0.1, f=1000):
    fov = math.radians(fov_deg)
    aspect = width / height
    d = 1 / math.tan(fov / 2)

    return np.array([
        [d / aspect, 0, 0, 0],
        [0, d, 0, 0],
        [0, 0, (n + f) / (n - f), (2 * n * f) / (n - f)],
        [0, 0, -1, 0]
    ])


def get_viewport_matrix(width, height):
    return np.array([
        [width / 2, 0, 0, width / 2],
        [0, -height / 2, 0, height / 2],
        [0, 0, 0.5, 0.5],
        [0, 0, 0, 1]
    ])


def is_front_face(v0, v1, v2):
    # Calculate face normal in view space
    edge1 = v1[:3] - v0[:3]
    edge2 = v2[:3] - v0[:3]
    normal = np.cross(edge1, edge2)

    # Face center in view space
    center = (v0[:3] + v1[:3] + v2[:3]) / 3

    # Camera is at origin in view space
    view_dir = -center

    # If the normal points toward the camera, the face is visible
    return np.dot(normal, view_dir) > 0


def draw_cube(size, position, color, screen, view_matrix, proj_matrix, vp_matrix):
    half = size / 2

    vertices = np.array([
        [-half, -half,  half, 1],
        [ half, -half,  half, 1],
        [ half,  half,  half, 1],
        [-half,  half,  half, 1],
        [-half, -half, -half, 1],
        [ half, -half, -half, 1],
        [ half,  half, -half, 1],
        [-half,  half, -half, 1]
    ])

    faces = [
        [0, 1, 2], [2, 3, 0],
        [7, 6, 5], [5, 4, 7],
        [4, 5, 1], [1, 0, 4],
        [3, 2, 6], [6, 7, 3],
        [4, 0, 3], [3, 7, 4],
        [1, 5, 6], [6, 2, 1]
    ]

    translate = np.array([
        [1, 0, 0, position[0]],
        [0, 1, 0, position[1]],
        [0, 0, 1, position[2]],
        [0, 0, 0, 1]
    ])

    view_vertices = []
    projected_vertices = []

    for v in vertices:
        # Local space -> World space
        world_v = np.matmul(translate, v)

        # World space -> View space
        view_v = np.matmul(view_matrix, world_v)
        view_vertices.append(view_v)

        # View space -> Clip space
        clip_v = np.matmul(proj_matrix, view_v)

        # Perspective divide
        if clip_v[3] != 0:
            ndc_v = clip_v / clip_v[3]
        else:
            ndc_v = clip_v

        # NDC -> Screen space
        screen_v = np.matmul(vp_matrix, ndc_v)
        projected_vertices.append((int(screen_v[0]), int(screen_v[1]), screen_v[2]))

    face_depths = []

    for face in faces:
        v0 = view_vertices[face[0]]
        v1 = view_vertices[face[1]]
        v2 = view_vertices[face[2]]

        # Backface culling
        if not is_front_face(v0, v1, v2):
            continue

        z_avg = sum(projected_vertices[i][2] for i in face) / 3
        face_depths.append((z_avg, face))

    # Painter's algorithm: draw farther faces first
    face_depths.sort(key=lambda x: x[0], reverse=True)

    for _, face in face_depths:
        pts = [(projected_vertices[i][0], projected_vertices[i][1]) for i in face]
        pygame.draw.polygon(screen, color, pts)


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

view_matrix = get_view_matrix(CAM_POS, TARGET_POS, UP)
proj_matrix = get_projection_matrix(FOV, WIDTH, HEIGHT)
vp_matrix = get_viewport_matrix(WIDTH, HEIGHT)

running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    screen.fill(BG_COLOR)

    draw_cube(100, (10, 10, 10), (0, 0, 255), screen, view_matrix, proj_matrix, vp_matrix)
    draw_cube(50, (-150, 150, -10), (0, 255, 0), screen, view_matrix, proj_matrix, vp_matrix)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()