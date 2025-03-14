from pytubefix import YouTube
import re
from dotenv import load_dotenv
import os
from openai import OpenAI


load_dotenv()

def sanitize_filename(filename):

    title = re.sub(r'[<>:"/\\|?*]', '', filename)
    title = title.replace(" ", "_")
    title = title.strip().replace(' ', '_')
    
    return title # "".join(c if c.isalnum() or c in " ._-" else "_" for c in filename)


def get_audio_from_youtube_video(youtube_url, path):
    
    try:
        yt = YouTube(youtube_url)
        print('Título:', yt.title)
        print('Visualizações:', yt.views)
        yd = yt.streams.get_audio_only()
        yt_title = sanitize_filename(yt.title)
        audio_filename = f'{yt_title}.mp3'
        yd.download(output_path=path, filename=audio_filename)
        print('Download de áudio concluído')
        return audio_filename
    except Exception as e:
        print(f"Erro: {e}")


def transcribe_audio_with_whisper(audio_path, idioma):

     # Verifica se o arquivo existe
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"O arquivo {audio_path} não foi encontrado")

    prompt_base = f"""
    Este é um áudio de um vídeo do YouTube. 
    Transcreva com precisão, mantendo a pontuação adequada.
    O idioma principal é {idioma}.
    Mantenha as expressões coloquiais e gírias quando apropriado.
    Diferencie entre múltiplos falantes quando possível.
    Ignore sons de fundo, música ou ruídos.
    Preserve termos técnicos, nomes próprios e marcas mencionadas.
    """

    audio_file = open(audio_path, "rb")
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        response_format="text",
        prompt = prompt_base,
        file=audio_file
    )

    criar_arquivo_texto(audio_filename + "_transcription", transcript, path)

    return transcript


def criar_arquivo_texto(nome_arquivo, conteudo, path):
    try:
        with open(path+"/"+nome_arquivo, 'w', encoding='utf-8') as arquivo:
            arquivo.write(conteudo)
        print(f"Arquivo '{nome_arquivo}' criado com sucesso!")
    except Exception as e:
        print(f"Erro ao criar o arquivo: {e}")


def sumarizar_video_with_ai(audio_filename,transcription, path):
    
    prompt_base = f"""
    # Prompt para Sumarização de Transcrições

    Você está analisando uma transcrição de um vídeo do YouTube. Crie um resumo conciso e informativo seguindo estas diretrizes:

    ## Contexto
    Esta é a transcrição de um vídeo que precisa ser resumida em seus pontos mais relevantes. Mantenha a essência do conteúdo enquanto reduz significativamente seu tamanho.

    ## Instruções de Sumarização
    1. Identifique o tema principal e o objetivo do conteúdo
    2. Extraia os pontos-chave e argumentos centrais 
    3. Preserve informações factuais importantes (dados, estatísticas, datas)
    4. Mantenha citações impactantes ou exemplos ilustrativos essenciais
    5. Organize o resumo em uma estrutura lógica (introdução, desenvolvimento, conclusão)
    6. Elimine repetições, exemplos redundantes e digressões
    7. Preserve terminologia técnica relevante e conceitos específicos do tema
    8. Mantenha o tom do autor original (formal, educativo, conversacional)

    ## Formato do Resumo
    - Título: Crie um título descritivo baseado no conteúdo
    - Resumo: 2-3 parágrafos que capturam a essência do conteúdo
    - Tópicos principais: Liste de 3-5 pontos fundamentais abordados
    - Conclusões/Insights: 1-2 parágrafos com as principais conclusões

    ## Observações Adicionais
    - Se houver múltiplos falantes, preserve quem disse o quê em pontos críticos
    - Se for um tutorial ou conteúdo educacional, mantenha os passos essenciais
    - Se contiver debate ou opiniões divergentes, apresente as principais perspectivas
    - Indique se há chamadas para ação importantes no final do vídeo
    """

    messages=[
        {"role": "system", "content": prompt_base},
        {"role": "user", "content": transcription},
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature = 1,
        max_tokens = 800
    )

    sumarization = response.choices[0].message.content
    # print(sumarization)
    criar_arquivo_texto(audio_filename + "_sumarization", sumarization, path)

youtube_url = "https://www.youtube.com/watch?v=J4ELMYEGVS0"
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key = api_key)

path = os.getcwd() + "/from_ytb_videos"

audio_filename =  get_audio_from_youtube_video(youtube_url, path)

transcription = transcribe_audio_with_whisper(path + "/" + audio_filename, "PT-BR")
sumarization = sumarizar_video_with_ai(audio_filename, transcription, path)







'''Funções que não estão sendo usadas mas quem sabe eu nao uso um dia

def high(youtube_url, path):
    try:
        yt = YouTube(youtube_url)
        print('Título:', yt.title)
        print('Visualizações:', yt.views)
        yt_title = sanitize_filename(yt.title)

        # Baixa o vídeo de maior resolução com um nome de arquivo especificado
        video_stream = yt.streams.filter().order_by("resolution").last()
        audio_stream = yt.streams.get_audio_only()

        video_filename = f'{yt_title}.mp4'
        audio_filename = f'{yt_title}.mp3'

        video_stream.download(output_path=path, filename=video_filename)
        audio_stream.download(output_path=path, filename=audio_filename)

        print('Download de vídeo e áudio de alta resolução concluído')

    except Exception as e:
        print(f"Erro: {e}")


def low(youtube_url, path):
    try:
        yt = YouTube(youtube_url)
        print('Título:', yt.title)
        print('Visualizações:', yt.views)
        yd = yt.streams.get_lowest_resolution()
        yt_title = sanitize_filename(yt.title)
        yd.download(output_path=path, filename=f'{yt_title}.mp4')
        print('Download de vídeo de baixa resolução concluído')
    except Exception as e:
        print(f"Erro: {e}")
'''

