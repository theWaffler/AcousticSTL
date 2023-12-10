import numpy as np
import trimesh
import os
import multiprocessing

# Constants
speed_of_sound = 343  # Speed of sound in air in m/s

# User inputs
center_frequency = 1000  # Center frequency for the diffusor in Hz
panel_width_mm, panel_height_mm = 1000, 1000  # Dimensions of the QRD diffusor panel
prime_number = 71   # Prime number for QRD calculation
printer_bed_size_mm = (200, 200)  # Size of the 3D printer bed
min_height_mm = 5   # Minimum height for the wells

# Function to generate a 2D QRD sequence for a segment
def generate_2d_qrd_sequence_for_segment(segment_x, segment_y, prime_number, segment_size_x, segment_size_y):
    qr_sequence = np.zeros((segment_size_x, segment_size_y))
    for i in range(segment_size_x):
        for j in range(segment_size_y):
            x_index = i + segment_x * segment_size_x
            y_index = j + segment_y * segment_size_y
            qr_sequence[i, j] = (x_index**2 + y_index**2) % prime_number
    return qr_sequence

# Function to create the mesh for a segment
def create_segment_mesh(segment_heights, grid_size_x, grid_size_y):
    segment_mesh = trimesh.Trimesh()
    for i in range(grid_size_x):
        for j in range(grid_size_y):
            height = segment_heights[i, j]
            square = trimesh.creation.box(extents=(grid_size_x, grid_size_y, height))
            square.apply_translation((i * grid_size_x, j * grid_size_y, height / 2))
            segment_mesh += square
    return segment_mesh

# Function to process a single segment (to be used with multiprocessing)
def process_segment(segment_coordinates):
    segment_x, segment_y = segment_coordinates
    wavelength_mm = (speed_of_sound * 1000) / center_frequency
    max_height_mm = wavelength_mm / 4  # Quarter wavelength
    num_segments_x = int(np.ceil(panel_width_mm / printer_bed_size_mm[0]))
    num_segments_y = int(np.ceil(panel_height_mm / printer_bed_size_mm[1]))
    segment_size_x = min(printer_bed_size_mm[0], panel_width_mm - segment_x * printer_bed_size_mm[0])
    segment_size_y = min(printer_bed_size_mm[1], panel_height_mm - segment_y * printer_bed_size_mm[1])
    qr_sequence = generate_2d_qrd_sequence_for_segment(segment_x, segment_y, prime_number, segment_size_x, segment_size_y)
    normalized_sequence = qr_sequence / (prime_number - 1)
    segment_heights = normalized_sequence * (max_height_mm - min_height_mm) + min_height_mm
    segment_mesh = create_segment_mesh(segment_heights, segment_size_x, segment_size_y)
    output_directory = os.getcwd()
    stl_path = os.path.join(output_directory, f'qrd_segment_{segment_x}_{segment_y}.stl')
    segment_mesh.export(stl_path, file_type='stl')
    return f"Generated STL file for segment ({segment_x}, {segment_y}) is saved at: {stl_path}"

# Prepare list of segment coordinates for multiprocessing
num_segments_x = int(np.ceil(panel_width_mm / printer_bed_size_mm[0]))
num_segments_y = int(np.ceil(panel_height_mm / printer_bed_size_mm[1]))
segment_coordinates = [(x, y) for x in range(num_segments_x) for y in range(num_segments_y)]

# Use multiprocessing to process each segment
if __name__ == "__main__":
    with multiprocessing.Pool() as pool:
        results = pool.map(process_segment, segment_coordinates)

    for result in results:
        print(result)
