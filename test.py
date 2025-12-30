# from openai import OpenAI
#
# # Replace with your actual API key
# client = OpenAI(api_key="sk-proj-VwTYgACukwJ7Erp5unKIT3BlbkFJwClnWksCSVGV7qdYmPoE")
#
# try:
#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[{"role": "user", "content": "Hello, are you working?"}]
#     )
#     print("API is working! Response:")
#     print(response.choices[0].message.content)
# except Exception as e:
#     print("API call failed:", e)

from shiny import App, ui, render

app_ui = ui.page_fluid(
    ui.tags.script(src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"),
    ui.input_action_button("screenshot", "Take Screenshot"),
    ui.div({"id": "capture_area"},
        ui.h3("This will be captured!"),
        ui.p("Some text inside the Shiny app.")
    ),
    ui.tags.script(
        """
        document.getElementById("screenshot").onclick = function() {
            html2canvas(document.getElementById("capture_area")).then(function(canvas) {
                var link = document.createElement("a");
                link.download = "screenshot.png";
                link.href = canvas.toDataURL();
                link.click();
            });
        };
        """
    )
)

def server(input, output, session):
    pass

app = App(app_ui, server)
