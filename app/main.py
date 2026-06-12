from sven.chat import interactive_chat
from sven.task import run_prompt_sequence
from sven.tools.git.commit import commit
from sven.tools.python.compilefiles import compilefiles

if __name__ == "__main__":
    # You can change the model name or tweak options here
    interactive_chat(model="gemma4:12b")
