# Streaming Markdown Rendering with Rich

Rich can render markdown **while** you receive the content (e.g., from a network request, a subprocess, or any generator). This is useful when you don't want to wait for the entire payload before displaying it.

## 1. Basic idea

```python
from rich.console import Console
from rich.markdown import Markdown

console = Console()

# Imagine `stream` yields chunks of a markdown document (bytes or str)
for chunk in stream():
    # Convert each chunk to a `Markdown` object and print it.
    # The console will keep the previously printed content.
    console.print(Markdown(chunk))
```

The console automatically maintains the cursor, so each call appends to the existing output.

## 2. Streaming from an async source

If you are using `asyncio` (for example, reading from an async HTTP response):

```python
import asyncio
from rich.console import Console
from rich.markdown import Markdown
from aiohttp import ClientSession

async def stream_markdown(url: str):
    console = Console()
    async with ClientSession() as session:
        async with session.get(url) as resp:
            async for line in resp.content.iter_any():
                # Decode bytes → str, then render
                console.print(Markdown(line.decode()))

asyncio.run(stream_markdown("https://raw.githubusercontent.com/.../README.md"))
```

## 3. Handling partial markdown blocks

When a chunk ends in the middle of a markdown construct (e.g., a code‑block), the `Markdown` parser will treat the incomplete part as plain text. To keep the visual fidelity you can buffer incomplete sections:

```python
buffer = ""
for chunk in stream():
    buffer += chunk
    # Simple heuristic: render when we see a double newline (end of a paragraph)
    if "\n\n" in buffer:
        console.print(Markdown(buffer))
        buffer = ""
# Render any remainder
if buffer:
    console.print(Markdown(buffer))
```

## 4. Using `Live` for live‑updating panels

Rich’s `Live` class can be used when you want to *replace* the previously rendered markdown (e.g., a progress log):

```python
from rich.live import Live
from rich.markdown import Markdown
from rich.console import Console
import time

console = Console()
with Live(refresh_per_second=4) as live:
    md = ""
    for i in range(5):
        md += f"## Step {i+1}\n\nProgress…\n\n"
        live.update(Markdown(md))
        time.sleep(1)
```

## 5. Full example – streaming from `git log`

```python
import subprocess
from rich.console import Console
from rich.markdown import Markdown

console = Console()
proc = subprocess.Popen(["git", "log", "--oneline"], stdout=subprocess.PIPE, text=True)

for line in proc.stdout:
    # Treat each line as a markdown list item
    console.print(Markdown(f"- {line.strip()}"))
```

## 6. Tips & Gotchas

| Situation | Recommendation |
|-----------|----------------|
| Very large markdown files | Buffer and render per paragraph or per section to avoid excessive memory usage. |
| Need to preserve scrolling position | Use `console.print(..., end="")` when you want to stream without adding extra newlines. |
| Want to update the same area (e.g., a progress bar) | Use `Live` as shown in Section 4. |

---

With these patterns you can integrate Rich’s markdown rendering into any streaming pipeline, giving your users a rich, colour‑coded, and instantly visible experience.
