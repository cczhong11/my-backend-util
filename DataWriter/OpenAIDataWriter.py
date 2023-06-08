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
            with open(os.path.join(dst_path, single_filename), "w") as f:
                f.write(transcript.text)

    def health_check(self) -> bool:
        return True
