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
            "read `improv.md`"
            "choose one feature you want to implement"
            "implement the feature"
            "compile the code you chaged"
            "compile the code"
            "review the changes, refine `improv.md` and add new feautures."
            ],model="gemma4:12b")
        commit("bot - improved")
