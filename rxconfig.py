import reflex as rx

config = rx.Config(
    app_name="frontend",  # nome da pasta onde está app.py
    disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],
)