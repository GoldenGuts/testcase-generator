import json, re

def extract_and_repair_json(input_string):
    print("Extracting and repairing JSON data..." + input_string)
    # Try to find the start of the JSON array
    start_index = input_string.find('[')
    if start_index == -1:
        return 'No JSON array found in the input.'

    # Attempt to isolate the JSON array part from the string
    end_index = input_string.rfind(']') + 1
    if end_index == 0:
        return 'No JSON array found in the input.'

    json_part = input_string[start_index:end_index]

    # Attempt to fix common JSON array errors by parsing and reconstructing the array
    fixed_json_array = []
    in_brackets = 0
    current_object = ''
    for char in json_part:
        if char == '{':
            if in_brackets == 0:
                current_object = char
            else:
                current_object += char
            in_brackets += 1
        elif char == '}':
            in_brackets -= 1
            current_object += char
            if in_brackets == 0:
                try:
                    # Attempt to parse the current object as JSON
                    obj = json.loads(current_object)
                    fixed_json_array.append(obj)
                except json.JSONDecodeError:
                    # If an error occurs, skip this object
                    pass
        else:
            if in_brackets > 0:
                current_object += char

    # Return the cleaned and reconstructed JSON array
    return json.dumps(fixed_json_array)
