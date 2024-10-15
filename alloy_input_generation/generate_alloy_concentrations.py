import os
import random
import logging
from alloy_combinations import generate_combinations, save_combinations_to_file, elements

# Initialize logging
logging.basicConfig(filename='alloy_concentrations.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def generate_random_concentrations(combo, num_sets=36):
    """
    Generate random concentrations for each element in a combination.
    Ensures that the sum of concentrations for each set is 100%.
    :param combo: A combination of elements
    :param num_sets: Number of concentration sets to generate
    :return: List of concentration sets
    """
    concentration_sets = []
    for _ in range(num_sets):
        # Generate random concentrations ensuring the sum is 100
        random_concentrations = [random.random() for _ in range(len(combo))]
        total = sum(random_concentrations)
        concentrations = [round((val / total) * 100, 2) for val in random_concentrations]
        concentration_sets.append(concentrations)
    return concentration_sets

def save_concentration_sets_to_file(combo, concentration_sets, filename):
    """
    Save the generated concentration sets for each combination to a file.
    :param combo: A combination of elements
    :param concentration_sets: List of concentration sets
    :param filename: Name of the file
    """
    with open(filename, 'a') as file:
        file.write(f"Combination: {', '.join(combo)}\n")
        for concentrations in concentration_sets:
            file.write(", ".join(f"{elem}: {conc}%" for elem, conc in zip(combo, concentrations)) + "\n")
        file.write("\n")

def main():
    # User input for combination size
    combo_size = 4
    
    # Generate combinations
    combinations_list = generate_combinations(elements, combo_size)
    logging.info(f"Generated {len(combinations_list)} combinations.")
    
    # Generate and save random concentration sets for each combination
    concentration_filename = 'alloy_concentrations.txt'
    for combo in combinations_list:
        concentration_sets = generate_random_concentrations(combo)
        save_concentration_sets_to_file(combo, concentration_sets, concentration_filename)
    print(f"Random concentration sets for each combination have been saved to {concentration_filename}")

if __name__ == '__main__':
    print(os.getcwd())
    main()