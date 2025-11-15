O Clarivox é um aplicativo voltado para pessoas com deficiência auditiva. Ele transforma fones de ouvido comuns em dispositivos de amplificação sonora personalizados, oferecendo recursos que facilitam a compreensão da fala em tempo real.

O sistema utiliza bibliotecas de áudio e machine learning embarcado para detectar atividade de voz, processar o som e disponibilizar controles acessíveis como play, pausa, repetição de fala e ajuste de balanço entre canais.

Funcionalidades:
Captura e reprodução de áudio em tempo real
Detecção de fala com Silero VAD
Interface acessível com botões de controle (play, pause, repetir, balanço)
Estrutura modular para expansão futura (reconhecimento de fala, perfis auditivos personalizados)
Compatibilidade com fones de ouvido comuns

Tecnologias utilizadas
Python
SoundDevice e SoundFile para manipulação de áudio
NumPy para processamento de dados
Silero VAD para detecção de atividade de voz
Frontend com Kivy/HTML5 + CSS + JS (em produção)
SQLite/PostgreSQL para gerenciamento de dados

Instalação
Clone o repositório:
bash
git clone https://github.com/seuusuario/clarivox.git
cd clarivox

Crie o ambiente virtual e instale as dependências:
bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
pip install -r requirements.txt

Como usar
Execute o aplicativo:

bash
python main.py

Conecte os fones de ouvido e utilize os controles do console para ajustar a experiência auditiva.

Roadmap
[x] Captura e reprodução de áudio
[x] Detecção de fala com IA
[ ] Reconhecimento de fala integrado
[ ] Perfis auditivos personalizados
[ ] Exportação de relatórios de uso
[ ] Interface do APP
