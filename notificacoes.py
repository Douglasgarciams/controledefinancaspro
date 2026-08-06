import os
from datetime import datetime

from kivy.utils import platform

from database.database import db


def formatar_moeda(valor):
    texto = f"{float(valor):,.2f}"

    texto = (
        texto
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    return f"R$ {texto}"


def solicitar_permissao_notificacoes():
    """
    Solicita POST_NOTIFICATIONS no Android 13+.
    No Windows, retorna True apenas para permitir testes do app.
    """
    if platform != "android":
        return True

    try:
        from android.permissions import (
            Permission,
            request_permissions,
        )

        permissao = getattr(
            Permission,
            "POST_NOTIFICATIONS",
            "android.permission.POST_NOTIFICATIONS",
        )

        request_permissions(
            [permissao]
        )

        return True

    except Exception as erro:
        print(
            "Erro ao solicitar permissão:",
            erro,
        )
        return False


def emitir_notificacao(
    titulo,
    mensagem,
):
    try:
        from plyer import notification

        notification.notify(
            title=titulo,
            message=mensagem,
            app_name="Finanças Pro",
            timeout=12,
        )

        return True

    except Exception as erro:
        print(
            "Erro ao emitir notificação:",
            erro,
        )
        return False


def verificar_e_emitir_alertas(
    forcar_teste=False,
):
    configuracao = (
        db.obter_configuracao_alertas()
    )

    if (
        not configuracao["ativo"]
        and not forcar_teste
    ):
        return 0

    dias = configuracao[
        "dias_antecedencia"
    ]

    if forcar_teste:
        emitir_notificacao(
            "Finanças Pro",
            (
                "Teste de alerta ativado. "
                f"Você será avisado com "
                f"{dias} dia(s) de antecedência."
            ),
        )
        return 1

    hoje = datetime.now().date()
    data_alerta = hoje.strftime(
        "%Y-%m-%d"
    )

    contas = db.obter_contas_para_alerta(
        dias_antecedencia=dias,
        data_referencia=hoje,
    )

    enviados = 0

    for conta in contas:
        if db.alerta_ja_enviado(
            transacao_id=conta["id"],
            data_alerta=data_alerta,
            dias_antecedencia=dias,
        ):
            continue

        mensagem = (
            f"{conta['descricao']} vence "
            f"em {dias} dia(s), no valor de "
            f"{formatar_moeda(conta['valor'])}."
        )

        if emitir_notificacao(
            "Conta próxima do vencimento",
            mensagem,
        ):
            db.registrar_alerta_enviado(
                transacao_id=conta["id"],
                data_alerta=data_alerta,
                dias_antecedencia=dias,
            )
            enviados += 1

    return enviados