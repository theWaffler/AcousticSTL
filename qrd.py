import numpy as np
import trimesh
import os

def generate_qrd_sequence(N, p):
    qrd_sequence = np.zeros(N)
    for i in range(N):
        qrd_sequence[i] = i % p
    return qrd_sequence

# Define panel and segment sizes
panel_size_mm = 420  # Size of the full panel (420x420mm)
segment_size = 210  # Size of each segment (210x210mm)
grid_size = 18      # Grid size for the full panel (18x18 for 420x420mm panel)

prime_number = 71  # Choose a prime number (you can change this)
qr_sequence = generate_qrd_sequence(grid_size * grid_size, prime_number)

output_directory = os.getcwd()

# Function to create the mesh for a segment
def create_segment_mesh(segment_heights, square_size):
    segment_mesh = trimesh.Trimesh()
    for i in range(segment_heights.shape[0]):
        for j in range(segment_heights.shape[1]):
            height = segment_heights[i, j]
            square = trimesh.creation.box(extents=(square_size, square_size, height))
            square.apply_translation((i * square_size, j * square_size, height / 2))
            segment_mesh += square
    return segment_mesh

# Function to assign heights based on QRD principles
def assign_heights_qrd(grid_size, prime_number):
    qr_sequence = generate_qrd_sequence(grid_size * grid_size, prime_number)
    heights = np.zeros((grid_size, grid_size))
    for i in range(grid_size):
        for j in range(grid_size):
            index = i * grid_size + j
            height = qr_sequence[index]
            heights[i, j] = height
    return heights

# Size of each square in the segments
square_size = segment_size / grid_size

# Generate heights based on QRD principles
randomized_heights = assign_heights_qrd(grid_size, prime_number)

# Generate and save the STL files for each segment with QRD-based height distribution
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
