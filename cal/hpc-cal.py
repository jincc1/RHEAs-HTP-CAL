import os
import re

def read_combinations(filename):
    """Read the alloy combinations from the specified file."""
    combinations = []
    with open(filename, 'r') as file:
        for line in file:
            # Assuming each line starts with "Combination: "
            if line.startswith("Combination: "):
                combo = line.split(": ")[1].strip().split(", ")
                combinations.append(combo)
    return combinations

def read_concentrations(filename):
    """Read the alloy concentrations from the specified file."""
    concentrations = []
    with open(filename, 'r') as file:
        current_concentration_set = []
        for line in file:
            if line.startswith("Combination: "):
                # If we hit a new combination, save the current set and reset
                if current_concentration_set:  # Save the previous set
                    concentrations.append(current_concentration_set)
                    current_concentration_set = []
                continue
            
            if line.strip():  # Skip empty lines
                # Parse the concentrations from the line
                concentration_data = re.findall(r'(\w+): ([\d.]+)%', line)
                concentrations.append([float(conc) for elem, conc in concentration_data])
        
        # Append the last set if exists
        if current_concentration_set:
            concentrations.append(current_concentration_set)
    
    return concentrations

def update_emto_parameters(species, concs):
    """Update the EMTO-CPA parameters with the provided species and concentrations."""
    # For demonstration, let's just print the values
    for combo, concentration_set in zip(species, concs):
        print("Updated species:", combo)
        print("Updated concentrations:", concentration_set)

def main():
    # Define path to the files
    combinations_file = os.path.join('alloy_input_generation', 'alloy_combinations.txt')
    concentrations_file = os.path.join('alloy_input_generation', 'alloy_concentrations.txt')
    
    # Read combinations and concentrations
    species = read_combinations(combinations_file)
    concs = read_concentrations(concentrations_file)

    # Check if we have the right number of combinations and concentrations
    if len(species) != 126:
        print(f"Warning: Expected 126 combinations, but found {len(species)}.")
    
    if len(concs) != 126 * 36:  # Expecting 36 concentrations for each of the 126 combinations
        print(f"Warning: Expected {126 * 36} concentrations, but found {len(concs)}.")

    # Update EMTO parameters
    update_emto_parameters(species, concs)

if __name__ == '__main__':
    main()