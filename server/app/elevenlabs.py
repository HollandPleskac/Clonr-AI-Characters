import os

from elevenlabs import clone, generate, play, set_api_key

from .gcp import (client, create_bucket, get_blob, get_bucket, list_blobs,
                  upload_blob)

ELEVEN_LABS_API_KEY = os.environ.get("ELEVEN_LABS_API_KEY")
set_api_key(ELEVEN_LABS_API_KEY)


def clone_from_audio(user_id, user_name):
    # bucket_name is user_id
    bucket = client.get_bucket(user_id)
    blobs = bucket.list_blobs()

    temp_dir = "/tmp/audio_files"
    os.makedirs(temp_dir, exist_ok=True)

    for blob in blobs:
        file_path = os.path.join(temp_dir, blob.name.split("/")[-1])
        blob.download_to_filename(file_path)

    cloned_voices = []
    for file_name in os.listdir(temp_dir):
        file_path = os.path.join(temp_dir, file_name)

        voice = clone(
            name=user_name,
            description="An old American male voice with a slight hoarseness in his throat. Perfect for news",  # Optional
            files=[file_path],
        )

        # audio = generate(text="Hello world!", voice=voice)
        # play(audio)
        cloned_voices.append(voice)

    for file_name in os.listdir(temp_dir):
        file_path = os.path.join(temp_dir, file_name)
        os.remove(file_path)
    os.rmdir(temp_dir)

    return {"cloned_voices": cloned_voices}
