from sven.chat import interactive_chat
from sven.task import run_prompt_sequence
from sven.tools.git.commit import commit
from sven.tools.python.compilefiles import compilefiles

if __name__ == "__main__":
    result = compilefiles()
    print(result)
    # You can change the model name or tweak options here
    #interactive_chat(model="gemma4:12b")
    # Or you can use a prompt sequence to run multiple tasks in sequence
    #commit("start the sprint")
    #for i in range(1, 24):
    #    print(f"sprint {i}")
    #    run_prompt_sequence(prompts=[
    #        "`./todo.md` describes what you have to do next. implement the features. Rewrite the todo.md",
    #        ],model="gemma4:12b")
    #    commit("bot")
