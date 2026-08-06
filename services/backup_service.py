import os
import sqlite3
from datetime import datetime
from pathlib import Path

from utils.app_paths import (
    obter_caminho_banco,
    obter_pasta_backups,
)


class BackupError(Exception):
    """Erro controlado do serviço de backup."""


def validar_banco(caminho):
    caminho = Path(caminho)

    if not caminho.exists():
        raise BackupError(
            "O arquivo de backup não existe."
        )

    if caminho.stat().st_size == 0:
        raise BackupError(
            "O arquivo de backup está vazio."
        )

    try:
        conexao = sqlite3.connect(
            str(caminho)
        )

        resultado = conexao.execute(
            "PRAGMA integrity_check"
        ).fetchone()

        tabelas = {
            linha[0]
            for linha in conexao.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                """
            ).fetchall()
        }

        conexao.close()

    except sqlite3.DatabaseError as erro:
        raise BackupError(
            "O arquivo não é um banco SQLite válido."
        ) from erro

    if not resultado or resultado[0] != "ok":
        raise BackupError(
            "O banco de dados está corrompido."
        )

    obrigatorias = {
        "transacoes",
        "categorias",
        "configuracoes",
    }

    if not obrigatorias.issubset(tabelas):
        raise BackupError(
            "O arquivo não pertence ao Finanças Pro."
        )

    return True


def criar_backup():
    origem = Path(obter_caminho_banco())

    if not origem.exists():
        raise BackupError(
            "Banco de dados principal não encontrado."
        )

    pasta = Path(obter_pasta_backups())

    nome = (
        "financas_backup_"
        + datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S"
        )
        + ".db"
    )

    destino = pasta / nome

    try:
        conexao_origem = sqlite3.connect(
            str(origem)
        )

        conexao_destino = sqlite3.connect(
            str(destino)
        )

        with conexao_destino:
            conexao_origem.backup(
                conexao_destino
            )

        conexao_destino.close()
        conexao_origem.close()

        validar_banco(destino)

    except Exception:
        if destino.exists():
            destino.unlink(
                missing_ok=True
            )
        raise

    return destino


def listar_backups():
    pasta = Path(obter_pasta_backups())
    resultado = []

    for caminho in pasta.glob(
        "financas_backup_*.db"
    ):
        try:
            data_modificacao = datetime.fromtimestamp(
                caminho.stat().st_mtime
            )

            resultado.append(
                {
                    "nome": caminho.name,
                    "caminho": str(caminho),
                    "tamanho": caminho.stat().st_size,
                    "data": data_modificacao,
                }
            )
        except OSError:
            continue

    resultado.sort(
        key=lambda item: item["data"],
        reverse=True,
    )

    return resultado


def criar_backup_seguranca():
    origem = Path(obter_caminho_banco())
    pasta = Path(obter_pasta_backups())

    nome = (
        "antes_restauracao_"
        + datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S"
        )
        + ".db"
    )

    destino = pasta / nome

    conexao_origem = sqlite3.connect(
        str(origem)
    )

    conexao_destino = sqlite3.connect(
        str(destino)
    )

    with conexao_destino:
        conexao_origem.backup(
            conexao_destino
        )

    conexao_destino.close()
    conexao_origem.close()

    return destino


def restaurar_backup(caminho_backup):
    origem_backup = Path(
        caminho_backup
    )

    validar_banco(
        origem_backup
    )

    banco_principal = Path(obter_caminho_banco())
    temporario = banco_principal.with_suffix(
        ".restauracao.tmp"
    )

    backup_seguranca = (
        criar_backup_seguranca()
    )

    try:
        conexao_origem = sqlite3.connect(
            str(origem_backup)
        )

        conexao_temporaria = sqlite3.connect(
            str(temporario)
        )

        with conexao_temporaria:
            conexao_origem.backup(
                conexao_temporaria
            )

        conexao_temporaria.close()
        conexao_origem.close()

        validar_banco(
            temporario
        )

        os.replace(
            temporario,
            banco_principal,
        )

    except Exception as erro:
        if temporario.exists():
            temporario.unlink(
                missing_ok=True
            )

        raise BackupError(
            "Não foi possível restaurar o backup."
        ) from erro

    return {
        "restaurado": banco_principal,
        "backup_seguranca": backup_seguranca,
    }


def excluir_backup(caminho_backup):
    caminho = Path(
        caminho_backup
    )

    pasta_backups = (
        Path(obter_pasta_backups()).resolve()
    )

    try:
        caminho_resolvido = caminho.resolve()
    except OSError as erro:
        raise BackupError(
            "Caminho de backup inválido."
        ) from erro

    if caminho_resolvido.parent != pasta_backups:
        raise BackupError(
            "Só é permitido excluir backups locais."
        )

    if not caminho_resolvido.exists():
        raise BackupError(
            "O backup já não existe."
        )

    caminho_resolvido.unlink()
    return True