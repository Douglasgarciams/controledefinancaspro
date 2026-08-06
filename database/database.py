import sqlite3
import calendar
from datetime import datetime, timedelta

from utils.app_paths import obter_caminho_banco


class Database:

    def __init__(self):
        self.caminho = str(obter_caminho_banco())
        self.criar_tabelas()
        self.executar_migracoes()
        self.criar_categorias_padrao()

    def conectar(self):
        conexao = sqlite3.connect(self.caminho)
        conexao.row_factory = sqlite3.Row
        conexao.execute("PRAGMA foreign_keys = ON")
        return conexao

    def criar_tabelas(self):
        with self.conectar() as conexao:
            conexao.execute(
                """
                CREATE TABLE IF NOT EXISTS categorias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    UNIQUE(nome, tipo)
                )
                """
            )

            conexao.execute(
                """
                CREATE TABLE IF NOT EXISTS transacoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    descricao TEXT NOT NULL,
                    valor REAL NOT NULL CHECK(valor > 0),
                    tipo TEXT NOT NULL
                        CHECK(tipo IN ('Receita', 'Despesa')),
                    categoria_id INTEGER,
                    data TEXT NOT NULL,
                    criado_em TEXT NOT NULL,
                    FOREIGN KEY(categoria_id)
                        REFERENCES categorias(id)
                        ON DELETE SET NULL
                )
                """
            )

            conexao.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_transacoes_data
                ON transacoes(data)
                """
            )

            conexao.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_transacoes_tipo
                ON transacoes(tipo)
                """
            )

            conexao.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_transacoes_categoria
                ON transacoes(categoria_id)
                """
            )

            conexao.execute(
                """
                CREATE TABLE IF NOT EXISTS configuracoes (
                    chave TEXT PRIMARY KEY,
                    valor TEXT NOT NULL
                )
                """
            )

            conexao.execute(
                """
                CREATE TABLE IF NOT EXISTS alertas_enviados (
                    transacao_id INTEGER NOT NULL,
                    data_alerta TEXT NOT NULL,
                    dias_antecedencia INTEGER NOT NULL,
                    enviado_em TEXT NOT NULL,
                    PRIMARY KEY (
                        transacao_id,
                        data_alerta,
                        dias_antecedencia
                    ),
                    FOREIGN KEY(transacao_id)
                        REFERENCES transacoes(id)
                        ON DELETE CASCADE
                )
                """
            )

            conexao.execute(
                """
                CREATE TABLE IF NOT EXISTS compras_parceladas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    descricao TEXT NOT NULL,
                    valor_original REAL NOT NULL,
                    quantidade_parcelas INTEGER NOT NULL,
                    valor_parcela REAL NOT NULL,
                    categoria_id INTEGER,
                    data_primeira_parcela TEXT NOT NULL,
                    criado_em TEXT NOT NULL,
                    FOREIGN KEY(categoria_id)
                        REFERENCES categorias(id)
                        ON DELETE SET NULL
                )
                """
            )

    def executar_migracoes(self):
        """Adiciona colunas novas sem apagar o banco existente."""
        with self.conectar() as conexao:
            colunas = {
                linha["name"]
                for linha in conexao.execute(
                    "PRAGMA table_info(transacoes)"
                ).fetchall()
            }

            novas_colunas = {
                "compra_parcelada_id": "INTEGER",
                "numero_parcela": "INTEGER",
                "total_parcelas": "INTEGER",
                "valor_original": "REAL",
                "status": "TEXT DEFAULT 'Pago'",
                "data_pagamento": "TEXT",
            }

            for nome, tipo_sql in novas_colunas.items():
                if nome not in colunas:
                    conexao.execute(
                        f"""
                        ALTER TABLE transacoes
                        ADD COLUMN {nome} {tipo_sql}
                        """
                    )

            conexao.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_transacoes_compra_parcelada
                ON transacoes(compra_parcelada_id)
                """
            )

            conexao.execute(
                """
                UPDATE transacoes
                SET status = 'Pago'
                WHERE status IS NULL
                   OR TRIM(status) = ''
                """
            )

    @staticmethod
    def adicionar_meses(data_base, quantidade):
        """Soma meses e ajusta o dia para o último dia válido."""
        ano = data_base.year
        mes = data_base.month + quantidade

        ano += (mes - 1) // 12
        mes = ((mes - 1) % 12) + 1

        ultimo_dia = calendar.monthrange(
            ano,
            mes,
        )[1]

        dia = min(
            data_base.day,
            ultimo_dia,
        )

        return data_base.replace(
            year=ano,
            month=mes,
            day=dia,
        )

    def adicionar_compra_parcelada(
        self,
        descricao,
        valor_original,
        quantidade_parcelas,
        valor_parcela,
        categoria,
        data_primeira_parcela,
        status="Pendente",
    ):
        descricao = descricao.strip()
        categoria = categoria.strip()

        if not descricao:
            raise ValueError(
                "A descrição é obrigatória."
            )

        if valor_original <= 0:
            raise ValueError(
                "O valor original deve ser maior que zero."
            )

        if quantidade_parcelas < 2:
            raise ValueError(
                "A compra parcelada deve ter pelo menos 2 parcelas."
            )

        if valor_parcela <= 0:
            raise ValueError(
                "O valor da parcela deve ser maior que zero."
            )

        if status not in ("Pago", "Pendente"):
            raise ValueError(
                "Status inicial das parcelas inválido."
            )

        categoria_id = self.obter_categoria_id(
            categoria,
            "Despesa",
        )

        if categoria_id is None:
            raise ValueError(
                "Categoria de despesa não encontrada."
            )

        try:
            primeira_data = datetime.strptime(
                data_primeira_parcela,
                "%Y-%m-%d",
            )
        except ValueError as erro:
            raise ValueError(
                "Data da primeira parcela inválida."
            ) from erro

        criado_em = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        with self.conectar() as conexao:
            cursor = conexao.execute(
                """
                INSERT INTO compras_parceladas (
                    descricao,
                    valor_original,
                    quantidade_parcelas,
                    valor_parcela,
                    categoria_id,
                    data_primeira_parcela,
                    criado_em
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    descricao,
                    valor_original,
                    quantidade_parcelas,
                    valor_parcela,
                    categoria_id,
                    data_primeira_parcela,
                    criado_em,
                ),
            )

            compra_id = cursor.lastrowid
            parcelas = []

            for indice in range(
                quantidade_parcelas
            ):
                numero = indice + 1

                data_parcela = self.adicionar_meses(
                    primeira_data,
                    indice,
                ).strftime("%Y-%m-%d")

                descricao_parcela = (
                    f"{descricao} "
                    f"({numero}/{quantidade_parcelas})"
                )

                data_pagamento = (
                    data_parcela
                    if status == "Pago"
                    else None
                )

                parcelas.append(
                    (
                        descricao_parcela,
                        valor_parcela,
                        "Despesa",
                        categoria_id,
                        data_parcela,
                        criado_em,
                        compra_id,
                        numero,
                        quantidade_parcelas,
                        valor_original,
                        status,
                        data_pagamento,
                    )
                )

            conexao.executemany(
                """
                INSERT INTO transacoes (
                    descricao,
                    valor,
                    tipo,
                    categoria_id,
                    data,
                    criado_em,
                    compra_parcelada_id,
                    numero_parcela,
                    total_parcelas,
                    valor_original,
                    status,
                    data_pagamento
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                parcelas,
            )

        return {
            "compra_id": compra_id,
            "total_parcelado": (
                quantidade_parcelas
                * valor_parcela
            ),
            "acrescimo": (
                quantidade_parcelas
                * valor_parcela
                - valor_original
            ),
        }

    def criar_categorias_padrao(self):
        categorias = [
            ("Salário", "Receita"),
            ("Investimentos", "Receita"),
            ("Outros ganhos", "Receita"),
            ("Alimentação", "Despesa"),
            ("Moradia", "Despesa"),
            ("Transporte", "Despesa"),
            ("Saúde", "Despesa"),
            ("Lazer", "Despesa"),
            ("Cartão de crédito", "Despesa"),
            ("Outros gastos", "Despesa"),
        ]

        with self.conectar() as conexao:
            conexao.executemany(
                """
                INSERT OR IGNORE INTO categorias (
                    nome,
                    tipo
                )
                VALUES (?, ?)
                """,
                categorias,
            )

    def obter_categorias(self, tipo):
        with self.conectar() as conexao:
            cursor = conexao.execute(
                """
                SELECT id, nome
                FROM categorias
                WHERE tipo = ?
                ORDER BY nome
                """,
                (tipo,),
            )

            return [
                dict(linha)
                for linha in cursor.fetchall()
            ]

    def obter_categoria_id(self, nome, tipo):
        with self.conectar() as conexao:
            cursor = conexao.execute(
                """
                SELECT id
                FROM categorias
                WHERE nome = ?
                  AND tipo = ?
                """,
                (nome, tipo),
            )

            linha = cursor.fetchone()
            return linha["id"] if linha else None

    def adicionar_transacao(
        self,
        descricao,
        valor,
        tipo,
        categoria,
        data,
        status="Pago",
    ):
        descricao = descricao.strip()
        categoria = categoria.strip()

        if not descricao:
            raise ValueError(
                "A descrição é obrigatória."
            )

        if valor <= 0:
            raise ValueError(
                "O valor deve ser maior que zero."
            )

        if tipo not in ("Receita", "Despesa"):
            raise ValueError(
                "Tipo de transação inválido."
            )

        if tipo == "Receita":
            status = "Pago"
        elif status not in ("Pago", "Pendente"):
            raise ValueError(
                "Status da despesa inválido."
            )

        categoria_id = self.obter_categoria_id(
            categoria,
            tipo,
        )

        if categoria_id is None:
            with self.conectar() as conexao:
                cursor = conexao.execute(
                    """
                    INSERT INTO categorias (
                        nome,
                        tipo
                    )
                    VALUES (?, ?)
                    """,
                    (
                        categoria,
                        tipo,
                    ),
                )

                categoria_id = cursor.lastrowid

        criado_em = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        data_pagamento = (
            data
            if tipo == "Despesa"
            and status == "Pago"
            else None
        )

        with self.conectar() as conexao:
            conexao.execute(
                """
                INSERT INTO transacoes (
                    descricao,
                    valor,
                    tipo,
                    categoria_id,
                    data,
                    criado_em,
                    status,
                    data_pagamento
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    descricao,
                    valor,
                    tipo,
                    categoria_id,
                    data,
                    criado_em,
                    status,
                    data_pagamento,
                ),
            )

    def obter_resumo(self):
        with self.conectar() as conexao:
            cursor = conexao.execute(
                """
                SELECT
                    COALESCE(
                        SUM(
                            CASE
                                WHEN tipo = 'Receita'
                                THEN valor
                                ELSE 0
                            END
                        ),
                        0
                    ) AS receitas,

                    COALESCE(
                        SUM(
                            CASE
                                WHEN tipo = 'Despesa'
                                THEN valor
                                ELSE 0
                            END
                        ),
                        0
                    ) AS despesas

                FROM transacoes
                """
            )

            linha = cursor.fetchone()

            receitas = float(linha["receitas"])
            despesas = float(linha["despesas"])

            return {
                "receitas": receitas,
                "despesas": despesas,
                "saldo": receitas - despesas,
            }

    def obter_ultimas_transacoes(self, limite=20):
        with self.conectar() as conexao:
            cursor = conexao.execute(
                """
                SELECT
                    t.id,
                    t.descricao,
                    t.valor,
                    t.tipo,
                    t.data,
                    COALESCE(
                        c.nome,
                        'Sem categoria'
                    ) AS categoria

                FROM transacoes AS t

                LEFT JOIN categorias AS c
                    ON c.id = t.categoria_id

                ORDER BY
                    t.data DESC,
                    t.id DESC

                LIMIT ?
                """,
                (limite,),
            )

            return [
                dict(linha)
                for linha in cursor.fetchall()
            ]

    def excluir_transacao(self, transacao_id):
        with self.conectar() as conexao:
            conexao.execute(
                """
                DELETE FROM transacoes
                WHERE id = ?
                """,
                (transacao_id,),
            )

    def adicionar_categoria(self, nome, tipo):
        nome = nome.strip()

        if not nome:
            raise ValueError(
                "O nome da categoria é obrigatório."
            )

        if tipo not in ("Receita", "Despesa"):
            raise ValueError(
                "Tipo de categoria inválido."
            )

        try:
            with self.conectar() as conexao:
                cursor = conexao.execute(
                    """
                    INSERT INTO categorias (
                        nome,
                        tipo
                    )
                    VALUES (?, ?)
                    """,
                    (nome, tipo),
                )

                return cursor.lastrowid

        except sqlite3.IntegrityError as erro:
            raise ValueError(
                "Esta categoria já está cadastrada."
            ) from erro

    def contar_transacoes_categoria(
        self,
        categoria_id,
    ):
        with self.conectar() as conexao:
            cursor = conexao.execute(
                """
                SELECT COUNT(*) AS quantidade
                FROM transacoes
                WHERE categoria_id = ?
                """,
                (categoria_id,),
            )

            linha = cursor.fetchone()
            return int(linha["quantidade"])

    def excluir_categoria(self, categoria_id):
        quantidade = self.contar_transacoes_categoria(
            categoria_id
        )

        if quantidade > 0:
            raise ValueError(
                "Esta categoria possui transações "
                "e não pode ser excluída."
            )

        with self.conectar() as conexao:
            cursor = conexao.execute(
                """
                DELETE FROM categorias
                WHERE id = ?
                """,
                (categoria_id,),
            )

            return cursor.rowcount > 0

    def obter_todas_categorias(self):
        with self.conectar() as conexao:
            cursor = conexao.execute(
                """
                SELECT
                    c.id,
                    c.nome,
                    c.tipo,
                    COUNT(t.id) AS quantidade_transacoes

                FROM categorias AS c

                LEFT JOIN transacoes AS t
                    ON t.categoria_id = c.id

                GROUP BY
                    c.id,
                    c.nome,
                    c.tipo

                ORDER BY
                    c.tipo,
                    c.nome
                """
            )

            return [
                dict(linha)
                for linha in cursor.fetchall()
            ]

    def obter_transacao_por_id(self, transacao_id):
        with self.conectar() as conexao:
            cursor = conexao.execute(
                """
                SELECT
                    t.id,
                    t.descricao,
                    t.valor,
                    t.tipo,
                    t.data,
                    COALESCE(
                        c.nome,
                        'Sem categoria'
                    ) AS categoria,
                    COALESCE(
                        t.status,
                        'Pago'
                    ) AS status,
                    t.data_pagamento,
                    t.compra_parcelada_id,
                    t.numero_parcela,
                    t.total_parcelas
                FROM transacoes AS t
                LEFT JOIN categorias AS c
                    ON c.id = t.categoria_id
                WHERE t.id = ?
                """,
                (transacao_id,),
            )

            linha = cursor.fetchone()
            return dict(linha) if linha else None

    def atualizar_transacao(
        self,
        transacao_id,
        descricao,
        valor,
        tipo,
        categoria,
        data,
        status="Pago",
    ):
        descricao = descricao.strip()
        categoria = categoria.strip()

        if not descricao:
            raise ValueError(
                "A descrição é obrigatória."
            )

        if valor <= 0:
            raise ValueError(
                "O valor deve ser maior que zero."
            )

        if tipo not in ("Receita", "Despesa"):
            raise ValueError(
                "Tipo de transação inválido."
            )

        categoria_id = self.obter_categoria_id(
            categoria,
            tipo,
        )

        if categoria_id is None:
            raise ValueError(
                "Categoria não encontrada."
            )

        if tipo == "Receita":
            status = "Pago"
        elif status not in ("Pago", "Pendente"):
            raise ValueError(
                "Status da despesa inválido."
            )

        data_pagamento = (
            datetime.now().strftime("%Y-%m-%d")
            if tipo == "Despesa"
            and status == "Pago"
            else None
        )

        with self.conectar() as conexao:
            cursor = conexao.execute(
                """
                UPDATE transacoes
                SET
                    descricao = ?,
                    valor = ?,
                    tipo = ?,
                    categoria_id = ?,
                    data = ?,
                    status = ?,
                    data_pagamento = ?
                WHERE id = ?
                """,
                (
                    descricao,
                    valor,
                    tipo,
                    categoria_id,
                    data,
                    status,
                    data_pagamento,
                    transacao_id,
                ),
            )

            return cursor.rowcount > 0

    def _montar_filtros(
        self,
        pesquisa="",
        tipo="Todos",
        mes=None,
        ano=None,
    ):
        clausulas = []
        parametros = []

        pesquisa = pesquisa.strip()

        if pesquisa:
            termo = f"%{pesquisa}%"
            clausulas.append(
                """
                (
                    LOWER(t.descricao) LIKE LOWER(?)
                    OR LOWER(
                        COALESCE(c.nome, '')
                    ) LIKE LOWER(?)
                    OR CAST(t.valor AS TEXT) LIKE ?
                    OR t.data LIKE ?
                )
                """
            )
            parametros.extend(
                [termo, termo, termo, termo]
            )

        if tipo in ("Receita", "Despesa"):
            clausulas.append("t.tipo = ?")
            parametros.append(tipo)

        if ano is not None:
            clausulas.append(
                "strftime('%Y', t.data) = ?"
            )
            parametros.append(str(ano))

        if mes is not None:
            clausulas.append(
                "strftime('%m', t.data) = ?"
            )
            parametros.append(
                f"{int(mes):02d}"
            )

        where_sql = ""

        if clausulas:
            where_sql = (
                " WHERE "
                + " AND ".join(clausulas)
            )

        return where_sql, parametros

    def obter_transacoes_filtradas(
        self,
        pesquisa="",
        tipo="Todos",
        mes=None,
        ano=None,
        limite=200,
    ):
        where_sql, parametros = self._montar_filtros(
            pesquisa=pesquisa,
            tipo=tipo,
            mes=mes,
            ano=ano,
        )

        consulta = f"""
            SELECT
                t.id,
                t.descricao,
                t.valor,
                t.tipo,
                t.data,
                COALESCE(
                    c.nome,
                    'Sem categoria'
                ) AS categoria,
                COALESCE(
                    t.status,
                    'Pago'
                ) AS status,
                t.data_pagamento,
                t.compra_parcelada_id,
                t.numero_parcela,
                t.total_parcelas
            FROM transacoes AS t
            LEFT JOIN categorias AS c
                ON c.id = t.categoria_id
            {where_sql}
            ORDER BY
                t.data DESC,
                t.id DESC
            LIMIT ?
        """

        parametros.append(int(limite))

        with self.conectar() as conexao:
            cursor = conexao.execute(
                consulta,
                parametros,
            )

            return [
                dict(linha)
                for linha in cursor.fetchall()
            ]

    def obter_resumo_filtrado(
        self,
        pesquisa="",
        tipo="Todos",
        mes=None,
        ano=None,
    ):
        where_sql, parametros = self._montar_filtros(
            pesquisa=pesquisa,
            tipo=tipo,
            mes=mes,
            ano=ano,
        )

        consulta = f"""
            SELECT
                COALESCE(
                    SUM(
                        CASE
                            WHEN t.tipo = 'Receita'
                            THEN t.valor
                            ELSE 0
                        END
                    ),
                    0
                ) AS receitas,

                COALESCE(
                    SUM(
                        CASE
                            WHEN t.tipo = 'Despesa'
                            THEN t.valor
                            ELSE 0
                        END
                    ),
                    0
                ) AS despesas,

                COUNT(t.id) AS quantidade

            FROM transacoes AS t

            LEFT JOIN categorias AS c
                ON c.id = t.categoria_id

            {where_sql}
        """

        with self.conectar() as conexao:
            cursor = conexao.execute(
                consulta,
                parametros,
            )

            linha = cursor.fetchone()

            receitas = float(
                linha["receitas"]
            )
            despesas = float(
                linha["despesas"]
            )

            return {
                "receitas": receitas,
                "despesas": despesas,
                "saldo": receitas - despesas,
                "quantidade": int(
                    linha["quantidade"]
                ),
            }

    def obter_anos_disponiveis(self):
        with self.conectar() as conexao:
            cursor = conexao.execute(
                """
                SELECT DISTINCT
                    strftime('%Y', data) AS ano
                FROM transacoes
                WHERE data IS NOT NULL
                ORDER BY ano DESC
                """
            )

            anos = [
                int(linha["ano"])
                for linha in cursor.fetchall()
                if linha["ano"]
            ]

        ano_atual = datetime.now().year

        if ano_atual not in anos:
            anos.insert(0, ano_atual)

        return anos

    def obter_totais_por_categoria(
        self,
        tipo="Despesa",
        mes=None,
        ano=None,
    ):
        clausulas = ["t.tipo = ?"]
        parametros = [tipo]

        if ano is not None:
            clausulas.append(
                "strftime('%Y', t.data) = ?"
            )
            parametros.append(str(ano))

        if mes is not None:
            clausulas.append(
                "strftime('%m', t.data) = ?"
            )
            parametros.append(
                f"{int(mes):02d}"
            )

        where_sql = " AND ".join(clausulas)

        consulta = f"""
            SELECT
                COALESCE(
                    c.nome,
                    'Sem categoria'
                ) AS categoria,
                SUM(t.valor) AS total,
                COUNT(t.id) AS quantidade
            FROM transacoes AS t
            LEFT JOIN categorias AS c
                ON c.id = t.categoria_id
            WHERE {where_sql}
            GROUP BY
                c.id,
                c.nome
            ORDER BY
                total DESC,
                categoria ASC
        """

        with self.conectar() as conexao:
            cursor = conexao.execute(
                consulta,
                parametros,
            )

            return [
                {
                    "categoria": linha["categoria"],
                    "total": float(linha["total"]),
                    "quantidade": int(
                        linha["quantidade"]
                    ),
                }
                for linha in cursor.fetchall()
            ]

    def obter_evolucao_mensal(
        self,
        ano=None,
    ):
        if ano is None:
            ano = datetime.now().year

        with self.conectar() as conexao:
            cursor = conexao.execute(
                """
                SELECT
                    CAST(
                        strftime('%m', data)
                        AS INTEGER
                    ) AS mes,

                    COALESCE(
                        SUM(
                            CASE
                                WHEN tipo = 'Receita'
                                THEN valor
                                ELSE 0
                            END
                        ),
                        0
                    ) AS receitas,

                    COALESCE(
                        SUM(
                            CASE
                                WHEN tipo = 'Despesa'
                                THEN valor
                                ELSE 0
                            END
                        ),
                        0
                    ) AS despesas

                FROM transacoes

                WHERE strftime('%Y', data) = ?

                GROUP BY strftime('%m', data)

                ORDER BY mes
                """,
                (str(ano),),
            )

            encontrados = {
                int(linha["mes"]): {
                    "receitas": float(
                        linha["receitas"]
                    ),
                    "despesas": float(
                        linha["despesas"]
                    ),
                }
                for linha in cursor.fetchall()
            }

        resultado = []

        for mes in range(1, 13):
            valores = encontrados.get(
                mes,
                {
                    "receitas": 0.0,
                    "despesas": 0.0,
                },
            )

            receitas = valores["receitas"]
            despesas = valores["despesas"]

            resultado.append(
                {
                    "mes": mes,
                    "receitas": receitas,
                    "despesas": despesas,
                    "saldo": receitas - despesas,
                }
            )

        return resultado

    def obter_resumo_relatorio(
        self,
        mes=None,
        ano=None,
    ):
        return self.obter_resumo_filtrado(
            pesquisa="",
            tipo="Todos",
            mes=mes,
            ano=ano,
        )


    def obter_status_exibicao(
        self,
        status,
        data_vencimento,
    ):
        if status == "Pago":
            return "Pago"

        try:
            vencimento = datetime.strptime(
                data_vencimento,
                "%Y-%m-%d",
            ).date()
        except (TypeError, ValueError):
            return "Pendente"

        if vencimento < datetime.now().date():
            return "Atrasado"

        return "Pendente"

    def marcar_transacao_como_paga(
        self,
        transacao_id,
        data_pagamento=None,
    ):
        if data_pagamento is None:
            data_pagamento = datetime.now().strftime(
                "%Y-%m-%d"
            )

        with self.conectar() as conexao:
            cursor = conexao.execute(
                """
                UPDATE transacoes
                SET
                    status = 'Pago',
                    data_pagamento = ?
                WHERE id = ?
                  AND tipo = 'Despesa'
                """,
                (
                    data_pagamento,
                    transacao_id,
                ),
            )

            return cursor.rowcount > 0

    def marcar_transacao_como_pendente(
        self,
        transacao_id,
    ):
        with self.conectar() as conexao:
            cursor = conexao.execute(
                """
                UPDATE transacoes
                SET
                    status = 'Pendente',
                    data_pagamento = NULL
                WHERE id = ?
                  AND tipo = 'Despesa'
                """,
                (transacao_id,),
            )

            return cursor.rowcount > 0

    def obter_resumo_status(
        self,
        mes=None,
        ano=None,
    ):
        clausulas = [
            "tipo = 'Despesa'"
        ]
        parametros = []

        if ano is not None:
            clausulas.append(
                "strftime('%Y', data) = ?"
            )
            parametros.append(str(ano))

        if mes is not None:
            clausulas.append(
                "strftime('%m', data) = ?"
            )
            parametros.append(
                f"{int(mes):02d}"
            )

        where_sql = " AND ".join(clausulas)

        with self.conectar() as conexao:
            cursor = conexao.execute(
                f"""
                SELECT
                    COALESCE(
                        SUM(
                            CASE
                                WHEN status = 'Pago'
                                THEN valor
                                ELSE 0
                            END
                        ),
                        0
                    ) AS pagas,

                    COALESCE(
                        SUM(
                            CASE
                                WHEN status != 'Pago'
                                  OR status IS NULL
                                THEN valor
                                ELSE 0
                            END
                        ),
                        0
                    ) AS pendentes

                FROM transacoes

                WHERE {where_sql}
                """,
                parametros,
            )

            linha = cursor.fetchone()

            return {
                "pagas": float(
                    linha["pagas"]
                ),
                "pendentes": float(
                    linha["pendentes"]
                ),
            }

    def obter_configuracao(
        self,
        chave,
        padrao=None,
    ):
        with self.conectar() as conexao:
            cursor = conexao.execute(
                """
                SELECT valor
                FROM configuracoes
                WHERE chave = ?
                """,
                (chave,),
            )

            linha = cursor.fetchone()

            return (
                linha["valor"]
                if linha
                else padrao
            )

    def salvar_configuracao(
        self,
        chave,
        valor,
    ):
        with self.conectar() as conexao:
            conexao.execute(
                """
                INSERT INTO configuracoes (
                    chave,
                    valor
                )
                VALUES (?, ?)
                ON CONFLICT(chave)
                DO UPDATE SET
                    valor = excluded.valor
                """,
                (
                    chave,
                    str(valor),
                ),
            )

    def obter_configuracao_alertas(self):
        ativo_texto = self.obter_configuracao(
            "alertas_ativos",
            "0",
        )

        dias_texto = self.obter_configuracao(
            "alertas_dias_antecedencia",
            "3",
        )

        horario = self.obter_configuracao(
            "alertas_horario",
            "08:00",
        )

        try:
            dias = int(dias_texto)
        except (TypeError, ValueError):
            dias = 3

        return {
            "ativo": ativo_texto == "1",
            "dias_antecedencia": dias,
            "horario": horario,
        }

    def salvar_configuracao_alertas(
        self,
        ativo,
        dias_antecedencia,
        horario="08:00",
    ):
        dias_antecedencia = int(
            dias_antecedencia
        )

        if dias_antecedencia not in (
            1,
            3,
            5,
            7,
        ):
            raise ValueError(
                "Antecedência inválida."
            )

        self.salvar_configuracao(
            "alertas_ativos",
            "1" if ativo else "0",
        )

        self.salvar_configuracao(
            "alertas_dias_antecedencia",
            dias_antecedencia,
        )

        self.salvar_configuracao(
            "alertas_horario",
            horario,
        )

    def obter_contas_para_alerta(
        self,
        dias_antecedencia,
        data_referencia=None,
    ):
        if data_referencia is None:
            data_referencia = datetime.now().date()

        data_alvo = (
            data_referencia
            + timedelta(
                days=int(
                    dias_antecedencia
                )
            )
        ).strftime("%Y-%m-%d")

        with self.conectar() as conexao:
            cursor = conexao.execute(
                """
                SELECT
                    t.id,
                    t.descricao,
                    t.valor,
                    t.data,
                    COALESCE(
                        c.nome,
                        'Sem categoria'
                    ) AS categoria
                FROM transacoes AS t
                LEFT JOIN categorias AS c
                    ON c.id = t.categoria_id
                WHERE t.tipo = 'Despesa'
                  AND COALESCE(
                        t.status,
                        'Pendente'
                      ) != 'Pago'
                  AND t.data = ?
                ORDER BY
                    t.data,
                    t.id
                """,
                (data_alvo,),
            )

            return [
                dict(linha)
                for linha in cursor.fetchall()
            ]

    def alerta_ja_enviado(
        self,
        transacao_id,
        data_alerta,
        dias_antecedencia,
    ):
        with self.conectar() as conexao:
            cursor = conexao.execute(
                """
                SELECT 1
                FROM alertas_enviados
                WHERE transacao_id = ?
                  AND data_alerta = ?
                  AND dias_antecedencia = ?
                """,
                (
                    transacao_id,
                    data_alerta,
                    dias_antecedencia,
                ),
            )

            return cursor.fetchone() is not None

    def registrar_alerta_enviado(
        self,
        transacao_id,
        data_alerta,
        dias_antecedencia,
    ):
        enviado_em = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        with self.conectar() as conexao:
            conexao.execute(
                """
                INSERT OR IGNORE INTO alertas_enviados (
                    transacao_id,
                    data_alerta,
                    dias_antecedencia,
                    enviado_em
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    transacao_id,
                    data_alerta,
                    dias_antecedencia,
                    enviado_em,
                ),
            )

    def obter_configuracoes_app(self):
        return {
            "nome_usuario": self.obter_configuracao(
                "nome_usuario",
                "Douglas",
            ),
            "tema": self.obter_configuracao(
                "tema",
                "Dark",
            ),
            "moeda": self.obter_configuracao(
                "moeda",
                "R$",
            ),
        }

    def salvar_configuracoes_app(
        self,
        nome_usuario,
        tema,
        moeda="R$",
    ):
        nome_usuario = nome_usuario.strip()

        if not nome_usuario:
            raise ValueError(
                "Informe o nome do usuário."
            )

        if tema not in ("Dark", "Light"):
            raise ValueError(
                "Tema inválido."
            )

        self.salvar_configuracao(
            "nome_usuario",
            nome_usuario,
        )

        self.salvar_configuracao(
            "tema",
            tema,
        )

        self.salvar_configuracao(
            "moeda",
            moeda,
        )

db = Database()