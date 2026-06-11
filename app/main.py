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
            "Read `./improv.md` you task is to select one feature. Nothing more.",
            "Try to describe the choosen feautre in `./work.md`, do not implement anything."
            ],model="gemma4:12b")
        commit("bot - step created")
        run_prompt_sequence(prompts=[
            "Open `./work.md`, read it carefully, and carry out the tasks described inside.",
            ],model="gemma4:12b")
        commit("bot - improved")
        run_prompt_sequence(prompts=[
            "review the code and described what can be improved, persist it in `./improv.md`",
            ],model="gemma4:12b")
        commit("bot - reviewed")
