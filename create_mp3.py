import edge_tts
import asyncio

async def create_mp3():
    text = "I couldn't hear what you said. Please repeat"
    voice = "en-US-EricNeural"
    output_file = "repeat_request.mp3"
    
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)
    
    print(f"MP3 file created: {output_file}")

if __name__ == "__main__":
    asyncio.run(create_mp3())