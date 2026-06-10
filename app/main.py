from sven.chat import interactive_chat
from sven.task import run_prompt_sequence

if __name__ == "__main__":
    # You can change the model name or tweak options here
    #interactive_chat(model="gpt-oss:20b")
    # Or you can use a prompt sequence to run multiple tasks in sequence
    run_prompt_sequence(prompts=[
        "create a the possibility to load a number ob prompt sequences from an md file",
        "check if you persist its results",
        "is there anything you forgot?"
        ],model="gemma4:12b")

