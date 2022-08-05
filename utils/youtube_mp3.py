import youtube_dl

def downloadYTmp3(link, target):
    # download options for youtube_dl
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': target,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])

