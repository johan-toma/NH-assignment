from dotenv import load_dotenv, dotenv_values
import os, json, openai, sys
load_dotenv()
OPENAI = os.getenv('OPENAI')

def load_json(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)

def save_output(filepath, content):
    with open(filepath, 'w') as file:
        json.dump(content, file, indent=2)
        
def generate_prompt(data):
    patient = data['patient']
    consultation = data['consultation']
    
    prompt = f""" 
    You are a veterinary assistant. Based on the following consultation data, 
    please generate empathetic and clear discharge notes for the pet's owner. 
    
    These are the patients details:
    Name: {patient['name']}
    Species: {patient['species']}
    Breed: {patient['breed']}
    Gender: {patient['gender']}
    Neutered: {"Yes" if patient['neutered'] else "No"}
    Date of Birth: {patient['date_of_birth']}
    Weight: {patient['weight']}
    
    The Consultation is on {consultation['date']} at {consultation['time']}:
    Reason: {consultation['reason']}
    Type: {consultation['type']}
    Clinical Notes:
    """
    
    for note in consultation.get('clinical notes', []):
        prompt += f" {note['note']}\n"
    
    procedures = consultation['treatment_items'].get('procedures', [])
    if len(procedures) == 0:
        prompt += "\nProcedures performed: \n"
        for procedure in procedures:
            prompt += f" - {procedure['name']} at {procedure['time']} on {procedure['date']}\n"
    
    prompt += "\nPlease write the discharge note in plain language for the pet owner. Summarizing what was done and what to watch for or what to do next.\n"
    return prompt.strip()

def get_discharge_note(prompt):
    openai.api_key = OPENAI
    
    if not openai.api_key:
        print('ERROR: Missing API KEY')
        sys.exit(1)
    
    
    response = openai.ChatCompletion.create(
        model='gpt-4o',
        messages = [
            {"role": "system", "content": "You are a helpful veterinary assistant"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=500,
        frequency_penalty=0.2,
        presence_penalty=0.1,
        top_p=1.0
    )
    
    return response['choices'][0]['message']['content'].strip()


def main():
    if len(sys.argv) > 2:
        print("ERROR: Too many arguments\nex: generate_discharge_note.py path/to/input.json")
        sys.exit(1)
    elif len(sys.argv) < 2:
        print("ERROR: Missing input file\nex: generate_discharge_note.py path/to/input.json")
        sys.exit(1)
    
    input_path = sys.argv[1]
    base_name = os.path.basename(input_path)
    
    output_path = os.path.join('solution', base_name.replace('.json', "_output.json"))
    
    data = load_json(input_path)
    print(f"Loading the data {data}")
    prompt = generate_prompt(data)
    print("Generating prompt for LLM...")
    discharge_note = get_discharge_note(prompt)
    print(f"Saving discharge note to: {output_path}")
    save_output(output_path, {"discharge_note": discharge_note})
    print(f"Discharge note has been generated!")


if __name__ == '__main__':
    main()
    