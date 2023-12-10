import numpy as np
import trimesh
import os
import random

# Define panel and segment sizes
panel_size_mm = 420  # Size of the full panel (400x400mm)
segment_size = 210  # Size of each segment (200x200mm)
grid_size = 18      # Grid size for the full panel (18x18 for 400x400mm panel)

# Maximum and minimum heights for the columns
max_height_mm = 30
min_height_mm = 4

# Minimum height difference among squares in a cluster
min_height_difference_mm = 3

# Population size for genetic algorithm
population_size = 100

# Number of generations
num_generations = 100

# Mutation probability
mutation_prob = 0.1

def create_segment_mesh(segment_heights, square_size):
    segment_mesh = trimesh.Trimesh()
    for i in range(segment_heights.shape[0]):
        for j in range(segment_heights.shape[1]):
            height = segment_heights[i, j]
            square = trimesh.creation.box(extents=(square_size, square_size, height))
            square.apply_translation((i * square_size, j * square_size, height / 2))
            segment_mesh += square
    return segment_mesh

def evaluate_fitness(segment_heights):
    # Calculate the fitness based on your criteria
    # You can define your fitness function here
    pass

def genetic_algorithm():
    # Initialize a population of random acoustic panels
    population = [np.random.uniform(min_height_mm, max_height_mm, (7, 7)) for _ in range(population_size)]

    for generation in range(num_generations):
        # Evaluate the fitness of each individual
        fitness_scores = [evaluate_fitness(panel) for panel in population]

        # Select the top-performing individuals
        selected_indices = np.argsort(fitness_scores)[-population_size // 2:]

        # Create a new population through crossover
        new_population = []
        for _ in range(population_size // 2):
            parent1 = population[random.choice(selected_indices)]
            parent2 = population[random.choice(selected_indices)]
            crossover_point = random.randint(1, 5)
            child1 = np.vstack((parent1[:crossover_point], parent2[crossover_point:]))
            child2 = np.vstack((parent2[:crossover_point], parent1[crossover_point:]))
            new_population.extend([child1, child2])

        # Apply mutation
        for i in range(population_size):
            if random.random() < mutation_prob:
                row = random.randint(0, 6)
                col = random.randint(0, 6)
                population[i][row, col] = np.random.uniform(min_height_mm, max_height_mm)

        population = new_population

    # Find the best individual in the final population
    best_index = np.argmax([evaluate_fitness(panel) for panel in population])
    best_acoustic_panel = population[best_index]

    return best_acoustic_panel

# Specify the output directory as the current working directory
output_directory = os.getcwd()

# Run the genetic algorithm to generate the best acoustic panel
best_panel = genetic_algorithm()

# Create and save the STL file for the best acoustic panel
best_panel_mesh = create_segment_mesh(best_panel, segment_size / 7)
stl_path = os.path.join(output_directory, 'best_acoustic_panel.stl')
best_panel_mesh.export(stl_path, file_type='stl')  # Export to STL format
