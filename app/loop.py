from sven.chat import interactive_chat
from sven.task import run_prompt_sequence
from sven.tools.git.commit import commit
from sven.tools.python.compilefiles import compilefiles

if __name__ == "__main__":
    commit("start the sprint")
    for i in range(1, 24):
        with open("todo.md", 'r', encoding='utf-8') as file:
            todo = file.read()
        print(f"sprint {i}")
        run_prompt_sequence(prompts=[
            f"""
            TODOS:
            ```
            {todo}
            ```

            Choose one todo.
            """,
            "Implement the selected TODO.",
            "Rewrite the todo file. Create new features."
            ],model="gemma4:12b")
        commit("bot")
        comiler = compilefiles()
        run_prompt_sequence(prompts=[
            f"""
            compileroutput:
            {comiler}
            If there are errors fix them
            """
            ],model="gemma4:12b")
        commit("bot - fixes")
