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

def create_panel_mesh(panel_heights, square_size):
    panel_mesh = trimesh.Trimesh()
    for i in range(panel_heights.shape[0]):
        for j in range(panel_heights.shape[1]):
            height = panel_heights[i, j]
            square = trimesh.creation.box(extents=(square_size, square_size, height))
            square.apply_translation((i * square_size, j * square_size, height / 2))
            panel_mesh += square
    return panel_mesh

# Panel and segment sizes
panel_size_mm = 200  # Size of each panel (200x200mm)
grid_size = 7        # Grid size for each panel (9x9 for 200x200mm panel)
max_height_mm = 25
min_height_mm = 1

# Prime number for QRD sequence
prime_number = 7
qr_sequence = generate_qrd_sequence(grid_size, prime_number)

# Output directory
output_directory = 'panels'
os.makedirs(output_directory, exist_ok=True)

# Specify the number of panels you want to generate
num_panels = 5

for panel_num in range(num_panels):
    # Create a copy of the QRD sequence and shuffle it to randomize heights
    randomized_qrd_sequence = qr_sequence.copy()
    random.shuffle(randomized_qrd_sequence)

    # Create a 2D grid for the panel with heights based on the shuffled QRD sequence
    panel_heights = np.zeros((grid_size, grid_size))
    for i in range(grid_size):
        for j in range(grid_size):
            panel_heights[i, j] = (randomized_qrd_sequence[(i + j) % prime_number] / prime_number) * (max_height_mm - min_height_mm) + min_height_mm

    # Size of each square in the panel
    square_size = panel_size_mm / grid_size

    # Generate the panel mesh
    panel_mesh = create_panel_mesh(panel_heights, square_size)

    # Save the panel as an STL file
    stl_path = os.path.join(output_directory, f'panel_{panel_num + 1}.stl')
    panel_mesh.export(stl_path, file_type='stl')  # Export to STL format

    print(f'Generated panel {panel_num + 1} in the directory: {output_directory}')
