import sounddevice as sd
import numpy as np
import time
from collections import deque
import threading
import speech_recognition as sr
import winsound

# Configurações de áudio
sample_rate = 44100       # Taxa de amostragem em hz // esse valor e o padrao de qualidade de audio, quanto maior, melhor e o som, porem mais pesado fica a reproducao
frame_duration = 0.1      # Duração de cada bloco de áudio (s)
frame_size = int(sample_rate * frame_duration)  # Tamanho do bloco // essa conta precisa ser feita pro sistema entender qual o tamanho dos blocos que ele deve manipular
ganho = 2.0 #Amplificador, colocar valores entre 1.0 e 3.0 para testar o melhor
memoria_segundos = 5 #Quanto tempo o audio fica guardado caso a pessoa queira que a frase seja repetida
buffer_maximo = int(memoria_segundos / frame_duration) #Se nosso frame duration seria 0.1s, em 1 segundo teriamos 10 blocos, o buffer_maximo esta sendo representado em blocos de audio
memoria_audio = deque(maxlen=buffer_maximo) #Lista circular para guardar os blocos de som, quando atinge o buffer_maximo os blocos mais antigos sao descartados
executando = True
stream = None
palavra_chave = ["pietro"] 

# Função de callback: chamada a cada bloco de áudio
def audio_callback(indata, outdata, frames, time_info, status):
    global memoria_audio
    if status:
        print("Erro:", status)

    audio_amplificado = indata * ganho #indata = o som que entra, multiplicado pelo ganho
    audio_amplificado = np.clip(audio_amplificado, -1.0, 1.0) #mantem os valores do audio no range para nao causar distorcao e estabilizar os volumes de audio

    memoria_audio.append(audio_amplificado.copy()) #Sobresceve o blocos de audio com append, adicionando novos blocos no fim da lista

    # print("Ganho:", ganho)
    # print("indata:", indata[:10])
    # print("amplificado:", audio_amplificado[:10])

    outdata[:] = audio_amplificado  # pega o audio ja amplificado e joga no outdata (som que esta entrando no fone)

#Comandos para reproduzir a memoria
def escutar_comandos():
    global executando
    while executando:
        comando = input("digite 'r' para repetir ou 'q' para sair: ").strip().lower()
        if comando == 'r':
            print("reproduzindo memoria...")
            repetir_memoria()
        elif comando == 'q':
            print("encerrando...")
            executando = False
     
#Reproducao dos blocos de som
def repetir_memoria():
    global stream
    if not memoria_audio: #Verifica se a memoria esta vazia retornando um aviso
        print("nenhuma memoria de audio armazenada.")
        return
    
    som = np.concatenate(list(memoria_audio))  #transforma o deque em lista e concatena os blocos // sd.play so funciona com um unico array continuo, por isso foi necessario formar uma lista e concatenar
   
    stream.stop()
    sd.play(som, samplerate=sample_rate) #reproduz o audio na mesma taxa de amostragem gravada
    sd.wait() #espera a reproducao completa do som antes de continuar com o codigo
    stream.start()
# Inicia o stream de áudio // as variaveis que a api precisa pra executar o audio *channels=1 reproducao em mono, como ele reproduzira falas nao precisa ser estereo, logo, mantem o programa leve

def alerta_nome_detectado(): #beep de alerta para palavra chave detectada
    print("Palavra chave detectada. tocando alarme sonoro")
    winsound.Beep(1000, 500)  # frequência 1000 hz, duração 500 ms

def detectar_nome(): #deteccao de nome, so tenta transcrever se memoria estiver cheia
    reconhecedor = sr.Recognizer()
    while executando:
        if len(memoria_audio) < buffer_maximo:
            time.sleep(1)
            continue

        som = np.concatenate(list(memoria_audio))
        som_int16 = np.int16(som * 32767)

        try:
            audio_data = sr.AudioData(som_int16.tobytes(), sample_rate, 2)
            texto = reconhecedor.recognize_google(audio_data, language="pt-BR")

            print(f"Transcrição: {texto}")
            if any(nome in texto.lower() for nome in palavra_chave):
                    alerta_nome_detectado()
        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            print("Erro no reconhecimento:", e)

        time.sleep(2)
try:
    stream = sd.Stream(
        samplerate=sample_rate,
        blocksize=frame_size,
        dtype='float32',
        channels=1,             # Mono (1 canal)
        callback=audio_callback
    )
    stream.start()

    print("Clarivox ativo")
    threading.Thread(target=escutar_comandos, daemon=True).start()
    threading.Thread(target=detectar_nome, daemon=True).start()

    print("Capturando...\nPressione Ctrl+C para parar.")
    while executando:
        time.sleep(1)  # basicamente um loop, enquanto for true conta 1 segundo, e enquanto ele conta, esta sendo true

    stream.stop()
    stream.close()

except KeyboardInterrupt:
    print("\n Encerrado pelo usuário.")
except Exception as e:
    print("Erro ao iniciar o stream:", e)