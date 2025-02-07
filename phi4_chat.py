import transformers
import yaml



# json = {
#     "dragon_taming": "type 3",
#     "castle_building": "type 4",
#     "alchemy_basics": "type 5"
# }

# with open("template.yaml", "r", encoding="utf-8") as file:
#     yaml_data = yaml.safe_load(file)
#     system_content = yaml_data["background"]["content"]
#     # template_dict["examples"].update(json)

# 将更新后的模板转回 YAML 格式
# updated_template = yaml.dump(template_dict, default_flow_style=False)
 

class Phi4:
    def __init__(self,system_content):
        self.pipeline = transformers.pipeline(
                "text-generation",
                model="microsoft/phi-4",
                model_kwargs={"torch_dtype": "auto"},
                device_map="mps",
            )
        self.system_content = system_content

    def __call__(self, prompt, system_content=None):
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt},
        ]
        outputs = self.pipeline(messages, max_new_tokens=128)

        return(outputs[0]["generated_text"][-1])
