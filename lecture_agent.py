from pydantic import BaseModel, Field
import time
from typing import List
import wget

import dspy

dspy.settings.configure(lm=dspy.OpenAI(model="gpt-4-0125-preview", max_tokens=2048))

from dspy import Signature, InputField, OutputField
from dspy.functional import TypedPredictor

from openai import OpenAI

client = OpenAI()


class AIImage(BaseModel):
    """A single generated image."""

    prompt: str = Field(desc="The prompt used to generate the image.")
    url: str = Field(
        desc="The URL of the generated image.", default="./img/placeholder.webp"
    )


class Slide(BaseModel):
    """A single slide in a lecture."""

    thoughts: str = Field(desc="A summary of your thoughts as you prepare the slide.")
    title: str = Field(desc="The slide's title.")
    bullets: List[str] = Field(
        desc="Up to 5 bullet points of concise, relevant content."
    )
    speaking_notes: List[str] = Field(
        desc="Detailed notes to support each bullet point, based on the raw notes."
    )

    image: AIImage = Field(desc="A nice AI generated image to accompany the slide.")
    python_code_example: str = Field(
        desc="An optional Python code example to include in the slide.", default=None
    )

    def to_html(self):
        html_output = f'<h2>{self.title}</h2><table><tr><td><img src="{self.image.url}" width="400" alt="{self.image.prompt}"></td><td>'
        for bullet, note in zip(self.bullets, self.speaking_notes):
            html_output += f"<li>{bullet}</li>"
            if note:
                html_output += f"<p><small>{note}</small></p>"
        if self.python_code_example:
            html_output += f"<pre><code>{self.python_code_example}</code></pre>"
        html_output += "</td></tr></table><hr>"
        return html_output


class Lecture(BaseModel):
    """A complete lecture with a title, description, and content."""

    thoughts: str = Field(desc="A summary of your thoughts as you prepare the lecture.")
    title: str = Field(desc="The lecture's title.")
    description: str = Field(desc="A brief description of the lecture.")
    slides: List[Slide] = Field(desc="The slides that make up the lecture.")

    def to_html(self):
        html_output = f"<h1>{self.title}</h1><p>{self.description}</p><hr>"
        for slide in self.slides:
            html_output += slide.to_html()
        return html_output


class LectureCreator(Signature):
    """Create content for a great lecture."""

    lecture_subject: str = InputField(desc="The subject of the lecture.")
    raw_notes: str = InputField(desc="Unstructured, raw notes that can be used as the basis for the lecture.", default="")
    custom_instructions: str = InputField(desc="Specific additional instructions to consider.", default="")
    lecture_content: Lecture = OutputField(desc="The complete lecture content.")


def create_my_lecture(subject: str, raw_notes: str, instructions: str = ""):
    lecture_creator = TypedPredictor(LectureCreator)
    lecture = lecture_creator(
        lecture_subject=subject,
        raw_notes=raw_notes,
        custom_instructions=instructions,
    )
    for slide in lecture.lecture_content.slides:
        prompt = slide.image.prompt
        print(f"Calling OpenAI to generate an image for the prompt: {prompt}")
        for _ in range(3):
            try:
                # Call OpenAI to generate the image
                dalle_response = client.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    size="1024x1024",
                    quality="standard",
                    n=1,
                )
                # Download and save it
                image_url = dalle_response.data[0].url
                image_filename = wget.download(image_url, out="./img")
                slide.image.url = image_filename
                break
            except Exception as e:
                print(f"Error calling OpenAI: {e}, retrying after 5 seconds...")
                time.sleep(5)
                continue

    # Save the markdown to a file
    with open(f"{subject}_lecture.html", "w") as file:
        file.write(lecture.lecture_content.to_html())

    return lecture


if __name__ == "__main__":
    raw_notes = open("a_raw_notes_file.txt").read()
    # raw_notes = open("de_ai_outline.txt").read()
    lecture_subject = "your lecture subject"
    instructions = """Let's try to create 10 slides in total based on my notes.
    The lecture slides are for a 15-minute talk.
    ...
    """
    create_my_lecture(lecture_subject, raw_notes)
