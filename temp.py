import json
import math
from pathlib import Path

def load_data(filepath):
    with open(filepath, 'r') as file:
        data = json.load(file)
    return data

def save_data(data, filepath):
    with open(filepath, 'w') as file:
        json.dump(data, file, indent=2)

def extract_feature_details(data):
    results = {
        "total_features": len(data["features"]),
        "features_info": []
    }
    for feature in data["features"]:
        feature_id = feature["properties"]["id"]
        coordinates = feature["geometry"]["coordinates"]
        first_coord = coordinates[0]
        last_coord = coordinates[-1]
        
        feature_info = {
            "id": feature_id,
            "first_coordinate": first_coord,
            "last_coordinate": last_coord
        }
        results["features_info"].append(feature_info)
    return results

def find_and_rearrange(features):
    if not features:
        return []
    
    def coordinates_match(coord1, coord2, tolerance=0.003):
        """Helper function to compare coordinates with tolerance"""
        return (abs(coord1[0] - coord2[0]) < tolerance and 
                abs(coord1[1] - coord2[1]) < tolerance)
    
    def find_next_feature(current, remaining, reverse=False):
        """Find the next connected feature in the chain"""
        for feature in remaining:
            current_end = current['first_coordinate'] if reverse else current['last_coordinate']
            feature_start = feature['last_coordinate'] if reverse else feature['first_coordinate']
            if coordinates_match(current_end, feature_start):
                return feature
        return None
    
    def try_connect_features(start_feature, features_list, reverse=False):
        """Attempt to connect features starting from a given feature"""
        ordered = [start_feature]
        remaining = [f for f in features_list if f != start_feature]
        current = start_feature
        
        while current:
            next_feature = find_next_feature(current, remaining, reverse)
            if next_feature:
                ordered.append(next_feature)
                remaining.remove(next_feature)
                current = next_feature
            else:
                break
                
        return ordered, remaining
    
    # Find a starting feature (one that nothing connects to)
    start_feature = None
    for feature in features:
        if not any(coordinates_match(feature['first_coordinate'], f['last_coordinate']) 
                  for f in features if f != feature):
            start_feature = feature
            break
    
    if not start_feature:
        start_feature = features[0]  # If no clear start, take the first one
        
    # Try connecting features in forward direction
    ordered_features, remaining = try_connect_features(start_feature, features)
    
    # If there are remaining features, try reverse direction
    if remaining:
        # Reverse coordinates of all features
        for feature in ordered_features + remaining:
            feature['first_coordinate'], feature['last_coordinate'] = \
                feature['last_coordinate'], feature['first_coordinate']
        
        # Try connecting again with reversed coordinates
        ordered_features, remaining = try_connect_features(ordered_features[-1], 
                                                         ordered_features + remaining)
    
    return ordered_features


# def process_folder(input_folder, output_folder):
#     Path(output_folder).mkdir(parents=True, exist_ok=True)
    
#     for input_path in Path(input_folder).glob('*.json'):
#         print(f"\nProcessing: {input_path.name}")
#         output_path = Path(output_folder) / input_path.name
        
#         try:
#             data = load_data(input_path)
#             feature_details = extract_feature_details(data)
#             ordered_features = find_and_rearrange(feature_details['features_info'])
#             save_data({"features": ordered_features}, output_path)
#             print(f"Saved processed file: {output_path.name}")
#         except Exception as e:
#             print(f"Error processing {input_path.name}: {str(e)}")

# def main():
#     input_folder = './data'
#     output_folder = './transformed_data'
#     process_folder(input_folder, output_folder)

# if __name__ == "__main__":
#     main()

# def load_data(filepath):
#     with open(filepath, 'r') as file:
#         data = json.load(file)
#     return data

# File path to the JSON data
file_path = 'data/orange_line.json'

# Load data from JSON file
data = load_data(file_path)

# Extract features and their details from the data
feature_details = extract_feature_details(data)
# print(json.dumps(feature_details, indent=2))
ordered_features = find_and_rearrange(feature_details['features_info'])
print(json.dumps(ordered_features, indent=2))
print(len(ordered_features))


# Print the sorted feature details
# print(json.dumps(feature_details, indent=2))
