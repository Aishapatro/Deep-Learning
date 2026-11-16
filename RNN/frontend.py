
import re
import gradio as gr
import pywhatkit as kit
import speech_recognition as sr


# 1. Convert voice into text
def transcribe_audio(audio_path):

    if not audio_path:
        return ""

    recognizer = sr.Recognizer()

    try:
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)

        return recognizer.recognize_google(audio_data)

    except sr.UnknownValueError:
        return "Error: Could not understand audio."

    except sr.RequestError as e:
        return f"Error: Speech recognition service failed ({e})."

    except Exception as e:
        return f"Error: {str(e)}"


# 2. Execute voice or text commands
def execute_command(audio_path, text_override, phone_number, image_path):

    # Determine command source
    if audio_path:
        command = transcribe_audio(audio_path)
    else:
        command = (text_override or "").strip()

    if not command or command.startswith("Error:"):
        return command or "No voice or text command provided."

    cmd_lower = command.lower()

    try:

        # 3. Play YouTube video
        if cmd_lower.startswith("play "):

            query = command[5:].strip()

            if not query:
                return "Error: Please provide a YouTube search query."

            kit.playonyt(query)

            return f"Command: {command}\nAction: Playing {query} on YouTube."

        # 4. Send WhatsApp image
        elif "send image" in cmd_lower or "send photo" in cmd_lower:

            if not phone_number or not image_path:
                return (
                    f"Command: {command}\n"
                    "Error: Please provide a phone number and upload an image."
                )

            caption_match = re.search(
                r"(?:saying|with caption|caption)\s+(.+)",
                command,
                re.IGNORECASE
            )

            caption = caption_match.group(1) if caption_match else ""

            kit.sendwhats_image(
                receiver=phone_number.strip(),
                img_path=image_path,
                caption=caption,
                tab_close=True
            )

            return (
                f"Command: {command}\n"
                f"Action: WhatsApp image sending initiated for {phone_number}."
            )

        # 5. Send WhatsApp text message
        elif (
            cmd_lower.startswith("send message")
            or cmd_lower.startswith("whatsapp")
            or cmd_lower.startswith("message")
        ):

            if not phone_number:
                return (
                    f"Command: {command}\n"
                    "Error: Please enter a phone number with country code."
                )

            message_body = re.sub(
                r"^(send message|whatsapp|message)\s*(saying|that|to)?\s*",
                "",
                command,
                flags=re.IGNORECASE
            ).strip()

            if not message_body:
                return (
                    "Error: Message content not found.\n"
                    "Try: Send message Hello there"
                )

            kit.sendwhatmsg_instantly(
                phone_no=phone_number.strip(),
                message=message_body,
                tab_close=True
            )

            return (
                f"Command: {command}\n"
                f"Action: WhatsApp message sending initiated.\n"
                f"Message: {message_body}\n"
                f"Recipient: {phone_number}"
            )

        # 6. Unknown command
        return (
            f"Transcribed: {command}\n"
            "Unrecognized command.\n"
            "Try Play..., Send message..., or Send image..."
        )

    except Exception as e:
        return f"Error while executing command: {str(e)}"


# 7. Build Gradio interface
with gr.Blocks(title="Voice Assistant") as demo:

    gr.Markdown("## 🎙️ Voice-Controlled YouTube & WhatsApp Assistant")

    gr.Markdown(
        """
        **Voice Commands:**

        - Play lo-fi hip hop
        - Send message I will be 10 minutes late
        - Send image saying Check this out
        """
    )

    with gr.Row():

        audio_input = gr.Audio(
            sources=["microphone"],
            type="filepath",
            label="Speak Command"
        )

        with gr.Column():

            phone_input = gr.Textbox(
                label="Recipient Phone Number",
                placeholder="+919876543210"
            )

            image_input = gr.Image(
                type="filepath",
                label="Image to Send"
            )

            text_fallback = gr.Textbox(
                label="Or Type Command Manually",
                placeholder="Play shape of you"
            )

    run_btn = gr.Button("Execute Command", variant="primary")

    output_log = gr.Textbox(
        label="Status & Transcription",
        interactive=False
    )

    run_btn.click(
        fn=execute_command,
        inputs=[
            audio_input,
            text_fallback,
            phone_input,
            image_input
        ],
        outputs=output_log
    )


# 8. Launch application
if __name__ == "__main__":
    demo.launch()
