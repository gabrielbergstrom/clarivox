import reflex as rx
from backend.audio_manager import iniciar_execucao, pausar_execucao, repetir_memoria

class State(rx.State):
    transcricao: str = ""

    def escutar(self):
        # passa o callback para receber a transcrição do backend
        iniciar_execucao(callback=self.receber_transcricao)

    def receber_transcricao(self, texto: str):
        # Atualiza o estado de forma thread-safe
        rx.run_in_worker_thread(self.atualizar_transcricao, texto)

    def atualizar_transcricao(self, texto: str):
        # Atualiza a variável do estado
        self.transcricao = texto

    def pausar(self):
        pausar_execucao()

    def repetir(self):
        repetir_memoria()

def index() -> rx.Component:
    return rx.box(
        rx.center(
            rx.vstack(
                rx.hstack(
                    rx.heading("Clarivox", size="9", color=rx.color_mode_cond("black", "white")),
                    rx.icon(tag="ear", size=40, color="orange"),
                    spacing="2",
                    align="center",
                    justify="center",
                ),
                rx.text("Aperte o botão para gravar", size="5", text_align="center",
                        color=rx.color_mode_cond("black", "white"), margin_y="5px"),
                rx.vstack(
                    rx.button(
                        rx.icon(tag="volume-2", size=24, color="white"),
                        rx.text("Escutar", size="5"),
                        on_click=State.escutar,
                        spacing="3",
                        justify="center",
                        color_scheme="green",
                        variant="solid",
                        size="4",
                        border_radius="full",
                        width=["180px", "230px"],
                        height=["60px", "70px"],
                    ),
                    rx.button(
                        rx.icon(tag="mic", size=24, color="white"),
                        rx.text("Repetir", size="5"),
                        on_click=State.repetir,
                        spacing="3",
                        justify="center",
                        variant="solid",
                        size="4",
                        border_radius="full",
                        background_color="#d4af37",
                        _hover={"background_color": "#c39c32"},
                        color="white",
                        width=["180px", "230px"],
                        height=["60px", "70px"],
                    ),
                    rx.button(
                        rx.icon(tag="pause", size=24, color="white"),
                        rx.text("Pausar", size="5"),
                        on_click=State.pausar,
                        spacing="3",
                        justify="center",
                        color_scheme="red",
                        variant="solid",
                        size="4",
                        border_radius="full",
                        width=["180px", "230px"],
                        height=["60px", "70px"],
                    ),
                    spacing="4",
                    align="center",
                    margin_top="10px",
                ),
                rx.vstack(
                    rx.text("Transcrição:", size="5", text_align="center",
                            margin_top="10px", margin_bottom="5px",
                            color=rx.color_mode_cond("black", "white")),
                    rx.box(
                        rx.text_area(
                            value=State.transcricao,
                            placeholder="A transcrição aparecerá aqui...",
                            width="90%",
                            height=["150px", "200px"],
                            resize="none",
                            padding="18px",
                            border=rx.color_mode_cond("2px solid #000", "2px solid #fff"),
                            border_radius="lg",
                            background_color=rx.color_mode_cond(
                                "rgba(0,0,0,0.05)",
                                "rgba(255,255,255,0.05)"
                            ),
                            color=rx.color_mode_cond("black", "white"),
                            font_size="2rem",
                            line_height="2.4rem",
                            font_weight="bold",
                            overflow_y="auto",
                            _placeholder={"color": "gray", "font_size": "1.6rem"},
                        ),
                        width="100%",
                        max_width="400px",
                        display="flex",
                        justify_content="center",
                    ),
                    align="center",
                    width="100%",
                ),
                spacing="4",
                align="center",
                justify="center",
                width="100%",
                height="100vh",
            ),
        ),
        background_color=rx.color_mode_cond("white", "black"),
        width="100%",
        height="100vh",
        padding="10px",
        position="relative",
    )

app = rx.App()
app.add_page(index)
