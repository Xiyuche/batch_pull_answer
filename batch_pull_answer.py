import asyncio
import aiohttp
import yaml
import csv
from tqdm import tqdm
from typing import List, Dict

# Function to read the configuration from YAML file
def read_config(config_file: str):
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config

# Function to read questions from a CSV file
def read_questions_from_csv(filename: str) -> List[str]:
    questions = []
    with open(filename, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            questions.append(row['question'])
    return questions

# Function to write the collected answers to a CSV file
def write_answers_to_csv(questions: List[str], answers: List[Dict[str, str]], model_names: List[str], filename: str):
    with open(filename, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['question'] + model_names
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for i, question in enumerate(questions):
            row = {'question': question}
            row.update(answers[i])
            writer.writerow(row)

# Asynchronous function to query a model
async def query_model(session: aiohttp.ClientSession, question: str, model_info: Dict, system_prompt: str, semaphore: asyncio.Semaphore):
    async with semaphore:
        try:
            messages = [
                {"role": "system", "content": system_prompt.format(question=question)},
                {"role": "user", "content": question},
            ]
            payload = {
                "model": model_info['name'],
                "messages": messages,
            }
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {model_info['client']['api_key']}"
            }
            async with session.post(f"{model_info['client']['base_url']}/chat/completions", json=payload, headers=headers) as resp:
                if resp.status == 200:
                    response = await resp.json()
                    return response['choices'][0]['message']['content'].strip()
                else:
                    print(f"Error querying {model_info['name']}: {resp.status} {await resp.text()}")
                    return "Error"
        except Exception as e:
            print(f"Exception querying {model_info['name']}: {e}")
            return "Error"

# Function to process a single model
async def process_model(session, model_info, questions, system_prompt, answers, position):
    semaphore = asyncio.Semaphore(model_info.get('concurrency', 1))
    model_name = model_info['name']
    tasks = []
    progress_bar = tqdm(
        total=len(questions),
        desc=f"Processing {model_name}",
        position=position,
        leave=True,
        dynamic_ncols=True
    )
    for idx, question in enumerate(questions):
        task = asyncio.create_task(
            query_model(session, question, model_info, system_prompt, semaphore)
        )
        tasks.append((idx, task))
    for idx, task in tasks:
        result = await task
        answers[idx][model_name] = result
        progress_bar.update(1)
    progress_bar.close()

# Main asynchronous function
async def main_async(config: Dict, questions: List[str]):
    answers = [{} for _ in range(len(questions))]
    async with aiohttp.ClientSession() as session:
        model_tasks = []
        for position, model_info in enumerate(config['models']):
            model_task = asyncio.create_task(
                process_model(session, model_info, questions, config['system_prompt'], answers, position)
            )
            model_tasks.append(model_task)
        await asyncio.gather(*model_tasks)
    return answers

# Main function
def main():
    # Load configuration
    config_file = 'config.yaml'
    config = read_config(config_file)

    # Load questions from the input CSV
    input_file = config['input_file']  # Update this to your input file path
    questions = read_questions_from_csv(input_file)

    # Run the asynchronous main function
    answers = asyncio.run(main_async(config, questions))

    # Write the results to a CSV file
    output_file = config['output_file']  # Update this to your output file path
    model_names = [model['name'] for model in config['models']]
    write_answers_to_csv(questions, answers, model_names, output_file)
    print(f"Results saved to {output_file}")

# Run the script
if __name__ == "__main__":
    main()
