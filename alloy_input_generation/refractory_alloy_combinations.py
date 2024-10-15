from itertools import combinations
import logging

# Initialize logging
logging.basicConfig(filename='alloy_combinations.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Define nine refractory elements and their corresponding properties
elements = {
    'Ti': {'atomic_number': 22, 'density': 4.5, 'melting_point': 1668},
    'V': {'atomic_number': 23, 'density': 6.0, 'melting_point': 1910},
    'Nb': {'atomic_number': 41, 'density': 8.57, 'melting_point': 2477},
    'Ta': {'atomic_number': 73, 'density': 16.65, 'melting_point': 3017},
    'Cr': {'atomic_number': 24, 'density': 7.19, 'melting_point': 1907},
    'Zr': {'atomic_number': 40, 'density': 6.52, 'melting_point': 1855},
    'Hf': {'atomic_number': 72, 'density': 13.31, 'melting_point': 2233},
    'Mo': {'atomic_number': 42, 'density': 10.28, 'melting_point': 2623},
    'W': {'atomic_number': 74, 'density': 19.25, 'melting_point': 3422}
}

def generate_combinations(elements, combo_size):
    """
    Generate all possible combinations of the elements.
    :param elements: Dictionary of elements
    :param combo_size: Size of each combination
    :return: List of combinations
    """
    unique_elements = list(elements.keys())  # Ensure elements are unique
    return list(combinations(unique_elements, combo_size))

def calculate_average_property(combo, elements, property_name):
    """
    Calculate the average of a specified property for a combination.
    :param combo: A combination of elements
    :param elements: Dictionary of elements
    :param property_name: The property to average
    :return: Average value of the property
    """
    total_property_value = sum(elements[element][property_name] for element in combo)
    return total_property_value / len(combo)

def filter_combinations(combinations_list, elements, property_name, threshold):
    """
    Filter combinations based on a property threshold.
    :param combinations_list: List of combinations
    :param elements: Dictionary of elements
    :param property_name: The property to filter by
    :param threshold: The threshold value
    :return: Filtered list of combinations
    """
    filtered_combos = []
    for combo in combinations_list:
        avg_property_value = calculate_average_property(combo, elements, property_name)
        if avg_property_value >= threshold:
            filtered_combos.append(combo)
    return filtered_combos

def save_combinations_to_file(combinations_list, filename):
    """
    Save the combinations to a file.
    :param combinations_list: List of combinations
    :param filename: Name of the file
    """
    with open(filename, 'w') as file:
        for combo in combinations_list:
            file.write(", ".join(combo) + "\n")

def main():
    # User input for combination size
    combo_size =4
    # Generate combinations
    combinations_list = generate_combinations(elements, combo_size)
    logging.info(f"Generated {len(combinations_list)} combinations.")
    
    # Calculate and display properties for each combination
    for combo in combinations_list:
        avg_atomic_number = calculate_average_property(combo, elements, 'atomic_number')
        avg_density = calculate_average_property(combo, elements, 'density')
        avg_melting_point = calculate_average_property(combo, elements, 'melting_point')
        print(f"Combination: {combo}, Avg Atomic Number: {avg_atomic_number:.2f}, "
              f"Avg Density: {avg_density:.2f}, Avg Melting Point: {avg_melting_point:.2f}")
    
    # Filter combinations by a property threshold
    property_name = 'melting_point'
    threshold = 2000
    filtered_combinations = filter_combinations(combinations_list, elements, property_name, threshold)
    logging.info(f"Filtered {len(filtered_combinations)} combinations with {property_name} >= {threshold}.")
    
    # Save all combinations to a file
    save_combinations_to_file(combinations_list, 'all_combinations.txt')
    print("All combinations have been saved to all_combinations.txt")
    
    # Save filtered combinations to a file
    save_combinations_to_file(filtered_combinations, 'filtered_combinations.txt')
    print(f"Filtered combinations (melting point >= {threshold}) have been saved to filtered_combinations.txt")

if __name__ == '__main__':
    main()