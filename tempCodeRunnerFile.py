import json
from pathlib import Path

def load_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def save_data(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)

def find_and_rearrange(features):
    if not features:
        return []
    
    ordered_features = []
    remaining_features = features[:]
    current_feature = features[-1]

    for feature in features:
        is_unique = True
        for other in features:
            # if feature['first_coordinate'] == other['last_coordinate']:
            if abs(feature['first_coordinate'][0] - other['last_coordinate'][0]) < 0.001 and abs(feature['first_coordinate'][1] - other['last_coordinate'][1]) < 0.001:
                is_unique = False
                break
        if is_unique:
            current_feature = feature
            break

    while current_feature:
        ordered_features.append(current_feature)
        remaining_features.remove(current_feature)
        next_feature = None
        for feature in remaining_features:
            if feature['first_coordinate'] == current_feature['last_coordinate']:
                next_feature = feature
                break
        current_feature = next_feature

    while current_feature:
        ordered_features.append(current_feature)
        remaining_features.remove(current_feature)
        next_feature = None
        for feature in remaining_features:
            if abs(feature['first_coordinate'][0] - current_feature['last_coordinate'][0]) < 0.001 and abs(feature['first_coordinate'][1] - current_feature['last_coordinate'][1]) < 0.001:
                next_feature = feature
                break
        current_feature = next_feature
   
    if len(remaining_features) != 0:
        ordered_features.reverse()
        for feature in ordered_features:
            temp = feature['first_coordinate']
            feature['first_coordinate'] = feature['last_coordinate']
            feature['last_coordinate'] = temp 
        current_feature = ordered_features[-1]
        ordered_features.remove(current_feature)


        while current_feature:
            ordered_features.append(current_feature)
            if current_feature in remaining_features:
                remaining_features.remove(current_feature)
            next_feature = None
            for feature in remaining_features:
                if abs(feature['first_coordinate'][0] - current_feature['last_coordinate'][0]) < 0.001 and abs(feature['first_coordinate'][1] - current_feature['last_coordinate'][1]) < 0.001:
                    next_feature = feature
                    break
            current_feature = next_feature
    
    if len(remaining_features) != 0:
        for feature in remaining_features:
            temp = feature['first_coordinate']
            feature['first_coordinate'] = feature['last_coordinate']
            feature['last_coordinate'] = temp 

        current_feature = ordered_features[-1]
        ordered_features.remove(current_feature)

        while current_feature:
            ordered_features.append(current_feature)
            if current_feature in remaining_features:
                remaining_features.remove(current_feature)
           
            next_feature = None
            for feature in remaining_features:
                if abs(feature['first_coordinate'][0] - current_feature['last_coordinate'][0]) < 0.003 and abs(feature['first_coordinate'][1] - current_feature['last_coordinate'][1]) < 0.003:
                    next_feature = feature
                    break
            current_feature = next_feature
    
    if len(remaining_features) != 0:
        for feature in remaining_features:
            temp = feature['first_coordinate']
            feature['first_coordinate'] = feature['last_coordinate']
            feature['last_coordinate'] = temp 

        current_feature = ordered_features[-1]
        ordered_features.remove(current_feature)

        while current_feature:
            ordered_features.append(current_feature)
            if current_feature in remaining_features:
                remaining_features.remove(current_feature)
        
            next_feature = None
            for feature in remaining_features:
                print(feature['id'], feature['first_coordinate'][0], current_feature['last_coordinate'][0])
                if abs(feature['first_coordinate'][0] - current_feature['last_coordinate'][0]) < 0.003 and abs(feature['first_coordinate'][1] - current_feature['last_coordinate'][1]) < 0.003:
                    next_feature = feature
                    break
            current_feature = next_feature

    return ordered_features

def extract_feature_coordinates(feature):
    coords = feature['geometry']['coordinates']
    return {
        'first_coordinate': coords[0],
        'last_coordinate': coords[-1],
        'id': feature['properties']['id']
    }

def are_coordinates_equal(coord1, coord2, tolerance=0.001):
    return (abs(coord1[0] - coord2[0]) < tolerance and 
            abs(coord1[1] - coord2[1]) < tolerance)

def find_matching_feature(target_coords, target_id, features, used_indices):
    for idx, feature in enumerate(features):
        if idx in used_indices:
            continue
            
        if feature['properties']['id'] != target_id:
            continue
            
        coords = feature['geometry']['coordinates']
        start_coord = coords[0]
        end_coord = coords[-1]
        
        if (are_coordinates_equal(start_coord, target_coords) or 
            are_coordinates_equal(end_coord, target_coords)):
            return idx
    return None

def reorder_features(geojson_data):
    features = geojson_data['features']
    coordinate_features = [extract_feature_coordinates(f) for f in features]

    ordered_segments = find_and_rearrange(coordinate_features)
    
    reordered_features = []
    used_indices = set()

    for segment in ordered_segments:
        first_coord = segment['first_coordinate']
        last_coord = segment['last_coordinate']
        segment_id = segment['id']
        
        idx = find_matching_feature(first_coord, segment_id, features, used_indices)
        if idx is not None:
            feature = features[idx]
            coords = feature['geometry']['coordinates']
         
            if are_coordinates_equal(coords[-1], first_coord):
                feature = feature.copy()
                feature['geometry'] = feature['geometry'].copy()
                feature['geometry']['coordinates'] = list(reversed(coords))
                
            reordered_features.append(feature)
            used_indices.add(idx)
    
    new_geojson = geojson_data.copy()
    new_geojson['features'] = reordered_features
    return new_geojson

def process_file(input_path, output_path):
    """Process a single GeoJSON file."""
    try:
        data = load_data(input_path)
        processed_data = reorder_features(data)
        
        save_data(processed_data, output_path)
        print(f"Successfully processed: {input_path.name}")
       
        original_count = len(data['features'])
        processed_count = len(processed_data['features'])
        print(f"Original features: {original_count}")
        print(f"Features in output: {processed_count}")
        print(f"Features filtered out: {original_count - processed_count}")
        
    except Exception as e:
        print(f"Error processing {input_path.name}: {str(e)}")

def main():
    input_folder = './data'
    output_folder = './transformed_data'
    
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    
    for input_path in Path(input_folder).glob('*.json'):
        output_path = Path(output_folder) / input_path.name
        process_file(input_path, output_path)

if __name__ == "__main__":
    main()