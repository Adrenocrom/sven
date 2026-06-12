from sven.chat import interactive_chat
from sven.task import run_prompt_sequence
from sven.tools.git.commit import commit
from sven.tools.python.compilefiles import compilefiles

if __name__ == "__main__":
    commit("start the sprint")
    for i in range(1, 24):
        print(f"sprint {i}")
        run_prompt_sequence(prompts=[
            """
            In the file `todo.md` new features are listed.
            Choose ONE feature and implement it.
            Compile all files and fix occuring errors.
            Rewrite the `todo.md` and add new features.
            """
            ],model="gemma4:12b")
        commit("bot")
