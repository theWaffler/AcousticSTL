import numpy as np
import trimesh
import os
import random

def generate_qrd_sequence(N, p):
    qrd_sequence = np.zeros(N)
    for i in range(N):
        qrd_sequence[i] = i % p
    return qrd_sequence

def find_next_prime(n):
    while True:
        n += 1
        for i in range(2, int(np.sqrt(n)) + 1):
            if n % i == 0:
                break
        else:
            return n

def create_segment_mesh(segment_heights, square_size):
    segment_mesh = trimesh.Trimesh()
    for i in range(segment_heights.shape[0]):
        for j in range(segment_heights.shape[1]):
            height = segment_heights[i, j]
            square = trimesh.creation.box(extents=(square_size, square_size, height))
            square.apply_translation((i * square_size, j * square_size, height / 2))
            segment_mesh += square
    return segment_mesh

panel_size_mm = 400  # Size of the full panel (400x400mm)
segment_size = 200  # Size of each segment (200x200mm)
grid_size = 18      # Grid size for the full panel (18x18 for 400x400mm panel)
max_height_mm = 20
min_height_mm = 3

#prime_number = find_next_prime(grid_size)
prime_number = 5
qr_sequence = generate_qrd_sequence(grid_size, prime_number)

output_directory = os.getcwd()

full_panel_heights = np.zeros((grid_size, grid_size))
for i in range(grid_size):
    for j in range(grid_size):
        full_panel_heights[i, j] = (qr_sequence[(i + j) % prime_number] / prime_number) * (max_height_mm - min_height_mm) + min_height_mm

square_size = segment_size / grid_size

random_height_range = (min_height_mm, max_height_mm)
randomized_heights = full_panel_heights + np.random.uniform(random_height_range[0], random_height_range[1], full_panel_heights.shape)

randomized_order = list(range(grid_size * grid_size))
random.shuffle(randomized_order)

def is_adjacency_valid(heights, i, j):
    adjacent_heights = []
    if i > 0:
        adjacent_heights.append(heights[i - 1, j])
    if i < heights.shape[0] - 1:
        adjacent_heights.append(heights[i + 1, j])
    if j > 0:
        adjacent_heights.append(heights[i, j - 1])
    if j < heights.shape[1] - 1:
        adjacent_heights.append(heights[i, j + 1])
    return adjacent_heights.count(heights[i, j]) <= 2

while True:
    is_valid_placement = True
    for i in range(1, len(randomized_order)):
        row = randomized_order[i] // grid_size
        col = randomized_order[i] % grid_size
        if not is_adjacency_valid(randomized_heights, row, col):
            is_valid_placement = False
            random.shuffle(randomized_order)
            break
    if is_valid_placement:
        break
    
#makes n x m grid
segment_stl_paths = []
for i in range(2):
    for j in range(2):
        segment_start_x = i * 7
        segment_start_y = j * 7
        segment_heights = randomized_heights[segment_start_x:segment_start_x + 7, segment_start_y:segment_start_y + 7]
        segment_mesh = create_segment_mesh(segment_heights, square_size)
        stl_path = os.path.join(output_directory, f'qrd_panel_segment_{i * 2 + j + 1}.stl')
        segment_mesh.export(stl_path, file_type='stl')
        segment_stl_paths.append(stl_path)

segment_stl_paths
