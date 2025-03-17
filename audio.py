import os
import subprocess
import pandas as pd
import yt_dlp 

audio_dir = 'audio'
if not os.path.exists(audio_dir):
    os.makedirs(audio_dir)

for year in range(1956, 2023):
    contestants = pd.read_csv('contestants.csv')
    contestants = contestants[contestants["year"] == year]

    for i, r in contestants.iterrows():
        destination_dir = os.path.join(audio_dir, str(r['year']))
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)

        youtube_url = r['youtube_url']
        if youtube_url:
            fn = '{}_{}_{}'.format(
                r['to_country'], r['song'], r['performer'])

            # Skip if file already exists
            fp = os.path.join(destination_dir, fn)
            if not os.path.exists(fp + '.mp3'):

                ydl_opts = {
                    'outtmpl': fp + '.%(ext)s',
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '320',
                    }],
                    'ffmpeg_location': r'C:\Users\Robin Khatiri\Downloads\ffmpeg-2025-03-17-git-5b9356f18e-full_build\bin'
                }

                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([youtube_url])
                except Exception as e:
                    print(e)
                    pass
            else:
                print('{} already exists'.format(fp))
            

            # studio_rec_dir = os.path.join(destination_dir, "studio_recording")
            # if not os.path.exists(studio_rec_dir):
            #     os.makedirs(studio_rec_dir)
            
            # # Additionally, try non-live versions:
            # query = f"{r['song']} {r['performer']}"
            # subprocess.call(["spotdl", "-f", studio_rec_dir, "--song", query])