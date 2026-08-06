import os
from pathlib import Path

from kivy.utils import platform


NOME_BANCO = "financas.db"
NOME_PASTA_BACKUPS = "backups"


def obter_pasta_projeto():
    """
    Pasta do código-fonte no Windows/Linux.
    No Android, esta pasta não deve ser usada para gravação.
    """
    return Path(__file__).resolve().parent.parent


def obter_pasta_dados():
    """
    Retorna uma pasta gravável e privada para os dados do aplicativo.

    Windows/Linux:
        pasta raiz do projeto, preservando o funcionamento atual.

    Android:
        diretório interno privado do aplicativo.
    """
    if platform == "android":
        try:
            from jnius import autoclass

            PythonActivity = autoclass(
                "org.kivy.android.PythonActivity"
            )

            contexto = PythonActivity.mActivity

            return Path(
                contexto.getFilesDir().getAbsolutePath()
            )

        except Exception as erro:
            raise RuntimeError(
                "Não foi possível localizar o armazenamento interno "
                "do aplicativo Android."
            ) from erro

    return obter_pasta_projeto()


def obter_caminho_banco():
    pasta = obter_pasta_dados()
    pasta.mkdir(
        parents=True,
        exist_ok=True,
    )

    return pasta / NOME_BANCO


def obter_pasta_backups():
    pasta = (
        obter_pasta_dados()
        / NOME_PASTA_BACKUPS
    )

    pasta.mkdir(
        parents=True,
        exist_ok=True,
    )

    return pasta


def obter_pasta_cache():
    if platform == "android":
        try:
            from jnius import autoclass

            PythonActivity = autoclass(
                "org.kivy.android.PythonActivity"
            )

            contexto = PythonActivity.mActivity

            pasta = Path(
                contexto.getCacheDir().getAbsolutePath()
            )

            pasta.mkdir(
                parents=True,
                exist_ok=True,
            )

            return pasta

        except Exception:
            pass

    pasta = obter_pasta_dados() / ".cache"
    pasta.mkdir(
        parents=True,
        exist_ok=True,
    )

    return pasta