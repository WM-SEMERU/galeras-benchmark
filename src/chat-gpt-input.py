import openai,os,sys
import json
from dotenv import load_dotenv
import random
import time


load_dotenv()
openai.api_key = os.environ.get('OPENAI_KEY')
chat_completion = openai.ChatCompletion()

def ask_chat_gpt(prompt):

    for delay_secs in (2**x for x in range(0, 6)):
        try:
            messages = [
                {"role": "system", "content": "You are a helpful assistant."}
                ]
        
            messages.append(
                {"role": "user", "content": prompt}
            )
            response = chat_completion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            answer = response.choices[0].message.content
            messages.append({"role": "assistant", "content": answer})
            break
        except openai.OpenAIError as e:
            randomness_collision_avoidance = random.randint(0, 1000) / 1000.0
            sleep_dur = delay_secs + randomness_collision_avoidance
            print(f"Error: {e}. Retrying in {round(sleep_dur, 2)} seconds.")
            time.sleep(sleep_dur)
            continue
        
    return answer, messages
    
        
def code_completion_random_cut():
    answers = list()
    json_path = '/workspaces/chat-gpt-failures/datasets/galeras_se_tasks_dataset/randomsplit.json'
    with open(json_path) as json_file:
        json_data = json.load(json_file)
        
        for data in json_data:
            prompt = "'Complete the following a {} code, return only code and complete method {}'".format('Python', data['random_split'])
            answer, messages= ask_chat_gpt(prompt)
            data['predicted_contorl'] = answer
            answers.append(data)
       
    return answers
    

def codeserchnet_summarizatio_code():
    answers = []
    with open('datasets/code_xglue/text-to-code/codesearchnet/python/valid.jsonl', 'r') as json_file:
        json_list = list(json_file)
    for json_str in json_list:
        result = json.loads(json_str)
        question = result[0]['docstring']
        answers.append(ask_chat_gpt(question))
        
def save(name, data):
    with open('/workspaces/chat-gpt-failures/datasets/galeras_prompting/{}.json'.format(name), 'w') as f:
        print("saving data")
        json.dump(data, f, ensure_ascii=False, indent=4)
        
def main():
    result = code_completion_random_cut()
    save("random_cut",result)

if __name__ == "__main__":
    sys.exit(main())
    
    #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
