import openai
import os

class OpenAILib:
    def __init__(self, api_key=os.getenv("OPENAI_API_KEY")):
        openai.api_key = api_key
        self.model = "gpt-3.5-turbo"

    def transcribe_audio(self, audio_file):
        transcription = openai.Audio.transcribe("whisper-1", audio_file)
        return transcription['text']

    def meeting_minutes(self, transcription):
        abstract_summary = self.__abstract_summary_extraction(transcription)
        key_points = self.__key_point_extraction(transcription)
        action_items = self.__action_item_extraction(transcription)
        sentiment = self.__sentiment_analysis(transcription)
        return {
            'abstract_summary': abstract_summary,
            'key_points': key_points,
            'action_items': action_items,
            'sentiment': sentiment
        }

    def __abstract_summary_extraction(self, transcription):
        response = openai.ChatCompletion.create(
            model=self.model,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": "You are a highly skilled AI trained in language comprehension and summarization. I would like you to read the following text and summarize it into a concise abstract paragraph. Aim to retain the most important points, providing a coherent and readable summary that could help a person understand the main points of the discussion without needing to read the entire text. Please avoid unnecessary details or tangential points. And you should make response message in japanese."
                },
                {
                    "role": "user",
                    "content": transcription
                }
            ]
        )
        return response['choices'][0]['message']['content']


    def __key_point_extraction(self, transcription):
        response = openai.ChatCompletion.create(
            model=self.model,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": "You are a proficient AI with a specialty in distilling information into key points. Based on the following text, identify and list the main points that were discussed or brought up. These should be the most important ideas, findings, or topics that are crucial to the essence of the discussion. Your goal is to provide a list that someone could read to quickly understand what was talked about. And you should make response message in japanese."
                },
                {
                    "role": "user",
                    "content": transcription
                }
            ]
        )
        return response['choices'][0]['message']['content']

    def __action_item_extraction(self, transcription):
        response = openai.ChatCompletion.create(
            model=self.model,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI expert in analyzing conversations and extracting action items. Please review the text and identify any tasks, assignments, or actions that were agreed upon or mentioned as needing to be done. These could be tasks assigned to specific individuals, or general actions that the group has decided to take. Please list these action items clearly and concisely. And you should make response message in japanese."
                },
                {
                    "role": "user",
                    "content": transcription
                }
            ]
        )
        return response['choices'][0]['message']['content']

    def __sentiment_analysis(self, transcription):
        response = openai.ChatCompletion.create(
            model=self.model,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": "As an AI with expertise in language and emotion analysis, your task is to analyze the sentiment of the following text. Please consider the overall tone of the discussion, the emotion conveyed by the language used, and the context in which words and phrases are used. Indicate whether the sentiment is generally positive, negative, or neutral, and provide brief explanations for your analysis where possible. And you should make response message in japanese."
                },
                {
                    "role": "user",
                    "content": transcription
                }
            ]
        )
        return response['choices'][0]['message']['content']
