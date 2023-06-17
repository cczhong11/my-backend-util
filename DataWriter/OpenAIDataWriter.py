from DataWriter.DataWriterBase import DataWriterBase
import os
import openai


class OpenAIDataWriter(DataWriterBase):
    def __init__(self, api: str):
        super(OpenAIDataWriter, self).__init__()
        openai.api_key = api

    def write_data(self, filename, dst_path, task):
        if task == "whisper":
            single_filename = filename.split("/")[-1]
            single_filename = single_filename.split(".")[0] + ".txt"
            print(filename)
            audio_file = open(filename, "rb")
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
            audio_file.close()
            if os.path.exists(os.path.join(dst_path, single_filename)):
                return
            with open(os.path.join(dst_path, single_filename), "w") as f:
                f.write(transcript.text)

    def improve_data(self, text):
        prompt = f"下面一段话是来自语音转文字，里面可能有英语变成了中文，请帮忙理顺，回答时只输出修改后的内容: {text}"
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}]
        )

        return completion.choices[0].message.content

    def health_check(self) -> bool:
        return True
