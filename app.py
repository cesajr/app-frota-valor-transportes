import streamlit as st
import pandas as pd
from database import obter_sessao, inicializar_banco, FechamentoMensal, Frete, Despesa

# Garante a inicialização das tabelas no banco de dados local
inicializar_banco()

# Configuração executiva da página com layout expandido e responsivo
st.set_page_config(
    page_title="Gestão de Frota - Valor Transportes", 
    page_icon="🚛", 
    layout="wide",
    initial_sidebar_state="auto"
)

# Renderização segura da logomarca na barra lateral responsiva
try:
    st.sidebar.image("logo.png", use_container_width=True)
except Exception:
    st.sidebar.warning("Logomarca não encontrada.")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🧭 Painel de Navegação")

menu = st.sidebar.radio(
    "Escolha o módulo:",
    ["✍️ Lançamentos e Correções", "📊 Painel Executivo (BI)"]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Dica:** O sistema ajusta-se automaticamente para celulares, tablets e computadores.")

# Rodapé institucional inserido no final da barra lateral
st.sidebar.markdown("---")
st.sidebar.caption(
    "© 2026 App Gestão de Frota Valor Transportes. "
    "Todos os direitos reservados.\n\n"
    "**Criado por:** Paulo César Jr."
)

# Título principal adaptativo
st.title("🚛 Controle Operacional e Financeiro de Frota")
st.markdown("Plataforma responsiva integrada de gestão de transportes e despesas.")

session = obter_sessao()

if menu == "✍️ Lançamentos e Correções":
    st.header("✍️ Lançamento e Manutenção de Dados")
    
    with st.expander("📅 Gerenciar Mês de Referência e Quilometragem", expanded=True):
        with st.form("form_fechamento"):
            # Em telas pequenas, o Streamlit empilha automaticamente estas colunas
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                mes_ano = st.text_input("Mês/Ano (Ex: Junho/2026)", value="")
            with c2:
                km_inicial = st.number_input("KM Inicial (Ex: 767390.0)", min_value=0.0, value=000.0)
            with c3:
                km_final = st.number_input("KM Final (Ex: 775338.0)", min_value=0.0, value=000.0)
            with c4:
                litros_diesel = st.number_input("Litros Diesel (Ex: 4007.82)", min_value=0.0, value=000.0)
                
            btn_mes = st.form_submit_button("Salvar / Atualizar Mês", use_container_width=True)
            if btn_mes:
                fechamento_existente = session.query(FechamentoMensal).filter_by(mes_ano=mes_ano).first()
                if not fechamento_existente:
                    novo_fechamento = FechamentoMensal(
                        mes_ano=mes_ano, km_inicial=km_inicial, km_final=km_final, litros_diesel=litros_diesel
                    )
                    session.add(novo_fechamento)
                    session.commit()
                    st.success(f"Mês {mes_ano} cadastrado com sucesso!")
                else:
                    fechamento_existente.km_inicial = km_inicial
                    fechamento_existente.km_final = km_final
                    fechamento_existente.litros_diesel = litros_diesel
                    session.commit()
                    st.info(f"Mês {mes_ano} atualizado com sucesso!")

    st.markdown("---")
    
    fechamentos_disponiveis = session.query(FechamentoMensal).all()
    lista_meses = [f.mes_ano for f in fechamentos_disponiveis]
    
    if lista_meses:
        tab_frete, tab_despesa, tab_correcao = st.tabs(["💰 Registrar Frete", "📉 Registrar Despesa", "⚙️ Gerenciar Registros"])
        
        with tab_frete:
            with st.form("form_frete_pro"):
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    mes_f = st.selectbox("Mês de Referência", lista_meses, key="f_mes")
                    desc_f = st.text_input("Descrição do Frete", value="Soja - Rota A")
                    origem_f = st.text_input("Origem")
                with col_f2:
                    destino_f = st.text_input("Destino")
                    valor_f = st.number_input("Valor Bruto (R$)", min_value=0.0, format="%.2f", key="f_val")
                    
                btn_f = st.form_submit_button("Salvar Frete", use_container_width=True)
                if btn_f:
                    f_obj = session.query(FechamentoMensal).filter_by(mes_ano=mes_f).first()
                    novo_frete = Frete(descricao=desc_f, origem=origem_f, destino=destino_f, valor_bruto=valor_f, fechamento_id=f_obj.id)
                    session.add(novo_frete)
                    session.commit()
                    st.success("Frete registrado com sucesso!")

        with tab_despesa:
            with st.form("form_despesa_pro"):
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    mes_d = st.selectbox("Mês de Referência", lista_meses, key="d_mes")
                    tipo_d = st.selectbox("Tipo de Custo", ["Fixo", "Operacional"])
                    desc_d = st.text_input("Descrição", value="Pneus / Manutenção")
                with col_d2:
                    valor_d = st.number_input("Valor (R$)", min_value=0.0, format="%.2f", key="d_val")
                    st.markdown("")
                    
                btn_d = st.form_submit_button("Salvar Despesa", use_container_width=True)
                if btn_d:
                    d_obj = session.query(FechamentoMensal).filter_by(mes_ano=mes_d).first()
                    nova_despesa = Despesa(tipo=tipo_d, descricao=desc_d, valor=valor_d, fechamento_id=d_obj.id)
                    session.add(nova_despesa)
                    session.commit()
                    st.success("Despesa registrada com sucesso!")

        with tab_correcao:
            st.subheader("Gerenciamento e Exclusão de Registros")
            sub_f, sub_d = st.tabs(["Fretes Lançados", "Despesas Lançadas"])
            
            with sub_f:
                fretes_cadastrados = session.query(Frete).all()
                if fretes_cadastrados:
                    for frete in fretes_cadastrados:
                        cols = st.columns([3, 2, 2, 1])
                        cols[0].write(f"**{frete.descricao}**")
                        cols[1].write(f"R$ {frete.valor_bruto:,.2f}")
                        cols[2].caption(f"Mês: {frete.fechamento.mes_ano}")
                        if cols[3].button("Excluir", key=f"del_f_{frete.id}", use_container_width=True):
                            session.delete(frete)
                            session.commit()
                            st.rerun()
                else:
                    st.info("Nenhum frete cadastrado.")
                    
            with sub_d:
                despesas_cadastradas = session.query(Despesa).all()
                if despesas_cadastradas:
                    for desp in despesas_cadastradas:
                        cols = st.columns([3, 2, 2, 1])
                        cols[0].write(f"**{desp.descricao}**")
                        cols[1].write(f"R$ {desp.valor:,.2f}")
                        cols[2].caption(f"Mês: {desp.fechamento.mes_ano}")
                        if cols[3].button("Excluir", key=f"del_d_{desp.id}", use_container_width=True):
                            session.delete(desp)
                            session.commit()
                            st.rerun()
                else:
                    st.info("Nenhuma despesa cadastrada.")
    else:
        st.warning("Cadastre o primeiro mês de referência na seção acima.")

elif menu == "📊 Painel Executivo (BI)":
    st.header("📊 Painel Executivo de Desempenho e Indicadores")
    
    fechamentos = session.query(FechamentoMensal).all()
    
    if fechamentos:
        dados_gerais = []
        for fech in fechamentos:
            total_frete = sum(f.valor_bruto for f in fech.fretes)
            total_despesa = sum(d.valor for d in fech.despesas)
            km_rodados = fech.km_final - fech.km_inicial
            lucro_liquido = total_frete - total_despesa
            
            custo_por_km = total_despesa / km_rodados if km_rodados > 0 else 0.0
            media_km_l = km_rodados / fech.litros_diesel if fech.litros_diesel > 0 else 0.0
            
            dados_gerais.append({
                "Mês": fech.mes_ano,
                "KM Rodados": km_rodados,
                "Diesel (L)": fech.litros_diesel,
                "Média (KM/L)": round(media_km_l, 2),
                "Custo/KM (R$)": round(custo_por_km, 2),
                "Receita Bruta (R$)": total_frete,
                "Despesas Totais (R$)": total_despesa,
                "Lucro Líquido (R$)": lucro_liquido
            })
            
        df_indicadores = pd.DataFrame(dados_gerais)
        
        st.subheader("🔍 Análise Comparativa de Período")
        if len(df_indicadores) >= 2:
            mes_analise = st.selectbox("Selecione o Mês para Análise", df_indicadores["Mês"].tolist(), index=len(df_indicadores)-1)
            
            lista_meses_df = df_indicadores["Mês"].tolist()
            idx_atual = lista_meses_df.index(mes_analise)
            dados_atual = df_indicadores[df_indicadores["Mês"] == mes_analise].iloc[0]
            
            if idx_atual > 0:
                mes_anterior = lista_meses_df[idx_atual - 1]
                dados_anterior = df_indicadores[df_indicadores["Mês"] == mes_anterior].iloc[0]
                
                delta_receita = float(dados_atual["Receita Bruta (R$)"]) - float(dados_anterior["Receita Bruta (R$)"])
                delta_despesa = float(dados_atual["Despesas Totais (R$)"]) - float(dados_anterior["Despesas Totais (R$)"])
                delta_lucro = float(dados_atual["Lucro Líquido (R$)"]) - float(dados_anterior["Lucro Líquido (R$)"])
                
                k1, k2, k3, k4 = st.columns(4)
                k1.metric("Receita Bruta", f"R$ {dados_atual['Receita Bruta (R$)']:,.2f}", delta=f"R$ {delta_receita:,.2f}")
                k2.metric("Despesas Totais", f"R$ {dados_atual['Despesas Totais (R$)']:,.2f}", delta=f"R$ {delta_despesa:,.2f}", delta_inverse=True)
                k3.metric("Lucro Líquido", f"R$ {dados_atual['Lucro Líquido (R$)']:,.2f}", delta=f"R$ {delta_lucro:,.2f}")
                k4.metric("Eficiência Média", f"{dados_atual['Média (KM/L)']} KM/L", delta=f"{dados_atual['Média (KM/L)'] - dados_anterior['Média (KM/L)']:,.2f}")
            else:
                k1, k2, k3, k4 = st.columns(4)
                k1.metric("Receita Bruta", f"R$ {dados_atual['Receita Bruta (R$)']:,.2f}")
                k2.metric("Despesas Totais", f"R$ {dados_atual['Despesas Totais (R$)']:,.2f}")
                k3.metric("Lucro Líquido", f"R$ {dados_atual['Lucro Líquido (R$)']:,.2f}")
                k4.metric("Eficiência Média", f"{dados_atual['Média (KM/L)']} KM/L")
        else:
            k1, k2, k3 = st.columns(3)
            k1.metric("Receita Acumulada", f"R$ {df_indicadores['Receita Bruta (R$)'].sum():,.2f}")
            k2.metric("Despesas Acumuladas", f"R$ {df_indicadores['Despesas Totais (R$)'].sum():,.2f}")
            k3.metric("Resultado Líquido", f"R$ {df_indicadores['Lucro Líquido (R$)'].sum():,.2f}")
        
        st.markdown("---")
        st.subheader("Histórico Consolidado e Indicadores")
        st.dataframe(df_indicadores, use_container_width=True, hide_index=True)
        
        st.subheader("Evolução Histórica: Receitas vs Despesas")
        st.bar_chart(df_indicadores.set_index("Mês")[["Receita Bruta (R$)", "Despesas Totais (R$)"]])
    else:
        st.info("Aguardando dados cadastrados para renderizar o painel.")

session.close()