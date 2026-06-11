# How to add a webfetch tool based on curl

Follow these steps to implement and integrate the `webfetch` tool:

1. **Define the Tool**: Create a function named `webfetch` that accepts a `url` as an argument.
2. **Implement Fetch Logic**: Use the `curl` command within the function to fetch content from the provided URL.
3. **Handle Output**: Parse the response from curl and return the raw body or formatted text.
4. **Register Tool**: Add the `webfetch` tool definition to your system's configuration file so it can be called by the assistant.
5. **Test Implementation**: Run a test command (e.g., `webfetch("https://google.com")`) to ensure the content is retrieved correctly.
