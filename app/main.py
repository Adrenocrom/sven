from sven.chat import interactive_chat
from sven.task import run_prompt_sequence
from sven.tools.git.commit import commit

if __name__ == "__main__":
    # You can change the model name or tweak options here
    #interactive_chat(model="gemma4:12b")
    # Or you can use a prompt sequence to run multiple tasks in sequence
    commit("start the sprint")
    for i in range(1, 10):
        print(f"sprint {i}")
        run_prompt_sequence(prompts=[
            "check for existing errors. List them",
            "fix errors.",
            ],model="gemma4:12b")
        commit("bot - fixed")
        run_prompt_sequence(prompts=[
            "review the code",
            "read `improv.md`"
            "implement only one improvement."
            "review the code, and rewrite the `improv.md`, remove already implemented feature and add new ones."
            ],model="gemma4:12b")
        commit("bot - improved")
