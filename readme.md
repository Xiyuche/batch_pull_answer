# Batch Model Answer Collector

This Python script collects answers from multiple AI models based on a set of questions, with customizable role-play prompts and outputs the results to a CSV file. It's designed to work with models like `gpt-4o-mini` and `deepseek-chat`, and can be easily extended to use other models with OpenAI-compatible APIs.

## Features

- Asynchronous querying of multiple AI models in parallel.
- Customizable system prompts for role-playing, e.g., simulating responses from a historical or fictional character.
- Input and output file paths are configurable via `config.yaml`.

## Requirements

The following Python packages are required for the script to run:

```bash
aiohttp
PyYAML
tqdm
```

You can install the required packages using the following command:

```bash
pip install -r requirements.txt
```

## Configuration

The configuration for the script is stored in the `config.yaml` file. It includes:

- **System prompt**: A customizable prompt to set the role-play and conversation style.
- **Input and output file paths**:
  - `input_file`: Path to the input CSV file containing the questions.
  - `output_file`: Path where the collected model answers will be saved.
- **Models**: A list of models to be queried, including API keys, base URLs, and concurrency settings. Feel free to add more models.

Example `config.yaml`:

```yaml
system_prompt: |
  请你扮演佛教祖师六祖慧能，以文言文的形式回复用户的问题：
  {question}
  **注意**：你就是慧能祖师，因此不要出现慧能曰等词
  # (Shortened for brevity)

input_file: 'csv/knowledge_questions.csv'
output_file: 'model_answers.csv'

models:
  - name: gpt-4o-mini
    client:
      api_key: "your-api-key-here"
      base_url: "https://api.openai-proxy.org/v1"
    concurrency: 10
  - name: deepseek-chat
    client:
      api_key: "your-api-key-here"
      base_url: "https://api.deepseek.com"
    concurrency: 3
```

## Usage

1. **Prepare the Configuration**:
   Edit the `config.yaml` file to add your own `api_key`, `base_url`, `input_file`, and `output_file`.

2. **Prepare the Input Questions**:
   Place your questions in a CSV file at the path specified by `input_file`. The CSV should have **only one** column named `question`.

3. **Run the Script**:
   Execute the script to start collecting model answers:

   ```bash
   python batch_pull_answer.py
   ```

4. **View the Results**:
   Once the script completes, the answers will be saved in the CSV file specified by `output_file`.

## Example

An example flow could look like:

1. Questions in `input/questions.csv`.
2. Results saved in `output/answers.csv`.

## Plan & problems

1. Currently, the process bars presented by `tqdm` have some issue, due to the async pulling.
2. Currently, do not support multi-input files, and the csv format is constraint.
3. Currently, the output file will be saved in `over-write` mode only. Be careful about this.
## License

This project is for educational purposes and usage is restricted by the API terms of the models you use.
