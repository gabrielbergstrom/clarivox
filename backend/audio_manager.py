import sounddevice as sd
import numpy as np
import time
import threading
from collections import deque
import speech_recognition as sr
import soundfile as sf
import torch
import torchaudio

# configurações gerais
sample_rate = 16000  # taxa de amostragem do áudio
frame_duration = 0.02  # duração de cada bloco de áudio em segundos
frame_size = int(sample_rate * frame_duration)  # tamanho do bloco em amostras
ganho = 5  # amplificação do áudio
balanco = 0.0  # -1.0 é só no fone esquerdo, 0.0 neutro, 1.0 é só no direito
memoria_segundos = 5  # quanto tempo de áudio fica guardado
reconhecimento_segundos = 2  # quanto tempo de áudio é usado pra transcrição
buffer_maximo = int(memoria_segundos / frame_duration)  # quantos blocos cabem na memória
buffer_reconhecimento = int(reconhecimento_segundos / frame_duration)  # blocos usados pra reconhecer
memoria_audio = deque(maxlen=buffer_maximo)  # fila que guarda os blocos de áudio
executando = False  # se tá gravando ou não
palavra_chave = ["pietro"]  # palavra que dispara o alerta
stream = None  # stream de áudio
stream_lock = threading.Lock()  # trava pra mexer no stream com segurança
threads_iniciados = False  # pra não iniciar as threads mais de uma vez

# detector de voz silero
torch.set_num_threads(1)
model, utils = torch.hub.load('snakers4/silero-vad', 'silero_vad', trust_repo=True)
(get_speech_timestamps, _, _, _, _) = utils
falando = False  # se o usuário está falando
silencio_contador = 0
silencio_limite = int(0.3 / frame_duration)  # 300ms de silêncio
buffer_vad = deque(maxlen=int(0.5 / frame_duration))  # 0.5s de áudio para VAD

# função que aplica o ganho e o balanço nos canais
def aplicar_ganho_balanco(indata):
    # se o áudio vier mono, duplica pra virar estéreo
    if indata.shape[1] == 1:
        indata = np.repeat(indata, 2, axis=1)
    # aplica o ganho e limita pra não estourar
    audio = np.clip(indata * ganho, -1.0, 1.0)
    # calcula quanto vai pro canal esquerdo e direito com base no balanço
    esquerda = 1.0 - max(0.0, balanco)
    direita = 1.0 - max(0.0, -balanco)
    # aplica o balanço nos canais
    audio[:, 0] *= esquerda
    audio[:, 1] *= direita
    return audio

# função que roda toda vez que chega um bloco de áudio
def audio_callback(indata, outdata, frames, time_info, status):
    global falando, silencio_contador
    # se não tiver gravando, manda silêncio
    if not executando:
        outdata[:] = np.zeros_like(outdata)
        return
    # garante que o áudio de entrada tá em estéreo
    indata_stereo = np.repeat(indata, 2, axis=1) if indata.shape[1] == 1 else indata
    # aplica o ganho e balanço
    audio_processado = aplicar_ganho_balanco(indata_stereo)
    # guarda esse pedaço na memória
    memoria_audio.append(audio_processado.copy())

    # acumula áudio para VAD
    audio_mono = np.mean(indata, axis=1)
    buffer_vad.append(audio_mono)

    # só analisa se o buffer estiver cheio
    if len(buffer_vad) == buffer_vad.maxlen:
        audio_concat = np.concatenate(list(buffer_vad))
        audio_tensor = torch.tensor(audio_concat, dtype=torch.float32)
        speech = get_speech_timestamps(audio_tensor, model, sampling_rate=sample_rate)
        if speech:
            falando = True
            silencio_contador = 0
        else:
            silencio_contador += 1
            if silencio_contador > silencio_limite:
                falando = False

    # se estiver falando, muta o áudio de saída
    if falando:
        outdata[:] = np.zeros_like(outdata)
    else:
        outdata[:] = audio_processado

