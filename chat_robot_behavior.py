from deepseek_r1_chat import deepseekR1
from phi4_chat import Phi4

import json
import yaml
import pandas as pd
from utils import read_interview_txt, read_video_caption_txt, remove_think_part, get_theme, get_theme_description, simplify_classification_task
import json
import os
from datetime import datetime
import argparse




class LLMs:
    def __init__(self, model_type):
        self.model_type = model_type

        if model_type == 'deepseek-r1':
            self.chat = deepseekR1
        elif model_type == 'phi4':
            self.system_content = system_content
            self.chat = Phi4(system_content=system_content)
        else:
            raise NotImplementedError("Unknown llm model type")
        
    def ask(self, prompts):
        return self.chat(prompts)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    if args.debug:
        log_dir = "LOGS/debug/"
    else:
        log_dir = "LOGS/"
    log_filename = os.path.join(log_dir, datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    os.makedirs(log_filename, exist_ok=True)

    with open("behavior_template.yaml", "r", encoding='utf-8') as yaml_file:
        behavior_template = yaml.safe_load(yaml_file)



    df = pd.read_csv("questionnaire/data/qualtrics.csv", header=[0, 1, 2])  # 读取前两行作为多级索引

    labels = df.columns.get_level_values(0).tolist() 
    questions = df.columns.get_level_values(1).tolist() 
    result = {}
    test_question = {}
    test_labels = ["Q2_", "Q2-", "Q3","Q4","Q5","Q6","Q7","Q8","Q9","Q10","Q11","Q12"]
    examples_labels = ["Q2_", "Q2-"]
    video_labels = "Q14-主题"
    use_examples = False
    classification_number = 2
    

    for index, row in df.iterrows():  
        respondent_examples_str = ""
        respondent_id = row["Q15"].iloc[0] 
        respondent_answers = {
            labels[i]: {"question": questions[i], "answer": row[i]} 
            for i in range(len(labels)) if labels[i] != "Q15"
        }
        test_question[respondent_id] = []
        for i in range(len(labels)):
            for test_label in test_labels:
                if labels[i].startswith(test_label):
                    test_question[respondent_id].append({
                                "question": questions[i],
                                "answer":  simplify_classification_task(classification_number, row[i]) if classification_number != 6 else row[i]
                            })
        # print(test_question)
        for i in range(len(labels)):
            for example_label in examples_labels:
                if labels[i].startswith(example_label):
                    respondent_examples_str += behavior_template['EXAMPLE_TEMPLATE'].format(question=questions[i],answer=row[i])
        interview_text = read_interview_txt('questionnaire/text/' + str(respondent_id).zfill(3) + '.txt')
        
        result[respondent_id] = {
            "respondent_answers": respondent_answers,
            "interview_text": interview_text,
            "respondent_examples_str": respondent_examples_str
        }
    # print(result)
    questions = ''
    video_caption = ['','']
    chat_robot = LLMs(model_type='deepseek-r1')
    

    if use_examples == True:
        for respondent_id, data_dict in result.items():
            behavior_prompt = behavior_template["BEHAVIOR_WITH_EXAMPLES_TEMPLATE"]
            behavior_prompt = behavior_prompt.format(
                gender=data_dict["respondent_answers"]["Q16"]['answer'],
                ages=data_dict["respondent_answers"]["Q17"]['answer'],
                background = questions+data_dict["interview_text"], 
                video_caption_A=video_caption[0],
                video_caption_B=video_caption[1],
                examples=data_dict["respondent_examples_str"])
            print(behavior_prompt)
    else:
        for respondent_id, data_dict in result.items():
            summarize_prompt = behavior_template["SUMMARIZE_TEMPLATE"]
            summarize_prompt = summarize_prompt.format(
                gender=data_dict["respondent_answers"]["Q16"]['answer'],
                ages=data_dict["respondent_answers"]["Q17"]['answer'],
                background=data_dict["interview_text"])
            # print(summarize_prompt)
            # print("[INFO] Waiting response!!")
            interview_text = chat_robot.ask(summarize_prompt)
            # print("interview",interview_text)
           
            # 短视频预测
            with open(log_filename + "/" + str(respondent_id).zfill(3) + "_VIDEO.json", "a", encoding="utf-8") as f:
                for i in range(len(labels)):
                    if labels[i].startswith(video_labels): # Qxx-xxx
                        # respondent_examples_str += behavior_template['EXAMPLE_TEMPLATE'].format(question=questions[i],answer=row[i])
                        behavior_prompt = behavior_template["BEHAVIOR_WITHOUT_EXAMPLES_TEMPLATE"]
                        behavior_prompt = behavior_prompt.format(
                            gender=data_dict["respondent_answers"]["Q16"]['answer'],
                            ages=data_dict["respondent_answers"]["Q17"]['answer'],
                            background= questions+data_dict["interview_text"], 
                            theme_description=get_theme_description(labels[i].split("主题")[-1]),
                            theme=get_theme(labels[i].split("主题")[-1]),
                            video_caption_A=read_video_caption_txt("./video_caption/" +labels[i].split("-")[-1].replace("主题","theme_")+ "_A.txt"),
                            video_caption_B=read_video_caption_txt("./video_caption/" +labels[i].split("-")[-1].replace("主题","theme_")+ "_B.txt"))
                        print("[INFO] Waiting response for participant " + str(respondent_id).zfill(3) + " on VIDEO Task theme " + labels[i] +"!!")
                        response = chat_robot.ask(behavior_prompt)

                        log_data = {
                            "respondent_id": respondent_id,
                            "label": labels[i],
                            "response": response,
                            "real": data_dict["respondent_answers"][labels[i]]['answer'],
                            "predicted": remove_think_part(response)
                        }
                        json.dump(log_data, f, ensure_ascii=False, indent=4)
                        f.write("\n")

            # 基础偏好预测   
            with open(log_filename + "/" + str(respondent_id).zfill(3) + "_QUESTION.json", "a", encoding="utf-8") as f:
                for question_and_answer in test_question[respondent_id]:
                    # print(question_and_answer)
                    question_prompt = behavior_template["SELF_TEMPLATE"]
                    question_prompt = question_prompt.format(
                        gender=data_dict["respondent_answers"]["Q16"]['answer'],
                        ages=data_dict["respondent_answers"]["Q17"]['answer'],
                        background= questions+data_dict["interview_text"],
                        question=question_and_answer["question"])
                    # print(question_prompt)
                    # print("[INFO] waiting response!!")
                    print("[INFO] Waiting response for participant " + str(respondent_id).zfill(3) + " on BASIC Task!!")
                    response = chat_robot.ask(question_prompt)
                    log_data = {
                            "respondent_id": respondent_id,
                            "label": question_and_answer["question"],
                            "response": response,
                            "real": question_and_answer["answer"],
                            "predicted": remove_think_part(response)
                        }
                    json.dump(log_data, f, ensure_ascii=False, indent=4)
                    f.write("\n")

    # background_information = yaml.dump(background_information, default_flow_style=False, allow_unicode=True)
    # print(background_information)


    
