import json

def filter_and_save_lines(input_file_path, output_folder_path, desired_lines):

    with open(input_file_path, 'r') as file:
        data = json.load(file)

    filtered_features = {line: [] for line in desired_lines}

    for feature in data['features']:
        if 'properties' in feature and 'lines' in feature['properties']:
        
            for line_info in feature['properties']['lines']:
                line_name = line_info['line']
                if line_name in desired_lines:
                    filtered_features[line_name].append(feature)

    for line, features in filtered_features.items():
        new_geojson = {
            'type': 'FeatureCollection',
            'features': features
        }
       
        output_file_path = f"{output_folder_path}/{line.replace(' ', '_').lower()}.json"
        with open(output_file_path, 'w') as file:
            json.dump(new_geojson, file, indent=4)
            print(f"Created GeoJSON for {line} with {len(features)} features.")

input_file_path = './dallas_sections.geojson'
output_folder_path = './data'
desired_lines = ['Blue Line', 'Green Line', 'Orange Line', 'Red Line']

filter_and_save_lines(input_file_path, output_folder_path, desired_lines)