# função que repete o que tá na memória
def repetir_memoria():
    global stream
    # se não tiver nada gravado, avisa
    if not memoria_audio:
        print("nenhuma memória de áudio armazenada.")
        return
    # junta tudo que tá na memória
    som = np.concatenate(list(memoria_audio))
    # converte pra int16 pra poder tocar
    som_int16 = np.int16(som * 32767)
    try:
        # para o stream pra não dar conflito
        with stream_lock:
            stream.stop()
        # toca o som
        sd.play(som_int16, samplerate=sample_rate)
        sd.wait()
        # volta com o stream depois de tocar
        with stream_lock:
            stream.start()
    except Exception as e:
        print("erro ao reproduzir:", e)
        try:
            with stream_lock:
                stream.start()
        except:
            pass

# função que toca o alerta quando detecta a palavra-chave
def alerta_nome_detectado():
    print("palavra-chave detectada!")
    try:
        # carrega o som do alerta
        data, fs = sf.read("new-notification-08-352461.wav", dtype='int16')
        # toca o som
        sd.play(data, samplerate=fs)
    except Exception as e:
        print("erro ao tocar alerta:", e)

# função que escuta o áudio e tenta reconhecer a fala
def detectar_nome():
    reconhecedor = sr.Recognizer()
    while True:
        # só tenta reconhecer se tiver gravando e com áudio suficiente
        if not executando or len(memoria_audio) < buffer_reconhecimento:
            time.sleep(0.2)
            continue
        # pega os últimos blocos da memória
        trecho = list(memoria_audio)[-buffer_reconhecimento:]
        som = np.concatenate(trecho)
        # transforma em mono pra mandar pro reconhecedor
        som_mono = np.mean(som, axis=1)
        som_int16 = np.int16(som_mono * 32767)
        try:
            # cria objeto de áudio pro recognizer
            audio_data = sr.AudioData(som_int16.tobytes(), sample_rate, 2)
            # tenta reconhecer o que foi falado
            texto = reconhecedor.recognize_google(audio_data, language="pt-BR")
            print(f"transcrição: {texto}")
            # se for exatamente a palavra-chave, dispara o alerta
            if texto.strip().lower() in palavra_chave:
                alerta_nome_detectado()
        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            print("erro no reconhecimento:", e)
        time.sleep(0.1)

#comandos do terminal // somente backend
def escutar_comandos():
    global executando, balanco
    while True:
        try:
            comando = input("digite 'p' para play, 'q' para pause, 'r' para repetir, 'b' para ajustar balanço: ").strip().lower()
            if comando == 'p':
                executando = True
                print("gravação iniciada.")
            elif comando == 'q':
                executando = False
                print("gravação pausada.")
            elif comando == 'r':
                repetir_memoria()
            elif comando == 'b':
                try:
                    valor = float(input("novo balanço (-1.0 esquerda, 0.0 neutro, 1.0 direita): "))
                    balanco = max(-1.0, min(1.0, valor))
                    print(f"balanço ajustado para {balanco}")
                except:
                    print("valor inválido.")
        except EOFError:
            break

# função principal que inicia tudo
def iniciar_clarivox():
    global stream, threads_iniciados
    try:
        # cria o stream com entrada mono e saída estéreo
        stream = sd.Stream(
            samplerate=sample_rate,
            blocksize=frame_size,
            dtype='float32',
            channels=(1, 2),  # entrada mono, saída estéreo
            callback=audio_callback,
            latency='low'
        )
        stream.start()
        print("clarivox iniciado.")
        # inicia as threads só uma vez
        if not threads_iniciados:
            threading.Thread(target=escutar_comandos, daemon=True).start()
            threading.Thread(target=detectar_nome, daemon=True).start()
            threads_iniciados = True
        # loop principal
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nencerrado pelo usuário.")
    except Exception as e:
        print("erro ao iniciar:", e)

# ponto de entrada
if __name__ == "__main__":
    iniciar_clarivox()