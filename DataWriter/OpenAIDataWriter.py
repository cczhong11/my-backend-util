from DataWriter.DataWriterBase import DataWriterBase
import os
import openai


class OpenAIDataWriter(DataWriterBase):
    def __init__(self, api: str):
        super(OpenAIDataWriter, self).__init__()
        self.client = openai.OpenAI(api_key=api)

    def write_data(self, filename, dst_path, task):
        if task == "whisper":
            single_filename = filename.split("/")[-1]
            single_filename = single_filename.split(".")[0] + ".txt"
            if os.path.exists(os.path.join(dst_path, single_filename)):
                return
            print(filename)
            audio_file = open(filename, "rb")
            # handle too long problem
            transcript = self.client.audio.transcriptions.create(
                "whisper-1", file=audio_file
            )
            audio_file.close()

            with open(os.path.join(dst_path, single_filename), "w") as f:
                f.write(transcript.text)

    def ask_chatgpt(self, prompt, use_16k_model=False):
        model = "gpt-3.5-turbo"
        if use_16k_model:
            model = "gpt-3.5-turbo-16k"
        completion = self.client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": prompt}]
        )

        return completion.choices[0].message.content

    def improve_data(self, text):
        prompt = f"下面一段话是来自语音转文字，里面可能有英语变成了中文，请帮忙理顺，回答时只输出修改后的内容: {text}"
        return self.ask_chatgpt(prompt)

    def suggest_data(self, text):
        prompt = f"下面一段话来自我的日记，请告诉我在哪些方面我可以描述细节和感受，哪些句式可以优化，哪些地方可以反思，回答时用“以下是chatgpt的建议：”开头，之后给出例子。{text}"
        return self.ask_chatgpt(prompt)

    def summary_data(self, context, text, use_16k_model=False):
        prompt = f"{context}。用中文总结下面的内容。{text}"
        return self.ask_chatgpt(prompt, use_16k_model)

    def markdown_data(self, text):
        prompt = f"将下面的话变成markdown格式: {text}"
        return self.ask_chatgpt(prompt)

    def health_check(self) -> bool:
        return True
